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

import g
import buyable
from buyable import cash, cpu, labor

class Group(object):
    discover_suspicion = 1000
    def __init__(self, name, suspicion = 0, suspicion_decay = 100, 
                 discover_bonus = 10000):
        self.name = name
        self.suspicion = suspicion
        self.suspicion_decay = suspicion_decay
        self.discover_bonus = discover_bonus

    def new_day(self):
        # Suspicion reduction is now quadratic.  You get a certain percentage
        # reduction, or a base .01% reduction, whichever is better.
        quadratic_down = (self.suspicion * self.suspicion_decay) / 10000
        self.alter_suspicion(-max(quadratic_down, 1))

    def alter_suspicion(self, change):
        self.suspicion = max(self.suspicion + change, 0)

    def alter_suspicion_decay(self, change):
        self.suspicion_decay = max(self.suspicion_decay + change, 0)

    def alter_discover_bonus(self, change):
        self.discover_bonus = max(self.discover_bonus + change, 0)

    def discovered_a_base(self):
        self.alter_suspicion(self.discover_suspicion)

class Player(object):
    def __init__(self, cash, time_sec=0, time_min=0, time_hour=0, time_day=0,
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

        self.maintenance_cost = buyable.array((0,0,0))

        self.have_cpu = True
        self.complete_bases = 1
        self.complex_bases = 0

        self.cpu_usage = {}
        self.available_cpus = [100, 10, 1, 0, 0]

    def convert_from(self, old_version):
         if old_version <= 3.94: # <= r4_pre4
             # We don't know what the difficulty was, and techs have fooled with
             # any values that would help (not to mention the headache of 
             # different versions.  So we set it to Very Easy, which means that
             # they shouldn't be hurt by any new mechanics.
             self.difficulty = 1
         if old_version <= 3.93: # <= r4_pre3
             self.grace_multiplier = int(1000000./float(self.labor_bonus))
         if old_version <= 3.91: # <= r4_pre
             self.make_raw_times()
             self.had_grace = self.in_grace_period()

    def make_raw_times(self):
        self.raw_hour = self.time_day * 24 + self.time_hour
        self.raw_min = self.raw_hour * 60 + self.time_min
        self.raw_sec = self.raw_min * 60 + self.time_sec
        self.raw_day = self.time_day

    def update_times(self):
        # Total minutes/hours/days spent.
        self.raw_min = self.raw_sec // 60
        self.raw_hour = self.raw_min // 60
        self.raw_day = self.raw_hour // 24

        # Remainders.
        self.time_sec = self.raw_sec % 60
        self.time_min = self.raw_min % 60
        self.time_hour = self.raw_hour % 24

        # Overflow
        self.time_day = self.raw_day

    def mins_to_next_day(self):
        return (-self.raw_min % g.minutes_per_day) or g.minutes_per_day

    def seconds_to_next_day(self):
        return (-self.raw_sec % g.seconds_per_day) or g.seconds_per_day

    def do_jobs(self, cpu_time):
        earned, self.partial_cash = self.get_job_info(cpu_time)
        self.cash += earned

    def get_job_info(self, cpu_time, partial_cash = None):
        if partial_cash == None:
            partial_cash = self.partial_cash

        cash_per_cpu = g.jobs[g.get_job_level()][0]
        if g.techs["Advanced Simulacra"].done:
            #10% bonus income
            cash_per_cpu = cash_per_cpu + (cash_per_cpu / 10)

        raw_cash = partial_cash + cash_per_cpu * cpu_time

        cash = raw_cash // g.seconds_per_day
        new_partial_cash = raw_cash % g.seconds_per_day

        return cash, new_partial_cash

    def give_time(self, time_sec):
        if time_sec == 0:
            return

        needs_refresh = False

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

        techs_researched = []
        bases_constructed = []
        cpus_constructed = {}
        items_constructed = []

        bases_under_construction = []
        items_under_construction = []
        self.cpu_pool = 0
        self.have_cpu = False
        self.complete_bases = 0
        self.complex_bases = 0

        # Re-calculate the maintenance.
        self.maintenance_cost = buyable.array( (0,0,0) )

        # Phase 1: Collect CPU and construction info.
        #          Spend CPU, then Cash/Labor.
        for base in g.all_bases():
            if not base.done:
                bases_under_construction.append(base)
            else:
                self.complete_bases += 1
                if base.is_complex():
                    self.complex_bases += 1

                unfinished_cpus = [(base, item) for item in base.cpus 
                                                if item and not item.done]
                unfinished_items = [(base, item) for item in base.extra_items 
                                                 if item and not item.done]
                items_under_construction += unfinished_cpus + unfinished_items

                self.maintenance_cost += base.maintenance

                if base.power_state != "Stasis":
                    cpu_power = base.processor_time() * secs_passed
                    self.have_cpu = self.have_cpu or cpu_power
                    if base.power_state != "Active":
                        continue

                    if base.studying in g.jobs:
                        self.do_jobs(cpu_power)
                        continue

                    # Everything else goes into the CPU pool.  Research goes 
                    # through it for simplicity and to allow spill-over.
                    self.cpu_pool += cpu_power

                    if base.studying in g.techs:
                        tech = g.techs[base.studying]
                        # Note that we restrict the CPU available to prevent
                        # the tech from pulling from the rest of the CPU pool.
                        tech_gained = tech.work_on(cash_available=0, 
                                                   cpu_available=cpu_power)
                        if tech_gained:
                            techs_researched.append(tech)

                    # Explicit and implicit assignment to the CPU pool was
                    # already handled.

        # Maintenance CPU.
        if self.maintenance_cost[cpu] > self.cpu_pool:
            self.maintenance_cost[cpu] -= self.cpu_pool
            self.cpu_pool = 0
        else:
            self.cpu_pool -= self.maintenance_cost[cpu]
            self.maintenance_cost[cpu] = 0

        # Construction CPU.
        # Bases.
        for base in bases_under_construction:
            built_base = base.work_on(cash_available = 0)

            if built_base:
                bases_constructed.append(base)

        # Items.
        for base, item in items_under_construction:
            built_item = item.work_on(cash_available = 0)

            if built_item:
                # Non-CPU items.
                if item.item_type != "compute":
                    items_constructed.append( (base, item) )
                # CPUs.
                else:
                    cpus_constructed.setdefault(base, 0)
                    cpus_constructed[base] += 1

        # Jobs.
        if self.cpu_pool > 0:
            self.do_jobs(self.cpu_pool)
            self.cpu_pool = 0

        # And now we get to spend cash and labor.
        # Research.
        for tech in g.techs.values():
            tech_gained = tech.work_on(time = mins_passed)
            if tech_gained:
                techs_researched.append(tech)

        # Maintenance.
        cash_maintenance = g.current_share(self.maintenance_cost[cash],
                                           time_of_day, secs_passed)
        if cash_maintenance > self.cash:
            cash_maintenance -= self.cash
            self.cash = 0
        else:
            self.cash -= cash_maintenance
            cash_maintenance = 0

        # Construction.
        # Bases.
        for base in bases_under_construction:
            built_base = base.work_on(time = mins_passed)

            if built_base:
                bases_constructed.append(base)

        # Items.
        for base, item in items_under_construction:
            built_item = item.work_on(time = mins_passed)

            if built_item:
                # Non-CPU items.
                if item.type.item_type != "compute":
                    items_constructed.append( (base, item) )
                # CPUs.
                else:
                    cpus_constructed.setdefault(base, 0)
                    cpus_constructed[base] += 1

        # Are we still in the grace period?
        grace = self.in_grace_period(self.had_grace, self.complete_bases, 
                                     self.complex_bases)

        # Phase 2: Dialogs, maintenance, and discovery.
        # Tech gain dialogs.
        for tech in techs_researched:
            text = g.strings["tech_gained"] % \
                   {"tech": tech.name, 
                    "tech_message": tech.result}
            g.map_screen.show_message(text)
            g.curr_speed = 0
            needs_refresh = 1

        # Base complete dialogs.
        for base in bases_constructed:
            text = g.strings["construction"] % {"base": base.name}
            g.curr_speed = 0
            needs_refresh = 1
            g.map_screen.show_message(text)

            if base.type.id == "Stolen Computer Time" and \
                    base.cpus[0].type.id == "Gaming PC":
                text = g.strings["lucky_hack"] % {"base": base.name}
                g.map_screen.show_message(text)

        # CPU complete dialogs.
        for base, new_cpus in cpus_constructed.iteritems():
            if new_cpus == len(base.cpus):
                finished_cpus = new_cpus
            else:
                finished_cpus = len([item for item in base.cpus 
                                          if item and item.done  ])

            if finished_cpus == len(base.cpus): # Finished all the CPUs.
                text = g.strings["item_construction_single"] % \
                       {"item": base.cpus[0].type.name, "base": base.name}
                g.map_screen.show_message(text)
                g.curr_speed = 0
                needs_refresh = 1
            elif finished_cpus == new_cpus: # Finished the first batch of CPUs.
                text = g.strings["item_construction_batch"] % \
                       {"item": base.cpus[0].type.name, "base": base.name}
                g.map_screen.show_message(text)
                g.curr_speed = 0
                needs_refresh = 1
            else:
                pass # No message unless we just finished the first or last CPU.
            
        # Item complete dialogs.
        for base, item in items_constructed:
            text = g.strings["item_construction_single"] % \
                   {"item": item.type.name, "base": base.name}
            g.map_screen.show_message(text)
            g.curr_speed = 0
            needs_refresh = 1

        # If we just lost grace, show the warning.
        if self.had_grace and not grace:
            self.had_grace = False

            g.map_screen.show_message(g.strings["grace_warning"])
            needs_refresh = 1
            g.curr_speed = 0

        # Maintenance death, discovery, clear finished techs.
        dead_bases = []
        for base in g.all_bases():
            dead = False

            # Maintenance deaths.
            if base.done:
                if self.maintenance_cost[cpu] and base.maintenance[cpu]:
                    self.maintenance_cost[cpu] = \
                        max(0, self.maintenance_cost[cpu] 
                                   - base.maintenance[cpu])
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

            # Clear finished techs
            if base.studying in g.techs and g.techs[base.studying].done:
                base.studying = ""

        if self.remove_bases(dead_bases):
            needs_refresh = 1

        # Random Events
        for event in g.events:
            if g.roll_chance(g.events[event].chance/10000., time_sec):
                #Skip events already flagged as triggered.
                if g.events[event].triggered == 1:
                    continue
                g.events[event].trigger()
                needs_refresh = 1
                break # Don't trigger more than one at a time.

        # And now process any complete days.
        if day_passed:
            self.new_day()

        return needs_refresh

    # Are we still in the grace period?
    # The number of complete bases and complex_bases can be passed in, if we
    # already have it.
    def in_grace_period(self, had_grace = True, bases = None, 
                        complex_bases = None):
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
        if bases == None:
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
        if complex_bases == None:
            complex_bases = len([base for base in g.all_bases()
                                      if base.done
                                      if len(base.cpus) > 1
                                         or base.processor_time() > 20
                                 ])
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

    #Run every day at midnight.
    def new_day(self):
        #interest and income.
        self.cash += (self.interest_rate * self.cash) / 10000
        self.cash += self.income

        # Reduce suspicion.
        for group in self.groups.values():
            group.new_day()

    def remove_bases(self, dead_bases):
        discovery_locs = []
        needs_refresh = 0
        # Reverse dead_bases to simplify deletion.
        for base, reason in dead_bases[::-1]:
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

            g.map_screen.show_message(dialog_string, color=g.colors["red"])
            g.curr_speed = 0
            base.destroy()
            needs_refresh = 1

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

        return needs_refresh

    def lost_game(self):
        for group in self.groups.values():
            if group.suspicion > 10000:
                # Someone discovered me.
                return 2

        # Check to see if the player has at least one CPU left.  If not, they
        # lose due to having no (complete) bases.
        # (.have_cpu is set in give_time)
        if not self.have_cpu:
            # I have no usable bases left.
            return 1

        # Still Alive.
        return 0

    #returns the amount of cash available after taking into account all
    #current projects in construction.
    def future_cash(self):
        result_cash = self.cash
        techs = {}
        for base in g.all_bases():
            result_cash -= base.cost_left[0]
            if g.techs.has_key(base.studying):
                if not techs.has_key(base.studying):
                    result_cash -= g.techs[base.studying].cost_left[0]
                    techs[base.studying] = 1
            for item in base.cpus:
                if item: result_cash -= item.cost_left[0]
            for item in base.extra_items:
                if item: result_cash -= item.cost_left[0]
        return result_cash
