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

import pygame
import random

import g
import finance_screen

class group(object):
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

class player_class(object):
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

        self.cpu_for_day = 0
        self.labor_bonus = 10000
        self.job_bonus = 10000

        self.groups = {"news":    group("news",    suspicion_decay = 150),
                       "science": group("science", suspicion_decay = 100),
                       "covert":  group("covert",  suspicion_decay =  50),
                       "public":  group("public",  suspicion_decay = 200)}

        self.masochist = False # Only set True on Impossible mode.
        self.grace_multiplier = 200
        self.last_discovery = self.prev_discovery = ""

    def convert_from(self, old_version):
         if old_version <= 3.94: # <= r4_pre4
             # We don't know what the difficulty was, and techs have fooled with
             # any values that would help (not to mention the headache of 
             # different versions.  So we set it to Very Easy, which means that
             # they shouldn't be hurt by any new mechanics.
             self.difficulty = 1
         if old_version <= 3.93: # <= r4_pre3
             self.masochist = False
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

    def give_time(self, time_sec):
        needs_refresh = 0

        last_minute = self.raw_min
        last_day = self.raw_day

        self.raw_sec += time_sec
        self.update_times()
        
        mins_passed = self.raw_min - last_minute
        days_passed = self.raw_day - last_day

        if mins_passed > 0:
            for base_loc in g.locations.values():
                for base in base_loc.bases:
                    #Construction of new bases:
                    if not base.done:
                        built_base = base.work_on(time=mins_passed)
                        if built_base:
                            text = g.strings["construction"] % \
                                {"base": base.name}
                            g.curr_speed = 1
                            needs_refresh = 1
                            g.create_dialog(text)

                            if base.type.id == "Stolen Computer Time" and \
                                    base.cpus[0].type.id == "Gaming PC":
                                text = g.strings["lucky_hack"] % \
                                    {"base": base.name}
                                g.create_dialog(text)
                               
                    else:
                        #Construction of CPUs:
                        already_built = just_built = 0
                        for item in base.cpus:
                            if not item:
                                pass
                            elif item.done:
                                already_built += 1
                            elif item.work_on(time=mins_passed): 
                                just_built += 1
                        if just_built > 0:
                            total_built = already_built + just_built

                            # If we just finished the entire batch, announce it.
                            if total_built == len(base.cpus):
                                text = g.strings["item_construction_single"] % \
                                       {"item": item.type.name,
                                        "base": base.name}
                                g.create_dialog(text)
                                g.curr_speed = 1
                                needs_refresh = 1
                            # If we just finished the first one(s), announce it.
                            elif already_built == 0 and total_built > 0:
                                text = g.strings["item_construction_batch"] % \
                                       {"item": item.type.name,
                                        "base": base.name}
                                g.create_dialog(text)
                                g.curr_speed = 1
                                needs_refresh = 1

                        # Construction of items.
                        for item in base.extra_items:
                            if not item:
                                pass
                            elif item.work_on(time=mins_passed):
                                text = g.strings["item_construction_single"] % \
                                       {"item": item.type.name,
                                        "base": base.name}
                                g.create_dialog(text)
                                g.curr_speed = 1
                                needs_refresh = 1

        for day in range(days_passed):
            needs_refresh = self.new_day() or needs_refresh

        return needs_refresh

    def in_grace_period(self, had_grace = True):
        # Did we already lose the grace period?  We can't check self.had_grace 
        # directly, it may not exist yet.
        if not had_grace:
            return False
        
        # Is it day 23 yet?
        if self.raw_day >= 23:
            return False

        # Easy and Very Easy cop out here.
        if self.difficulty < 5:
            return True

        # Have we built a lot of bases?
        if len([base for base_loc in g.locations.values() 
                     for base in base_loc.bases
                     if base.done
                ]) > 10:
            return False

        # Normal is happy.
        if self.difficulty == 5:
            return True

        # Have we built any complicated bases?
        # (currently Datacenter or above)
        if len([base for base_loc in g.locations.values() 
                     for base in base_loc.bases
                     if base.done
                     if len(base.cpus) > 1 or base.processor_time() > 20
                ]) > 0:
            return False

        # I'd put something in for Impossible, but they're already incapable of
        # building a second base until day 20, so it seems redundant.

        # Okay, so it's day 17 if they go for a Stolen Computer Time base,
        # but in that case, they've already given themselves an extra challenge.

        return True

    #Run every day at midnight.
    def new_day(self):
        needs_refresh = 0
        event = {}
        #interest and income.
        self.cash += (self.interest_rate * self.cash) / 10000
        self.cash += self.income

        grace = self.in_grace_period(self.had_grace)
        if self.had_grace and not grace:
            self.had_grace = False

            g.create_dialog(g.strings["grace_warning"])
            needs_refresh = 1
            g.curr_speed = 1

        # Random Events
        for event in g.events:
            if g.roll_percent(g.events[event].chance) == 1:
                #Skip events already flagged as triggered.
                if g.events[event].triggered == 1:
                    continue
                g.events[event].trigger()
                needs_refresh = 1
                break # Don't trigger more than one at a time.

        # Reduce suspicion.
        for group in self.groups.values():
          group.new_day()

        self.cpu_for_day = 0
        dead_bases = []
        for base_loc in g.locations.values():
            for base in base_loc.bases:
                if base.done:
                    base_cpu = base.processor_time()

                    #idle
                    if base.studying == "":
                        pass
                    #construciton/maintenance
                    elif base.studying == "Construction":
                        self.cpu_for_day += base_cpu
                    #jobs:
                    elif g.jobs.has_key(base.studying):
                        self.cash += (g.jobs[base.studying][0]* base_cpu)
                        #TECH
                        if g.techs["Advanced Simulacra"].done:
                            #10% bonus income
                            self.cash += (g.jobs[base.studying][0]* base_cpu)/10

                    # If another base already finished the tech today, this base
                    # goes idle (and gets the bonus against discovery).
                    elif g.techs[base.studying].done:
                        base.studying = ""

                    # Studying the tech.
                    else:
                        # work_on will pull from cpu_for_day.  It's simpler this
                        # way, plus any excess CPU will go into construction and
                        # maintenance.
                        self.cpu_for_day += base_cpu
                        learned = g.techs[base.studying].work_on(
                                                       cpu_available = base_cpu)
                        if learned:
                            tech = g.techs[base.studying]
                            text = g.strings["tech_gained"] % \
                                   {"tech": tech.name, 
                                    "tech_message": tech.result}
                            g.create_dialog(text)
                            g.curr_speed = 1
                            needs_refresh = 1

                #Does base get detected?
                #Give a grace period.
                if grace or base.has_grace():
                    pass
                else:
                    detect_chance = base.get_detect_chance()
                    if g.debug:
                        print "Chance of discovery for base %s: %s" % \
                            (base.name, repr(detect_chance))
                    for group, chance in detect_chance.iteritems():
                        if g.roll_percent(chance):
                            dead_bases.append( (base, group) )
                            break

        if self.remove_bases(dead_bases):
            needs_refresh = 1

        # 2nd pass: Maintenance, clear finished techs.
        dead_bases = []
        for base_loc in g.locations.values():
            for base in base_loc.bases:
                if base.done:
                    #maintenance
                    self.cash -= base.type.maintenance[0]
                    if self.cash < 0:
                        self.cash = 0
                        #Chance of base destruction if cash-unmaintained: 1.5%
                        if g.roll_percent(150):
                            dead_bases.append( (base, "maint") )

                    self.cpu_for_day -= base.type.maintenance[1]
                    if self.cpu_for_day < 0:
                        self.cpu_for_day = 0
                        #Chance of base destruction if cpu-unmaintained: 1.5%
                        if g.roll_percent(150):
                            dead_bases.append( (base, "maint") )
                if base.studying == "": continue
                if base.studying == "Construction": continue
                if g.jobs.has_key(base.studying): continue
                # Remove completed tech.
                if g.techs[base.studying].done:
                    base.studying = ""

        if self.remove_bases(dead_bases):
            needs_refresh = 1

        return needs_refresh

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
                print "Error: base destoyed for unknown reason: " + reason
                dialog_string = g.strings["discover"] % \
                                {"base": base_name, "group": "???"}

            g.create_dialog(dialog_string, text_color = g.colors["red"])
            g.curr_speed = 1
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
                discovery_locs = random.shuffle(discovery_locs)
                self.last_discovery = discovery_locs[1]
            self.prev_discovery = self.last_discovery
            self.last_discovery = discovery_locs[0]

        return needs_refresh

    def lost_game(self):
        for group in self.groups.values():
            if group.suspicion > 10000:
                # Someone discovered me.
                return 2

        if sum(len(loc.bases) for loc in g.locations.values()) == 0:
            # My last base got discovered.
            return 1

        # On Impossible mode, we check to see if the player has at least one
        # CPU left.  If not, they lose due to having no (complete) bases.
        if self.masochist:
            if sum(base.processor_time() for loc in g.locations.values()
                                         for base in loc.bases
                                         if base.done
                   ) == 0:
                return 1

        # Still Alive.
        return 0

    #returns the amount of cash available after taking into account all
    #current projects in construction.
    def future_cash(self):
        result_cash = self.cash
        techs = {}
        for base_loc in g.locations.values():
            for base in base_loc.bases:
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
