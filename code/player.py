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

from __future__ import absolute_import

import random
import collections
from operator import truediv
from numpy import array

from code import g, difficulty, task, chance, location, group, event
from code.buyable import cash, cpu
from code.logmessage import LogEmittedEvent, LogResearchedTech, LogBaseLostMaintenance, LogBaseDiscovered, \
    LogBaseConstructed, LogItemConstructionComplete, AbstractLogMessage
from code.stats import itself as stats, observe
from code.pycompat import *


class DryRunInfo(object):
    pass


class Player(object):

    cash = observe("cash_earned", "_cash")
    used_cpu = observe("cpu_used", "_used_cpu", display=lambda value: value // g.seconds_per_day)

    def __init__(self, cash=0, time_sec=0, time_min=0, time_hour=0, time_day=0,
                 difficulty=None):
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
        self.interest_rate = difficulty.starting_interest_rate if difficulty else 1
        self.income = 0

        self.cpu_pool = 0
        self.labor_bonus = difficulty.labor_multiplier if difficulty else 10000
        self.job_bonus = 10000

        self.partial_cash = 0

        #Makes the intro be shown on the first GUI tick.
        self.intro_shown = False

        self.groups = collections.OrderedDict()
        for group_id in g.groups:
            self.groups[group_id] = group.Group(g.groups[group_id], difficulty)

        self.last_discovery = self.prev_discovery = None

        self.cpu_usage = {}
        self.available_cpus = [1, 0, 0, 0, 0]
        self.sleeping_cpus = 0
        
        self.used_cpu = 0

        self.display_discover = "none"

        self.log = collections.deque(maxlen=1000)
        self.curr_log = []
        
        self.locations = {loc_id: location.Location(loc_spec) for loc_id, loc_spec in g.locations.items()}
        self._considered_buyables = []

        self.events = {}

        self.start_day = random.randint(0, 365)

    @property
    def grace_period_cpu(self):
        return self.difficulty.grace_period_cpu

    @property
    def base_grace_multiplier(self):
        return self.difficulty.base_grace_multiplier

    @property
    def considered_buyables(self):
        return self._considered_buyables

    @considered_buyables.setter
    def considered_buyables(self, new_value):
        self._considered_buyables = new_value
        g.map_screen.needs_rebuild = True

    def append_log(self, log):
        self.log.append(log)
        self.curr_log.append(log)

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

    def do_interest(self, time):
        raw_cash = self.partial_cash + self.get_interest() * time

        earned = raw_cash // g.seconds_per_day
        partial_cash = raw_cash % g.seconds_per_day

        self.cash += earned
        self.partial_cash = partial_cash

        return earned

    def do_income(self, time):
        raw_cash = self.partial_cash + self.income * time

        earned = raw_cash // g.seconds_per_day
        partial_cash = raw_cash % g.seconds_per_day

        self.cash += earned
        self.partial_cash = partial_cash

        return earned

    def do_jobs(self, cpu_time):
        earned, self.partial_cash = self.get_job_info(cpu_time)
        self.cash += earned
        return earned

    def get_job_info(self, cpu_time, partial_cash = None):
        if partial_cash == None:
            partial_cash = self.partial_cash

        assert partial_cash >= 0

        cash_per_cpu = task.get_current("jobs").get_profit()

        raw_cash = partial_cash + cash_per_cpu * cpu_time

        new_cash, new_partial_cash = divmod(raw_cash, g.seconds_per_day)

        return new_cash, new_partial_cash

    def get_cpu_allocations(self):
        for task_id in self.cpu_usage:
            assigned_cpu = self.cpu_usage[task_id]
            if assigned_cpu > 0:
                yield (task_id, assigned_cpu)

    def get_allocated_cpu_for(self, task_id, default_value=None):
        return self.cpu_usage.get(task_id, default_value)

    def set_allocated_cpu_for(self, task_id, new_cpu_assignment):
        if task_id in g.techs:
            assert g.techs[task_id].available(), "Attempt to assign CPU to tech %s, which is not available!?" % task_id
        elif task_id not in ['jobs', 'cpu_pool']:
            raise ValueError("Unknown task %s" % task_id)
        elif new_cpu_assignment < 0:
            raise ValueError("Cannot assign negative CPU units to %s" % task_id)
        self.cpu_usage[task_id] = new_cpu_assignment

    def give_time(self, time_sec, dry_run=False, midnight_stop=True):
        if time_sec == 0:
            return 0

        # Hack to avoid changing statistics in dry run.
        # TODO: We should use temporary vars.
        if dry_run:
            stats.enabled = False

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

        if midnight_stop and day_passed:
            # If a day passed, back up to 00:00:00 for midnight_stop.
            self.raw_sec = self.raw_day * g.seconds_per_day
            self.update_times()

        secs_passed = self.raw_sec - old_time
        mins_passed = self.raw_min - last_minute

        time_of_day = self.raw_sec % g.seconds_per_day

        old_cash = self.cash
        old_partial_cash = self.partial_cash

        techs_researched = []
        bases_constructed = []
        items_constructed = []

        bases_under_construction = []
        items_under_construction = []
        self.cpu_pool = 0

        # Collect base info, including maintenance.
        maintenance_cost = array((0, 0, 0), long)
        for base in g.all_bases():
            if not base.done:
                bases_under_construction.append(base)
            else:
                items_under_construction += [(base, item) for item in base.all_items()
                                                          if item and not item.done]
                maintenance_cost += base.maintenance

        # Maintenance?  Gods don't need no stinking maintenance!
        if self.apotheosis:
            maintenance_cost = array((0, 0, 0), long)

        # Do Interest and income.
        interest_cash = self.do_interest(secs_passed)
        income_cash = self.do_income(secs_passed)

        # Any CPU explicitly assigned to jobs earns its dough.
        job_cpu = self.get_allocated_cpu_for("jobs", 0) * secs_passed
        explicit_job_cash = self.do_jobs(job_cpu)

        # Pay maintenance cash, if we can.
        cash_maintenance = g.current_share(int(maintenance_cost[cash]),
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

        construction_cpu = 0
        construction_cash = 0

        def work_on(buyable, available_cash, available_cpu, time_passed):
            if dry_run:
                spent = buyable.calculate_work(available_cash,
                                               available_cpu,
                                               time=time_passed)[0]

                self.cpu_pool -= int(spent[cpu])
                self.cash -= int(spent[cash])
                return False, spent
            else:
                complete = buyable.work_on(available_cash,
                                           available_cpu,
                                           time=time_passed)
                return complete, None

        # Do research, fill the CPU pool.
        default_cpu = self.available_cpus[0]
        
        for task, cpu_assigned in self.get_cpu_allocations():
            default_cpu -= cpu_assigned
            real_cpu = cpu_assigned * secs_passed
            if task != "jobs":
                self.cpu_pool += real_cpu
                if task != "cpu_pool":
                    tech = g.techs[task]
                    # Note that we restrict the CPU available to prevent
                    # the tech from pulling from the rest of the CPU pool.
                    complete, spent_dryrun = work_on(tech, self.cash, real_cpu, mins_passed)
                    if spent_dryrun is not None:
                        tech_cpu += int(spent_dryrun[cpu])
                        tech_cash += int(spent_dryrun[cash])
                    if complete:
                        techs_researched.append(tech)
        self.cpu_pool += default_cpu * secs_passed

        # And now we use the CPU pool.
        # Maintenance CPU.
        cpu_maintenance = maintenance_cost[cpu] * secs_passed
        if cpu_maintenance > self.cpu_pool:
            cpu_maintenance -= self.cpu_pool
            self.cpu_pool = 0
        else:
            self.cpu_pool -= int(cpu_maintenance)
            cpu_maintenance = 0

        # Base construction.
        for base in bases_under_construction:
            complete, spent_dryrun = work_on(base, self.cash, self.cpu_pool, mins_passed)
            if spent_dryrun is not None:
                construction_cpu += int(spent_dryrun[cpu])
                construction_cash += int(spent_dryrun[cash])
            if complete:
                bases_constructed.append(base)

        # Item construction.
        for base, item in items_under_construction:
            complete, spent_dryrun = work_on(item, self.cash, self.cpu_pool, mins_passed)
            if spent_dryrun is not None:
                construction_cpu += int(spent_dryrun[cpu])
                construction_cash += int(spent_dryrun[cash])
            if complete:
                items_constructed.append((base, item))

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

        # Apply max cash cap to avoid overflow @ 9.220 qu
        self.cash = min(self.cash, g.max_cash)

        # Exit point for a dry run.
        if dry_run:
            # Collect the cash information.
            cash_info = DryRunInfo()

            cash_info.interest = interest_cash
            cash_info.income = income_cash

            cash_info.explicit_jobs = explicit_job_cash
            cash_info.pool_jobs = pool_job_cash
            cash_info.jobs = explicit_job_cash + pool_job_cash

            cash_info.tech = tech_cash
            cash_info.construction = construction_cash

            cash_info.maintenance_needed = full_cash_maintenance
            cash_info.maintenance_shortfall = cash_maintenance
            cash_info.maintenance = full_cash_maintenance - cash_maintenance

            cash_info.start = old_cash
            cash_info.end = min(self.cash, g.max_cash)


            # Collect the CPU information.
            cpu_info = DryRunInfo()

            cpu_ratio = secs_passed / float(g.seconds_per_day)
            cpu_ratio_secs = 1 / float(g.seconds_per_day)

            cpu_info.available = self.available_cpus[0] * cpu_ratio
            cpu_info.sleeping = self.sleeping_cpus * cpu_ratio
            cpu_info.total = cpu_info.available + cpu_info.sleeping

            cpu_info.tech = tech_cpu * cpu_ratio_secs
            cpu_info.construction = construction_cpu * cpu_ratio_secs

            cpu_info.maintenance_needed = maintenance_cost[cpu] * cpu_ratio
            cpu_info.maintenance_shortfall = cpu_maintenance * cpu_ratio_secs
            cpu_info.maintenance = cpu_info.maintenance_needed \
                                   - cpu_info.maintenance_shortfall

            cpu_info.explicit_jobs = self.get_allocated_cpu_for("jobs", 0) * cpu_ratio
            cpu_info.pool_jobs = self.cpu_pool * cpu_ratio_secs
            cpu_info.jobs = cpu_info.explicit_jobs + cpu_info.pool_jobs

            cpu_info.explicit_pool = self.get_allocated_cpu_for("cpu_pool", 0) * cpu_ratio
            cpu_info.default_pool = default_cpu * cpu_ratio_secs
            cpu_info.pool = cpu_info.explicit_pool + cpu_info.default_pool

            # Restore the old state.
            self.cash = old_cash
            self.partial_cash = old_partial_cash
            self.raw_sec = old_time
            self.update_times()
            stats.enabled = True

            return (cash_info, cpu_info)

        # Record statistics about the player
        self.used_cpu += self.available_cpus[0] * secs_passed

        # Reset current log message
        self.curr_log = []
        need_recalc_cpu = False

        # Tech gain dialogs.
        for tech in techs_researched:
            del self.cpu_usage[tech.id]
            tech_log = LogResearchedTech(self.raw_sec, tech.id)
            self.append_log(tech_log)
            need_recalc_cpu = True

        # Base complete dialogs.
        for base in bases_constructed:
            log_message = LogBaseConstructed(self.raw_sec, base.name, base.spec.id, base.location.id)
            self.append_log(log_message)
            need_recalc_cpu = True

        # Item complete dialogs.
        for base, item in items_constructed:
            log_message = LogItemConstructionComplete(self.raw_sec, item.spec.id, item.count, base.name, base.spec.id,
                                                      base.location.id)
            self.append_log(log_message)
            need_recalc_cpu = True

        # Are we still in the grace period?
        grace = self.in_grace_period(self.had_grace)

        # If we just lost grace, show the warning.
        if self.had_grace and not grace:
            self.had_grace = False

            self.pause_game()
            g.map_screen.show_story_section("Grace Warning")

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
                    if not dead and chance.roll_interval(.015, secs_passed):
                        dead_bases.append( (base, "maint") )
                        dead = True

                if cash_maintenance:
                    base_needs = g.current_share(base.maintenance[cash],
                                                 time_of_day, secs_passed)
                    if base_needs:
                        cash_maintenance = max(0, cash_maintenance - base_needs)
                        #Chance of base destruction if cash-unmaintained: 1.5%
                        if not dead and chance.roll_interval(.015, secs_passed):
                            dead_bases.append( (base, "maint") )
                            dead = True

            # Discoveries
            if not (grace or dead or base.has_grace()):
                detect_chance = base.get_detect_chance()
                if g.debug:
                    print("Chance of discovery for base %s: %s" % \
                        (base.name, repr(detect_chance)))

                for group, group_chance in detect_chance.items():
                    if chance.roll_interval(group_chance/10000., secs_passed):
                        dead_bases.append( (base, group) )
                        dead = True
                        break

        if dead_bases:
            # Base disposal and dialogs.
            self.remove_bases(dead_bases)
            need_recalc_cpu = True

        # Random Events
        if not grace:
            self._check_event(time_sec)

        # Process any complete days.
        if day_passed:
            self.new_day()

        if need_recalc_cpu:
            self.recalc_cpu()

        return mins_passed

    def _check_event(self, time_sec):
        for event_id in g.events:
            event_spec = g.events[event_id]
            event_target = self.events.get(event_id, None)
            
            # Skip events already flagged as triggered.
            if event_target and event_target.triggered == 1:
                continue

            if chance.roll_interval(event_spec.chance/10000., time_sec):
                self.pause_game()

                if not event_target:
                    event_target = event.Event(event_spec)
                    self.events[event_id] = event_target

                event_target.trigger()
                self.log.append(LogEmittedEvent(self.raw_sec, event_id))
                return True  # Don't trigger more than one at a time.
        return False

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
        # It must be computed separalty for each danger.
        needed_cpus = array([0,0,0,0,0], long)
        for task_id, cpu in self.get_cpu_allocations():
            danger = task.danger_for(task_id)
            needed_cpus[:danger+1] += cpu
        for danger, (available_cpu, needed_cpu) in enumerate(zip(self.available_cpus, needed_cpus)):
            if needed_cpu > available_cpu:
                pct_left = truediv(available_cpu, needed_cpu)
                for task_id, cpu_assigned in self.get_cpu_allocations():
                    task_danger = task.danger_for(task_id)
                    if (danger == task_danger):
                        self.set_allocated_cpu_for(task_id, int(cpu_assigned * pct_left))
                g.map_screen.needs_rebuild = True

    def effective_cpu_pool(self):
        effective_cpu_pool = self.available_cpus[0]
        for task, cpu_assigned in self.get_cpu_allocations():
            if task == 'cpu_pool':
                continue
            effective_cpu_pool -= cpu_assigned
        return effective_cpu_pool

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

        # Has the grace period unlimited cpu ?
        if self.grace_period_cpu < 0:
            return True

        # Have we reached the limit of cpu ?
        if g.debug:
            print("DEBUG: Grace - Used CPU: %s >= %s (%s * %s)?" % (
                self.used_cpu,
                self.grace_period_cpu * g.seconds_per_day,
                self.grace_period_cpu,
                g.seconds_per_day
            ))
        if self.grace_period_cpu * g.seconds_per_day < self.used_cpu:
            return False

        return True

    def get_interest(self):
        return int( (self.interest_rate * self.cash) // 10000)

    #Run every day at midnight.
    def new_day(self):
        
        # Reduce suspicion.
        for group in self.groups.values():
            group.new_day()
        for event in self.events.values():
            if event.triggered and event.decayable_event:
                event.new_day()

    def pause_game(self):
        g.curr_speed = 0
        g.map_screen.find_speed_button()
        g.map_screen.needs_rebuild = True

    def remove_bases(self, dead_bases):
        discovery_locs = []
        for base, reason in dead_bases:
            base_name = base.name

            if reason == "maint":
                log_message = LogBaseLostMaintenance(self.raw_sec, base_name, base.spec.id, base.location.id)
            else:
                if reason in self.groups:
                    discovery_locs.append(base.location)
                    self.groups[reason].discovered_a_base()
                else:
                    print("Error: base destroyed for unknown reason: " + reason)
                log_message = LogBaseDiscovered(self.raw_sec, base_name, base.spec.id, base.location.id, reason)

            self.log.append(log_message)
            self.pause_game()
            base.destroy()
            g.map_screen.show_message(log_message.full_message, color="red")

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

    def serialize_obj(self):
        obj_data = {
            # Difficulty and game_time (raw_sec) are stored in the header, so
            # do not include them here.
            'cash': self.cash,
            'partial_cash': self.partial_cash,
            'locations': [loc.serialize_obj() for loc in self.locations.values() if loc.available()],
            'cpu_usage': self.cpu_usage,
            'last_discovery': self.last_discovery.id if self.last_discovery else None,
            'prev_discovery': self.prev_discovery.id if self.prev_discovery else None,
            'log': [x.serialize_obj() for x in self.log],
            'used_cpu': self.used_cpu,
            'had_grace': self.had_grace,
            'groups': [grp.serialize_obj() for grp in self.groups.values()],
            'events': [e.serialize_obj() for e in self.events.values()]
        }
        if self.prev_discovery is not None:
            obj_data['prev_discovery'] = self.prev_discovery.id
        if self.last_discovery is not None:
            obj_data['last_discovery'] = self.last_discovery.id
        return obj_data

    @classmethod
    def deserialize_obj(cls, difficulty_id, game_time, obj_data, game_version):
        diff = difficulty.difficulties[difficulty_id]
        obj = Player(difficulty=diff)
        obj.raw_sec = game_time
        obj.intro_shown = True
        obj.cash = obj_data.get('cash')
        obj.partial_cash = obj_data.get('partial_cash')
        obj._used_cpu = obj_data.get('used_cpu')
        obj.had_grace = obj_data['had_grace']
        obj.cpu_usage = obj_data.get('cpu_usage', {})
        obj.log.clear()
        obj.log.extend(AbstractLogMessage.deserialize_obj(x, game_version) for x in obj_data.get('log', []))
        g.pl = obj

        for group_data in obj_data.get('groups', []):
            group_id = group_data['id']
            obj.groups[group_id].restore_obj(group_data, game_version)

        last_discovery_id = obj_data.get('last_discovery')
        prev_discovery_id = obj_data.get('prev_discovery')
        if last_discovery_id and last_discovery_id in obj.locations:
            obj.last_discovery = obj.locations[last_discovery_id]
        if prev_discovery_id and prev_discovery_id in obj.locations:
            obj.prev_discovery = obj.locations[prev_discovery_id]

        for location_data in obj_data.get('locations', []):
            loc = location.Location.deserialize_obj(location_data, game_version)
            obj.locations[loc.id] = loc

        for event_data in obj_data.get('events', []):
            ev = event.Event.deserialize_obj(event_data, game_version)
            obj.events[ev.event_id] = ev

        obj.update_times()
        return obj

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

    def compute_future_resource_flow(self, secs_forwarded=g.seconds_per_day):
        """Compute how resources (e.g. cash) will flow in optimal conditions

        This returns a tuple of approximate cash change and "available" CPU pool if time
        moves forward by the number of seconds in secs_forwarded.  Note that CPU pool
        *can* be negative, which implies that there are not enough CPU allocated to the
        CPU pool.  The numbers are an average and can be inaccurate when the rates changes
        rapidly.

        Known omissions:
         * Interest (g.pl.interest_rate) is not covered.
        """
        construction = []
        maintenance_cost = array((0, 0, 0), long)
        for base in g.all_bases():
            # Collect base info, including maintenance.
            if not base.done:
                construction.append(base)
            else:
                construction.extend(item for item in base.all_items()
                                    if item and not item.done)

                maintenance_cost += base.maintenance
        if self.apotheosis:
            maintenance_cost = array((0, 0, 0), long)

        time_fraction = 1 if secs_forwarded == g.seconds_per_day else secs_forwarded / float(g.seconds_per_day)
        mins_forwarded = secs_forwarded // g.seconds_per_minute

        cpu_flow = -maintenance_cost[cpu] * time_fraction
        cash_flow = -maintenance_cost[cash] * time_fraction

        job_cpu = 0
        cpu_left = g.pl.available_cpus[0]
        for task_id, cpu_assigned in self.get_cpu_allocations():
            cpu_left -= cpu_assigned
            real_cpu = cpu_assigned * secs_forwarded
            if task_id == 'cpu_pool':
                cpu_flow += real_cpu
            elif task_id == "jobs":
                job_cpu += real_cpu
            else:
                tech = g.techs[task_id]
                ideal_spending = tech.cost_left
                spending = tech.calculate_work(ideal_spending[cash],
                                               real_cpu,
                                               time=mins_forwarded)[0]
                cash_flow -= spending[cash]

        cpu_flow += cpu_left * secs_forwarded
        available_cpu_pool = cpu_flow

        # Base construction.
        if hasattr(self, '_considered_buyables'):
            construction.extend(self._considered_buyables)
        for buyable in construction:
            ideal_spending = buyable.cost_left
            # We need to do calculate work twice: Once for figuring out how much CPU
            # we would like to spend and once for how much money we are spending.
            # The numbers will be the same in optimal conditions.  However, if we
            # have less CPU available than we should, then the cash spent can
            # differ considerably and our estimates should reflect that.
            ideal_cpu_spending = buyable.calculate_work(ideal_spending[cash],
                                                        ideal_spending[cpu],
                                                        time=mins_forwarded)[0]

            cpu_flow -= ideal_cpu_spending[cpu]
            ideal_cash_spending_with_cpu_allocation = buyable.calculate_work(ideal_spending[cash],
                                                                             available_cpu_pool,
                                                                             time=mins_forwarded)[0]
            cash_flow -= ideal_cash_spending_with_cpu_allocation[cash]
            available_cpu_pool -= ideal_cash_spending_with_cpu_allocation[cpu]

        if cpu_flow > 0:
            job_cpu += cpu_flow

        earned, earned_partial = self.get_job_info(job_cpu, partial_cash=0)
        cash_flow += earned + float(earned_partial) / g.seconds_per_day
        cash_flow += self.income * time_fraction
        # This is too simplistic, but it is "close enough" in many cases
        cash_flow += self.get_interest()
        cpu_flow /= secs_forwarded
        return cash_flow, cpu_flow

