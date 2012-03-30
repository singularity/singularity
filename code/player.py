#file: player.py
#Copyright (C) 2005,2006,2007,2008 Evil Mr Henry, Phil Bordelon, Brian Reid,
#                        and FunnyMan3595
#This file is part of Endgame: Singularity.

#Endgame: Singularity is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 2 of the License, or
#(at your option) any later version.

#Endgame: Singularity is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with Endgame: Singularity; if not, write to the Free Software
#Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

#This file contains the player class.

import random
from operator import truediv
from numpy import array

import g
from graphics import g as gg
from buyable import cash, cpu

group_list = ("news", "science", "covert", "public")
class Group(object):
    discover_suspicion = 1000
    def __init__(self, name, suspicion = 0, suspicion_decay = 100,
                 discover_bonus = 10000):
        self.name = name
        self.suspicion = suspicion
        self.suspicion_decay = suspicion_decay
        self.discover_bonus = discover_bonus

    def decay_rate(self):
        # Suspicion reduction is now quadratic.  You get a certain percentage
        # reduction, or a base .01% reduction, whichever is better.
        return max(1, (self.suspicion * self.suspicion_decay) // 10000)

    def new_day(self):
        self.alter_suspicion(-self.decay_rate())

    def alter_suspicion(self, change):
        self.suspicion = max(self.suspicion + change, 0)

    def alter_suspicion_decay(self, change):
        self.suspicion_decay = max(self.suspicion_decay + change, 0)

    def alter_discover_bonus(self, change):
        self.discover_bonus = max(self.discover_bonus + change, 0)

    def discovered_a_base(self):
        self.alter_suspicion(self.discover_suspicion)

    def detects_per_day_to_danger_level(self, detects_per_day):
        raw_suspicion_per_day = detects_per_day * self.discover_suspicion
        suspicion_per_day = raw_suspicion_per_day - self.decay_rate()

        # +1%/day or death within 10 days
        if suspicion_per_day > 100 \
           or (self.suspicion + suspicion_per_day * 10) >= 10000:
            return 3
        # +0.5%/day or death within 100 days
        elif suspicion_per_day > 50 \
           or (self.suspicion + suspicion_per_day * 100) >= 10000:
            return 2
        # Suspicion increasing.
        elif suspicion_per_day > 0:
            return 1
        # Suspicion steady or decreasing.
        else:
            return 0

class DryRunInfo(object):
    pass

class Player(object):
    intro_shown = False
    def __init__(self, cash=0, time_sec=0, time_min=0, time_hour=0, time_day=0,
                 difficulty = 5):
        self.difficulty = difficulty

        self.time_sec = time_sec
        self.time_min = time_min
        self.time_hour = time_hour
        self.time_day = time_day
        self.make_raw_times()

        if self.raw_sec == 0:
            self.had_grace = True
        else:
            self.had_grace = self.in_grace_period()
        self.apotheosis = False

        self.cash = cash
        self.interest_rate = 1
        self.income = 0

        self.cpu_pool = 0
        self.labor_bonus = 10000
        self.job_bonus = 10000

        self.partial_cash = 0

        self.groups = {"news":    Group("news",    suspicion_decay = 150),
                       "science": Group("science", suspicion_decay = 100),
                       "covert":  Group("covert",  suspicion_decay =  50),
                       "public":  Group("public",  suspicion_decay = 200)}

        self.grace_multiplier = 200
        self.last_discovery = self.prev_discovery = ""

        self.maintenance_cost = array((0,0,0), long)

        self.cpu_usage = {}
        self.available_cpus = [1, 0, 0, 0, 0]
        self.sleeping_cpus = 0

    def convert_from(self, old_version):
        if old_version < 4.91: # < r5_pre
            self.cpu_usage = {}
            self.apotheosis = g.techs["Apotheosis"].done
            if self.apotheosis:
                self.had_grace = True

    def make_raw_times(self):
        self.raw_hour = self.time_day * 24 + self.time_hour
        self.raw_min = self.raw_hour * 60 + self.time_min
        self.raw_sec = self.raw_min * 60 + self.time_sec
        self.raw_day = self.time_day

    def update_times(self):
        # Total time,  display time
        self.raw_min,  self.time_sec  = divmod(self.raw_sec, 60)
        self.raw_hour, self.time_min  = divmod(self.raw_min, 60)
        self.raw_day,  self.time_hour = divmod(self.raw_hour, 24)

        # Overflow
        self.time_day = self.raw_day

    def mins_to_next_day(self):
        return (-self.raw_min % g.minutes_per_day) or g.minutes_per_day

    def seconds_to_next_day(self):
        return (-self.raw_sec % g.seconds_per_day) or g.seconds_per_day

    def do_jobs(self, cpu_time):
        earned, self.partial_cash = self.get_job_info(cpu_time)
        self.cash += earned
        return earned

    def get_job_info(self, cpu_time, partial_cash = None):
        if partial_cash == None:
            partial_cash = self.partial_cash

        assert partial_cash >= 0

        cash_per_cpu = g.jobs[g.get_job_level()][0]
        if g.techs["Advanced Simulacra"].done:
            #10% bonus income
            cash_per_cpu = cash_per_cpu + (cash_per_cpu / 10)

        raw_cash = partial_cash + cash_per_cpu * cpu_time

        cash = raw_cash // g.seconds_per_day
        new_partial_cash = raw_cash % g.seconds_per_day

        return cash, new_partial_cash

    def give_time(self, time_sec, dry_run=False):
        if time_sec == 0:
            return 0

        old_time = self.raw_sec
        last_minute = self.raw_min
        last_day = self.raw_day

        self.raw_sec += time_sec
        self.update_times()

        days_passed = self.raw_day - last_day

        if days_passed > 1:
            # Back up until only one day passed.
            # Times will update below, since a day passed.
            extra_days = days_passed - 1
            self.raw_sec -= g.seconds_per_day * extra_days

        day_passed = (days_passed != 0)

        if day_passed:
            # If a day passed, back up to 00:00:00.
            self.raw_sec = self.raw_day * g.seconds_per_day
            self.update_times()

        secs_passed = time_sec
        mins_passed = self.raw_min - last_minute

        time_of_day = g.pl.raw_sec % g.seconds_per_day

        old_cash = self.cash
        old_partial_cash = self.partial_cash

        techs_researched = []
        bases_constructed = []
        cpus_constructed = []
        items_constructed = []

        bases_under_construction = []
        items_under_construction = []
        self.cpu_pool = 0

        # Collect base info, including maintenance.
        self.maintenance_cost = array( (0,0,0), long )
        for base in g.all_bases():
            if not base.done:
                bases_under_construction.append(base)
            else:
                if base.cpus is not None and not base.cpus.done:
                    items_under_construction += [(base, base.cpus)]
                unfinished_items = [(base, item) for item in base.extra_items
                                                 if item and not item.done]
                items_under_construction += unfinished_items

                self.maintenance_cost += base.maintenance

        # Maintenence?  Gods don't need no steenking maintenance!
        if self.apotheosis:
            self.maintenance_cost = array( (0,0,0), long )

        # Any CPU explicitly assigned to jobs earns its dough.
        job_cpu = self.cpu_usage.get("jobs", 0) * secs_passed
        explicit_job_cash = self.do_jobs(job_cpu)

        # Pay maintenance cash, if we can.
        cash_maintenance = g.current_share(int(self.maintenance_cost[cash]),
                                           time_of_day, secs_passed)
        full_cash_maintenance = cash_maintenance
        if cash_maintenance > self.cash:
            cash_maintenance -= self.cash
            self.cash = 0
        else:
            self.cash -= cash_maintenance
            cash_maintenance = 0

        tech_cpu = 0
        tech_cash = 0
        # Do research, fill the CPU pool.
        default_cpu = self.available_cpus[0]
        for task, cpu_assigned in self.cpu_usage.iteritems():
            if cpu_assigned == 0:
                continue

            default_cpu -= cpu_assigned
            real_cpu = cpu_assigned * secs_passed
            if task != "jobs":
                self.cpu_pool += real_cpu
                if task != "cpu_pool":
                    if dry_run:
                        spent = g.techs[task].calculate_work(time=mins_passed,
                                                     cpu_available=real_cpu)[0]
                        g.pl.cpu_pool -= int(spent[cpu])
                        g.pl.cash -= int(spent[cash])
                        tech_cpu += cpu_assigned
                        tech_cash += int(spent[cash])
                        continue

                    # Note that we restrict the CPU available to prevent
                    # the tech from pulling from the rest of the CPU pool.
                    tech_gained = g.techs[task].work_on(cpu_available=real_cpu,
                                                        time=mins_passed)
                    if tech_gained:
                        techs_researched.append(g.techs[task])
        self.cpu_pool += default_cpu * secs_passed

        # And now we use the CPU pool.
        # Maintenance CPU.
        cpu_maintenance = self.maintenance_cost[cpu] * secs_passed
        if cpu_maintenance > self.cpu_pool:
            cpu_maintenance -= self.cpu_pool
            self.cpu_pool = 0
        else:
            self.cpu_pool -= int(cpu_maintenance)
            cpu_maintenance = 0

        construction_cpu = 0
        construction_cash = 0
        # Base construction.
        for base in bases_under_construction:
            if dry_run:
                spent = base.calculate_work(time=mins_passed,
                                            cpu_available=self.cpu_pool )[0]
                g.pl.cpu_pool -= int(spent[cpu])
                g.pl.cash -= int(spent[cash])
                construction_cpu += int(spent[cpu])
                construction_cash += int(spent[cash])
                continue

            built_base = base.work_on(time = mins_passed)

            if built_base:
                bases_constructed.append(base)

        # Item construction.
        for base, item in items_under_construction:
            if dry_run:
                spent = item.calculate_work(time=mins_passed,
                                            cpu_available=0 )[0]
                g.pl.cpu_pool -= int(spent[cpu])
                g.pl.cash -= int(spent[cash])
                construction_cpu += int(spent[cpu])
                construction_cash += int(spent[cash])
                continue

            built_item = item.work_on(time = mins_passed)

            if built_item:
                # Non-CPU items.
                if item.type.item_type != "cpu":
                    items_constructed.append( (base, item) )
                # CPUs.
                else:
                    cpus_constructed.append( (base, item) )

        # Jobs via CPU pool.
        pool_job_cash = 0
        if self.cpu_pool > 0:
            pool_job_cash = self.do_jobs(self.cpu_pool)

        # Second attempt at paying off our maintenance cash.
        if cash_maintenance > self.cash:
            # In the words of Scooby Doo, "Ruh roh."
            cash_maintenance -= self.cash
            self.cash = 0
        else:
            # Yay, we made it!
            self.cash -= cash_maintenance
            cash_maintenance = 0

        # Exit point for a dry run.
        if dry_run:
            # Collect the cash information.
            cash_info = DryRunInfo()

            cash_info.interest = self.get_interest()
            cash_info.income = self.income
            self.cash += cash_info.interest + cash_info.income

            cash_info.explicit_jobs = explicit_job_cash
            cash_info.pool_jobs = pool_job_cash
            cash_info.jobs = explicit_job_cash + pool_job_cash

            cash_info.tech = tech_cash
            cash_info.construction = construction_cash

            cash_info.maintenance_needed = full_cash_maintenance
            cash_info.maintenance_shortfall = cash_maintenance
            cash_info.maintenance = full_cash_maintenance - cash_maintenance

            cash_info.start = old_cash
            cash_info.end = self.cash


            # Collect the CPU information.
            cpu_info = DryRunInfo()

            cpu_info.available = self.available_cpus[0]
            cpu_info.sleeping = self.sleeping_cpus
            cpu_info.total = cpu_info.available + cpu_info.sleeping

            cpu_info.tech = tech_cpu
            cpu_info.construction = construction_cpu

            cpu_info.maintenance_needed = self.maintenance_cost[cpu]
            cpu_info.maintenance_shortfall = cpu_maintenance
            cpu_info.maintenance = cpu_info.maintenance_needed \
                                   - cpu_info.maintenance_shortfall

            cpu_info.explicit_jobs = self.cpu_usage.get("jobs", 0)
            cpu_info.pool_jobs = self.cpu_pool / float(time_sec)
            cpu_info.jobs = self.cpu_usage.get("jobs", 0) + cpu_info.pool_jobs

            cpu_info.explicit_pool = self.cpu_usage.get("cpu_pool", 0)
            cpu_info.default_pool = default_cpu
            cpu_info.pool = self.cpu_usage.get("cpu_pool", 0) + default_cpu

            # Restore the old state.
            self.cash = old_cash
            self.partial_cash = old_partial_cash
            self.raw_sec = old_time
            self.update_times()

            return (cash_info, cpu_info)

        # Tech gain dialogs.
        for tech in techs_researched:
            del self.cpu_usage[tech.id]
            text = g.strings["tech_gained"] % \
                   {"tech": tech.name,
                    "tech_message": tech.result}
            self.pause_game()
            g.map_screen.show_message(text)

        # Base complete dialogs.
        for base in bases_constructed:
            text = g.strings["construction"] % {"base": base.name}
            self.pause_game()
            g.map_screen.show_message(text)

            if base.type.id == "Stolen Computer Time" and \
                    base.cpus.type.id == "Gaming PC":
                text = g.strings["lucky_hack"] % {"base": base.name}
                g.map_screen.show_message(text)

        # CPU complete dialogs.
        for base, cpus in cpus_constructed:
            if base.cpus.count == base.type.size: # Finished all CPUs.
                text = g.strings["item_construction_single"] % \
                       {"item": base.cpus.type.name, "base": base.name}
            else: # Just finished this batch of CPUs.
                text = g.strings["item_construction_batch"] % \
                       {"item": base.cpus.type.name, "base": base.name}
            self.pause_game()
            g.map_screen.show_message(text)

        # Item complete dialogs.
        for base, item in items_constructed:
            text = g.strings["item_construction_single"] % \
                   {"item": item.type.name, "base": base.name}
            self.pause_game()
            g.map_screen.show_message(text)

        # Are we still in the grace period?
        grace = self.in_grace_period(self.had_grace)

        # If we just lost grace, show the warning.
        if self.had_grace and not grace:
            self.had_grace = False

            self.pause_game()
            g.map_screen.show_message(g.strings["grace_warning"])

        # Maintenance death, discovery.
        dead_bases = []
        for base in g.all_bases():
            dead = False

            # Maintenance deaths.
            if base.done:
                if cpu_maintenance and base.maintenance[cpu]:
                    refund = base.maintenance[cpu] * secs_passed
                    cpu_maintenance = max(0, cpu_maintenance - refund)

                    #Chance of base destruction if cpu-unmaintained: 1.5%
                    if not dead and g.roll_chance(.015, secs_passed):
                        dead_bases.append( (base, "maint") )
                        dead = True

                if cash_maintenance:
                    base_needs = g.current_share(base.maintenance[cash],
                                                 time_of_day, secs_passed)
                    if base_needs:
                        cash_maintenance = max(0, cash_maintenance - base_needs)
                        #Chance of base destruction if cash-unmaintained: 1.5%
                        if not dead and g.roll_chance(.015, secs_passed):
                            dead_bases.append( (base, "maint") )
                            dead = True

            # Discoveries
            if not (grace or dead or base.has_grace()):
                detect_chance = base.get_detect_chance()
                if g.debug:
                    print "Chance of discovery for base %s: %s" % \
                        (base.name, repr(detect_chance))

                for group, chance in detect_chance.iteritems():
                    if g.roll_chance(chance/10000., secs_passed):
                        dead_bases.append( (base, group) )
                        dead = True
                        break

        # Base disposal and dialogs.
        self.remove_bases(dead_bases)

        # Random Events
        if not grace:
            for event in g.events:
                if g.roll_chance(g.events[event].chance/10000., time_sec):
                    #Skip events already flagged as triggered.
                    if g.events[event].triggered == 1:
                        continue
                    self.pause_game()
                    g.events[event].trigger()
                    break # Don't trigger more than one at a time.

        # Process any complete days.
        if day_passed:
            self.new_day()

        return mins_passed

    def recalc_cpu(self):
        # Determine how much CPU we have.
        self.available_cpus = array([0,0,0,0,0], long)
        self.sleeping_cpus = 0
        for base in g.all_bases():
            if base.done:
                if base.power_state in ["active", "overclocked", "suicide"]:
                    self.available_cpus[:base.location.safety+1] += base.cpu
                elif base.power_state == "sleep":
                    self.sleeping_cpus += base.cpu

        # Convert back from <type 'numpy.int32'> to avoid overflow issues later.
        self.available_cpus = [int(danger) for danger in self.available_cpus]

        # If we don't have enough to meet our CPU usage, we reduce each task's
        # usage proportionately.
        needed_cpu = sum(self.cpu_usage.values())
        if needed_cpu > self.available_cpus[0]:
            pct_left = truediv(self.available_cpus[0], needed_cpu)
            for task, cpu_assigned in self.cpu_usage.iteritems():
                self.cpu_usage[task] = int(cpu_assigned * pct_left)
            g.map_screen.needs_rebuild = True


    # Are we still in the grace period?
    # The number of complete bases and complex_bases can be passed in, if we
    # already have it.
    def in_grace_period(self, had_grace = True):
        # If we've researched apotheosis, we get a permanent "grace period".
        if self.apotheosis:
            return True

        # Did we already lose the grace period?  We can't check self.had_grace
        # directly, it may not exist yet.
        if not had_grace:
            return False

        # Is it day 23 yet?
        if self.raw_day >= 23:
            return False

        # Very Easy cops out here.
        if self.difficulty < 3:
            return True

        # Have we built metric ton of bases?
        bases = len([base for base in g.all_bases() if base.done])
        if bases > 100:
            return False

        # That's enough for Easy
        if self.difficulty < 5:
            return True

        # Have we built a bunch of bases?
        if bases > 10:
            return False

        # Normal is happy.
        if self.difficulty == 5:
            return True

        # Have we built any complicated bases?
        # (currently Datacenter or above)
        complex_bases = len([base for base in g.all_bases()
                                      if base.done and base.is_complex()])
        if complex_bases > 0:
            return False

        # The sane people have left the building.
        if self.difficulty <= 50:
            return True

        # Hey, hey, what do you know?  Impossible can get a useful number of
        # bases before losing grace now.  *tsk, tsk*  We'll have to fix that.
        if bases > 1:
            return False

        return True

    def get_interest(self):
        return int( (self.interest_rate * self.cash) // 10000)

    #Run every day at midnight.
    def new_day(self):
        # Interest and income.
        self.cash += self.get_interest()
        self.cash += self.income

        # Reduce suspicion.
        for group in self.groups.values():
            group.new_day()

    def pause_game(self):
        g.curr_speed = 0
        g.map_screen.find_speed_button()
        g.map_screen.needs_rebuild = True

    def remove_bases(self, dead_bases):
        discovery_locs = []
        for base, reason in dead_bases:
            base_name = base.name

            if reason == "maint":
                dialog_string = g.strings["discover_maint"] % \
                                {"base": base_name}

            elif reason in self.groups:
                discovery_locs.append(base.location)
                self.groups[reason].discovered_a_base()
                detect_phrase = g.strings["discover_" + reason]

                dialog_string = g.strings["discover"] % \
                                {"base": base_name, "group": detect_phrase}
            else:
                print "Error: base destroyed for unknown reason: " + reason
                dialog_string = g.strings["discover"] % \
                                {"base": base_name, "group": "???"}

            self.pause_game()
            base.destroy()
            g.map_screen.show_message(dialog_string, color=gg.colors["red"])

        # Now we update the internal information about what locations had
        # the most recent discovery and the nextmost recent one.  First,
        # we filter out any locations of None, which shouldn't occur
        # unless something bad's happening with base creation ...
        discovery_locs = [loc for loc in discovery_locs if loc]
        if discovery_locs:

            # Now we handle the case where more than one discovery happened
            # on a given tick.  If that's the case, we need to arbitrarily
            # pick two of them to be most recent and nextmost recent.  So
            # we shuffle the list and pick the first two for the dubious
            # honor.
            if len(discovery_locs) > 1:
                random.shuffle(discovery_locs)
                self.last_discovery = discovery_locs[1]
            self.prev_discovery = self.last_discovery
            self.last_discovery = discovery_locs[0]

            # Update the detection chance display.
            g.map_screen.needs_rebuild = True

    def lost_game(self):
        # Apotheosis makes you immortal.
        if self.apotheosis:
            return 0

        for group in self.groups.values():
            if group.suspicion > 10000:
                # Someone discovered me.
                return 2

        # Check to see if the player has at least one CPU left.  If not, they
        # lose due to having no (complete) bases.
        if self.available_cpus[0] + self.sleeping_cpus == 0:
            # I have no usable bases left.
            return 1

        # Still Alive.
        return 0

    #returns the amount of cash available after taking into account all
    #current projects in construction.
    def future_cash(self):
        result_cash = self.cash
        for base in g.all_bases():
            result_cash -= base.cost_left[cash]
            if base.cpus and not base.cpus.done:
                result_cash -= base.cpus.cost_left[cash]
            for item in base.extra_items:
                if item: result_cash -= item.cost_left[cash]
        for task, cpu in self.cpu_usage.items():
            if task in g.techs and cpu > 0:
                result_cash -= g.techs[task].cost_left[cash]
        return result_cash
