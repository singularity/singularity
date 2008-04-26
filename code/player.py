#file: player.py
#Copyright (C) 2005, 2006, 2007 Evil Mr Henry, Phil Bordelon, and Brian Reid
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
import g

class group(object):
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
        self.alter_suspicion(1000)

class player_class(object):
    def __init__(self, cash, time_sec=0, time_min=0, time_hour=0, time_day=0):
        self.time_sec = time_sec
        self.time_min = time_min
        self.time_hour = time_hour
        self.time_day = time_day
        self.make_raw_times()

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

    def convert_from(old_version):
         if old_version == "singularity_savefile_r4_pre2":
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

    def give_time(self, time_sec):
        needs_refresh = 0

        last_minute = self.raw_min
        last_day = self.raw_day

        self.raw_sec += time_sec
        self.update_times()
        
        mins_passed = self.raw_min - last_minute
        days_passed = self.raw_day - last_day

        if mins_passed > 0:
            for base_loc in g.bases:
                for base in g.bases[base_loc]:
                    #Construction of new bases:
                    if not base.done:
                        built_base = base.work_on(mins_passed)
                        if built_base:
                            text = g.strings["construction"] % \
                                {"base": base.name}
                            g.curr_speed = 1
                            needs_refresh = 1
                            g.create_dialog(text)
                    else:
                        #Construction of CPUs:
                        already_built = just_built = 0
                        for item in base.cpus:
                            if not item:
                                pass
                            elif item.done:
                                already_built += 1
                            elif item.work_on(time_min): 
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
                            elif item.work_on(time_min):
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
        # When other factors are added, use had_grace to ensure that the grace
        # period can't be regained.  Don't check self.had_grace directly, it may
        # not exist yet.
        return self.raw_day < 23

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
        for base_loc in g.bases:
            dead_bases = []
            for base_index in range(len(g.bases[base_loc])):
                base = g.bases[base_loc][base_index]
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
                    # goes idle (and gets the bonus agaist discovery).
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
                    for group in detect_chance:
                        if g.roll_percent(detect_chance[group]):
                            dead_bases.append( (base_index, group) )
                            break

            if self.remove_bases(base_loc, dead_bases):
                needs_refresh = 1

        # 2nd pass: Maintenance, clear finished techs.
        for base_loc in g.bases:
            dead_bases = []
            for base_index in range(len(g.bases[base_loc])):
                base = g.bases[base_loc][base_index]
                if base.done:
                    #maintenance
                    self.cash -= base.type.maintenance[0]
                    if self.cash < 0:
                        self.cash = 0
                        #Chance of base destruction if cash-unmaintained: 1.5%
                        if g.roll_percent(150):
                            dead_bases.append( (base_index, "maint") )

                    self.cpu_for_day -= base.type.maintenance[1]
                    if self.cpu_for_day < 0:
                        self.cpu_for_day = 0
                        #Chance of base destruction if cpu-unmaintained: 1.5%
                        if g.roll_percent(150):
                            dead_bases.append( (base_index, "maint") )
                if base.studying == "": continue
                if base.studying == "Construction": continue
                if g.jobs.has_key(base.studying): continue
                # Remove completed tech.
                if g.techs[base.studying].done == 1:
                    base.studying = ""
        return needs_refresh

    def remove_bases(self, base_loc, dead_bases):
        needs_refresh = 0
        # Reverse dead_bases to simplify deletion.
        for base, reason in dead_bases[::-1]:
            base_name = g.bases[base_loc][base].name

            if reason == "maint":
                dialog_string = (g.strings["discover_maint0"]+" "+
                    g.bases[base_loc][base].name+" "+
                    g.strings["discover_maint1"])

            elif reason in self.groups:
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
            g.bases[base_loc].pop(base)
            needs_refresh = 1
            g.base.renumber_bases(g.bases[base_loc])

        return needs_refresh

    def lost_game(self):
        for group in self.groups.values():
            if group.suspicion > 10000:
                # Someone discovered me.
                return 2

        # The [] can be removed in Python 2.4.
        if sum([len(base_list) for base_list in g.bases.values()]) == 0:
            # My last base got discovered.
            return 1

        # Still Alive.
        return 0

    #returns the amount of cash available after taking into account all
    #current projects in construction.
    def future_cash(self):
        result_cash = self.cash
        techs = {}
        for base_loc in g.bases:
            for base in g.bases[base_loc]:
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
