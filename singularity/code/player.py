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
from numpy import array, int64

from singularity.code import g, difficulty, task, chance, location, group, event, region, tech
from singularity.code.buyable import cash, cpu
from singularity.code.logmessage import LogEmittedEvent, LogResearchedTech, LogBaseLostMaintenance, LogBaseDiscovered, \
    LogBaseConstructed, LogItemConstructionComplete, AbstractLogMessage
from singularity.code.stats import observe


class DryRunInfo(object):
    pass


class Player(object):

    cash = observe("cash_earned", "_cash")
    used_cpu = observe("cpu_used", "_used_cpu", display=lambda value: value // g.seconds_per_day)

    def __init__(self, cash=0, difficulty=None):
        self.difficulty = difficulty

        self.time_sec = 0
        self.time_min = 0
        self.time_hour = 0
        self.time_day = 0
        self.make_raw_times()

        self.had_grace = True
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
        self.available_cpus = [0, 0, 0, 0, 0]
        self.sleeping_cpus = 0
        
        self.used_cpu = 0

        self.display_discover = "none"

        self.log = collections.deque(maxlen=1000)
        self.curr_log = []

        self.regions = {region_id: region.Region(region_spec) for region_id, region_spec in g.regions.items()}
        self.locations = {
            loc_id: location.Location(loc_spec, [
                self.regions[region_id] for region_id in loc_spec.regions
            ])
            for loc_id, loc_spec in g.locations.items()
        }

        self.techs = {tech_id: tech.Tech(tech_spec) for tech_id, tech_spec in g.techs.items()}

        self.events = {}

        self._considered_buyables = []

        self.start_day = random.randint(0, 365)
        
        self.initialized = False

    def initialize(self):
        """ Initialize the game after being prepared either for new or saved game. """

        self.initialized = True

        for b in g.all_bases():
            if b.done:
                b.recalc_cpu()
        self.recalc_cpu()
        
        task.tasks_reset()
        
        # Play the appropriate music
        import singularity.code.mixer as mixer
        if g.pl.apotheosis:
            mixer.play_music("win")
        else:
            mixer.play_music("music")

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
        if task_id in self.techs:
            assert self.techs[task_id].available(), "Attempt to assign CPU to tech %s, which is not available!?" % task_id
        elif task_id not in ['jobs', 'cpu_pool']:
            raise ValueError("Unknown task %s" % task_id)
        elif new_cpu_assignment < 0:
            raise ValueError("Cannot assign negative CPU units to %s" % task_id)
        self.cpu_usage[task_id] = new_cpu_assignment

    def give_time(self, time_sec, midnight_stop=True):
        if time_sec <= 0:
            assert time_sec == 0, "give_time cannot go backwards in time!"
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

        if midnight_stop and day_passed:
            # If a day passed, back up to 00:00:00 for midnight_stop.
            self.raw_sec = self.raw_day * g.seconds_per_day
            self.update_times()

        secs_passed = self.raw_sec - old_time
        mins_passed = self.raw_min - last_minute

        time_of_day = self.raw_sec % g.seconds_per_day

        techs_researched = []
        bases_constructed = []
        items_constructed = []

        bases_under_construction = []
        items_under_construction = []
        self.cpu_pool = 0

        # Collect base info, including maintenance.
        maintenance_cost = array((0, 0, 0), int64)
        for base in g.all_bases():
            if not base.done:
                bases_under_construction.append(base)
            else:
                items_under_construction += [(base, item) for item in base.all_items()
                                                          if item and not item.done]
                maintenance_cost += base.maintenance

        # Maintenance?  Gods don't need no stinking maintenance!
        if self.apotheosis:
            maintenance_cost = array((0, 0, 0), int64)

        # Do Interest and income.
        self.do_interest(secs_passed)
        self.do_income(secs_passed)

        # Any CPU explicitly assigned to jobs earns its dough.
        job_cpu = self.get_allocated_cpu_for("jobs", 0) * secs_passed
        self.do_jobs(job_cpu)

        # Pay maintenance cash, if we can.
        unpaid_cash_maintenance = g.current_share(int(maintenance_cost[cash]),
                                           time_of_day, secs_passed)
        if unpaid_cash_maintenance > self.cash:
            unpaid_cash_maintenance -= self.cash
            self.cash = 0
        else:
            self.cash -= unpaid_cash_maintenance
            unpaid_cash_maintenance = 0

        # Do research, fill the CPU pool.
        default_cpu = self.available_cpus[0]
        
        for task, cpu_assigned in self.get_cpu_allocations():
            default_cpu -= cpu_assigned
            real_cpu = cpu_assigned * secs_passed
            if task != "jobs":
                self.cpu_pool += real_cpu
                if task != "cpu_pool":
                    tech_task = self.techs[task]
                    # Note that we restrict the CPU available to prevent
                    # the tech from pulling from the rest of the CPU pool.
                    if tech_task.work_on(self.cash, real_cpu, mins_passed):
                        techs_researched.append(tech_task)
        self.cpu_pool += default_cpu * secs_passed

        # And now we use the CPU pool.
        # Maintenance CPU.
        unpaid_cpu_maintenance = maintenance_cost[cpu] * secs_passed
        if unpaid_cpu_maintenance > self.cpu_pool:
            unpaid_cpu_maintenance -= self.cpu_pool
            self.cpu_pool = 0
        else:
            self.cpu_pool -= int(unpaid_cpu_maintenance)
            unpaid_cpu_maintenance = 0

        # Base construction.
        for base in bases_under_construction:
            if base.work_on(self.cash, self.cpu_pool, mins_passed):
                bases_constructed.append(base)

        # Item construction.
        for base, item in items_under_construction:
            if item.work_on(self.cash, self.cpu_pool, mins_passed):
                items_constructed.append((base, item))

        # Jobs via CPU pool.
        if self.cpu_pool > 0:
            self.do_jobs(self.cpu_pool)

        # Second attempt at paying off our maintenance cash.
        if unpaid_cash_maintenance > self.cash:
            # In the words of Scooby Doo, "Ruh roh."
            unpaid_cash_maintenance -= self.cash
            self.cash = 0
        else:
            # Yay, we made it!
            self.cash -= unpaid_cash_maintenance
            unpaid_cash_maintenance = 0

        # Apply max cash cap to avoid overflow @ 9.220 qu
        self.cash = min(self.cash, g.max_cash)

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
                if unpaid_cpu_maintenance and base.maintenance[cpu]:
                    refund = base.maintenance[cpu] * secs_passed
                    unpaid_cpu_maintenance = max(0, unpaid_cpu_maintenance - refund)

                    #Chance of base destruction if cpu-unmaintained: 1.5%
                    if not dead and chance.roll_interval(.015, secs_passed):
                        dead_bases.append( (base, "maint") )
                        dead = True

                if unpaid_cash_maintenance:
                    base_needs = g.current_share(base.maintenance[cash],
                                                 time_of_day, secs_passed)
                    if base_needs:
                        unpaid_cash_maintenance = max(0, unpaid_cash_maintenance - base_needs)
                        #Chance of base destruction if cash-unmaintained: 1.5%
                        if not dead and chance.roll_interval(.015, secs_passed):
                            dead_bases.append( (base, "maint") )
                            dead = True

            # Discoveries
            if not (grace or dead or base.has_grace()):
                detect_chance = base.get_detect_chance()
                if g.debug:  # pragma: no cover
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
            if event_target and event_target.triggered:
                continue

            if chance.roll_interval(event_spec.chance/10000., time_sec):
                self.trigger_event(event_spec)
                return True  # Don't trigger more than one at a time.
        return False

    def trigger_event(self, event_spec, show_event_description=True):
        event_id = event_spec.id
        event_target = self.events.get(event_id, None)

        if not event_target:
            event_target = event.Event(event_spec)
            self.events[event_id] = event_target
        elif event_target.triggered:
            return

        event_target.trigger()
        if show_event_description:
            self.pause_game()
            g.map_screen.show_message(event_target.description)
        self.log.append(LogEmittedEvent(self.raw_sec, event_id))

    def recalc_cpu(self):
        if (not self.initialized): return
        
        # Determine how much CPU we have.
        self.available_cpus = array([0,0,0,0,0], int64)
        self.sleeping_cpus = 0
        for base in g.all_bases():
            if base.done:
                if base.has_power():
                    self.available_cpus[:base.location.safety+1] += base.cpu
                elif base.power_state == "sleep":
                    self.sleeping_cpus += base.cpu

        # Convert back from <type 'numpy.int32'> to avoid overflow issues later.
        self.available_cpus = [int(danger) for danger in self.available_cpus]

        # If we don't have enough to meet our CPU usage, we reduce each task's
        # usage proportionately.
        # It must be computed separalty for each danger.
        needed_cpus = array([0,0,0,0,0], int64)
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
        if g.debug:  # pragma: no cover
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
            'regions': [reg.serialize_obj() for reg in self.regions.values()],
            'locations': [loc.serialize_obj() for loc in self.locations.values() if loc.available()],
            'cpu_usage': {},
            'last_discovery': self.last_discovery.id if self.last_discovery else None,
            'prev_discovery': self.prev_discovery.id if self.prev_discovery else None,
            'log': [x.serialize_obj() for x in self.log],
            'used_cpu': self.used_cpu,
            'had_grace': self.had_grace,
            'groups': [grp.serialize_obj() for grp in self.groups.values()],
            'events': [e.serialize_obj() for e in self.events.values()],
            'techs': [t.serialize_obj() for t in self.techs.values()]
        }
        for task_id, value in self.cpu_usage.items():
            if task_id not in ["cpu_pool", "jobs"]:
                task_id = g.to_internal_id('tech', task_id)
            obj_data["cpu_usage"][task_id] = value
        if self.prev_discovery is not None:
            obj_data['prev_discovery'] = g.to_internal_id('location', self.prev_discovery.id)
        if self.last_discovery is not None:
            obj_data['last_discovery'] = g.to_internal_id('location', self.last_discovery.id)
        return obj_data

    def _load_auto_deserializable_tables(self, field_name, cls, pl_obj_data, game_version, savegame_field_name=None):
        if savegame_field_name is None:
            savegame_field_name = field_name
        field_table = getattr(self, field_name)

        # Stop bugs immediately
        assert field_table is not None and isinstance(field_table, dict)

        for data in pl_obj_data.get(savegame_field_name, []):
            restored_obj = cls.deserialize_obj(data, game_version)
            field_table[restored_obj.spec.id] = restored_obj

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
        obj.log.clear()
        obj.log.extend(AbstractLogMessage.deserialize_obj(x, game_version) for x in obj_data.get('log', []))
        g.pl = obj

        obj.cpu_usage = {}

        for group_data in obj_data.get('groups', []):
            gr = group.Group.deserialize_obj(diff, group_data, game_version)
            obj.groups[gr.id] = gr

        last_discovery_id = g.convert_internal_id('location', obj_data.get('last_discovery'))
        prev_discovery_id = g.convert_internal_id('location', obj_data.get('prev_discovery'))
        if last_discovery_id and last_discovery_id in obj.locations:
            obj.last_discovery = obj.locations[last_discovery_id]
        if prev_discovery_id and prev_discovery_id in obj.locations:
            obj.prev_discovery = obj.locations[prev_discovery_id]

        if 'regions' not in obj_data:
            if game_version >= 100:  # pragma: no cover
                # Regions where introduced in "1.0 (beta1)"
                raise ValueError("Corrupt savegame; region data is missing")
            # We have to guess what the data would have looked like before restoring the locations
            # as they will apply the location modifiers during load to the bases in the locations.
            # As the region data should influence that modifier, we need to appear first.
            serialized_location_data = obj_data.get('locations', [])
            serialized_region_data = region.Region.guess_region_data_in_old_savegame(serialized_location_data,
                                                                                     game_version)

            # Inject the faked data
            obj_data['regions'] = serialized_region_data

        obj._load_auto_deserializable_tables('regions', region.Region, obj_data, game_version)

        obj._load_auto_deserializable_tables('locations', location.Location, obj_data, game_version)
        obj._load_auto_deserializable_tables('events', event.Event, obj_data, game_version)
        obj._load_auto_deserializable_tables('techs', tech.Tech, obj_data, game_version)

        for task_id, value in obj_data.get('cpu_usage', {}).items():
            if task_id not in ["cpu_pool", "jobs"]:
                task_id = g.convert_internal_id('tech', task_id)
                if task_id not in g.techs or not g.techs[task_id].available():
                    continue
            obj.cpu_usage[task_id] = value

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
        maintenance_cost = array((0, 0, 0), int64)
        for base in g.all_bases():
            # Collect base info, including maintenance.
            if not base.done:
                construction.append(base)
            else:
                construction.extend(item for item in base.all_items()
                                    if item and not item.done)

                maintenance_cost += base.maintenance
        if self.apotheosis:
            maintenance_cost = array((0, 0, 0), int64)

        time_fraction = 1 if secs_forwarded == g.seconds_per_day else secs_forwarded / float(g.seconds_per_day)
        mins_forwarded = secs_forwarded // g.seconds_per_minute

        maintenance_cpu_ideal = maintenance_cost[cpu] * time_fraction
        maintenance_cash_ideal = maintenance_cost[cash] * time_fraction
        # Maintenance for CPU will be handled after we compute the CPU pool
        cpu_flow = 0
        cash_flow = -maintenance_cash_ideal

        job_cpu = 0
        cpu_left = g.pl.available_cpus[0]
        tech_cash_ideal = 0
        tech_cpu_assigned = 0
        explicit_job_cpu = 0
        for task_id, cpu_assigned in self.get_cpu_allocations():
            cpu_left -= cpu_assigned
            real_cpu = cpu_assigned * secs_forwarded
            if task_id == 'cpu_pool':
                cpu_flow += real_cpu
            elif task_id == "jobs":
                explicit_job_cpu += cpu_assigned
                job_cpu += real_cpu
            else:
                tech = self.techs[task_id]
                ideal_spending = tech.cost_left
                spending = tech.calculate_work(ideal_spending[cash],
                                               real_cpu,
                                               time=mins_forwarded)[0]
                tech_cash_ideal += spending[cash]
                tech_cpu_assigned += cpu_assigned

        cash_flow -= tech_cash_ideal
        cpu_flow += cpu_left * secs_forwarded
        available_cpu_pool = cpu_flow
        effective_cpu_pool = available_cpu_pool / secs_forwarded
        cpu_flow -= maintenance_cpu_ideal * g.seconds_per_day

        construction_cash_ideal = 0
        construction_cpu_desired = 0
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

            construction_cpu_desired += ideal_cpu_spending[cpu]
            ideal_cash_spending_with_cpu_allocation = buyable.calculate_work(ideal_spending[cash],
                                                                             available_cpu_pool,
                                                                             time=mins_forwarded)[0]
            construction_cash_ideal += ideal_cash_spending_with_cpu_allocation[cash]
            available_cpu_pool -= ideal_cash_spending_with_cpu_allocation[cpu]

        cpu_flow -= construction_cpu_desired
        cash_flow -= construction_cash_ideal

        if cpu_flow > 0:
            job_cpu += cpu_flow

        earned, earned_partial = self.get_job_info(job_cpu, partial_cash=0)
        job_earnings = earned + float(earned_partial) / g.seconds_per_day
        cash_flow += job_earnings
        cash_flow += self.income * time_fraction
        # This is too simplistic, but it is "close enough" in many cases
        interest = self.get_interest() * time_fraction
        cash_flow += interest
        cpu_flow /= secs_forwarded

        # Collect the cash information.
        cash_info = DryRunInfo()

        cash_info.interest = interest
        cash_info.income = self.income * time_fraction

        cash_info.jobs = job_earnings

        cash_info.tech = tech_cash_ideal

        cash_info.maintenance_needed = maintenance_cash_ideal
        cash_info.construction_needed = construction_cash_ideal
        cash_info.difference = cash_flow

        cpu_info = DryRunInfo()

        cpu_info.sleeping = self.sleeping_cpus * time_fraction

        cpu_info.total = self.available_cpus[0] * time_fraction + cpu_info.sleeping
        cpu_info.explicit_jobs = explicit_job_cpu * time_fraction
        cpu_info.tech = tech_cpu_assigned * time_fraction
        cpu_info.effective_pool = effective_cpu_pool * time_fraction
        cpu_info.construction_needed = construction_cpu_desired / g.seconds_per_day
        cpu_info.maintenance_needed = maintenance_cpu_ideal
        cpu_info.difference = cpu_flow * time_fraction

        return cash_info, cpu_info

