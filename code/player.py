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
        self.alter_suspicion(max(quadratic_down, 1))

    def alter_suspicion(self, change):
        self.suspicion = max(self.suspicion - change, 0)

    def alter_suspicion_decay(self, change):
        self.suspicion_decay = max(self.suspicion_decay - change, 0)

    def alter_discover_bonus(self, change):
        self.discover_bonus = max(self.discover_bonus - change, 0)

    def discovered_a_base(self):
        self.alter_suspicion(1000)

class player_class(object):
    def __init__(self, cash, time_sec=0, time_min=0, time_hour=0, time_day=0):
        self.cash = cash
        self.time_sec = time_sec
        self.time_min = time_min
        self.time_hour = time_hour
        self.time_day = time_day
        self.interest_rate = 1
        self.income = 0
        self.cpu_for_day = 0
        self.labor_bonus = 10000
        self.job_bonus = 10000
        self.groups = {"news":    group("news",    suspicion_decay = 150),
                       "science": group("science", suspicion_decay = 100),
                       "covert":  group("covert",  suspicion_decay =  50),
                       "public":  group("public",  suspicion_decay = 200)}

    def give_time(self, time_sec):
        needs_refresh = 0
        store_last_minute = self.time_min
        store_last_day = self.time_day
        time_min = 0
        time_hour = 0
        time_day = 0
        self.time_sec += time_sec
        if self.time_sec >= 60:
            time_min += self.time_sec / 60
            self.time_sec = self.time_sec % 60
        self.time_min += time_min
        if self.time_min >= 60:
            time_hour += self.time_min / 60
            self.time_min = self.time_min % 60
        self.time_hour += time_hour
        if self.time_hour >= 24:
            time_day += self.time_hour / 24
            self.time_hour = self.time_hour % 24
        self.time_day += time_day

        if time_min > 0:
            for base_loc in g.bases:
                for base in g.bases[base_loc]:
                    #Construction of new bases:
                    if base.built == 0:
                        tmp_base_time = (base.cost[2] * self.labor_bonus) /10000
                        if tmp_base_time == 0:
                            money_towards = base.cost[0]
                            cpu_towards = base.cost[1]
                            if cpu_towards > self.cpu_for_day:
                                cpu_towards = self.cpu_for_day
                        else:
                            money_towards = (time_min*base.cost[0]) / \
                            (tmp_base_time)
                            if money_towards > base.cost[0]:
                                money_towards = base.cost[0]
                            cpu_towards = (time_min*base.cost[1]) / \
                            (tmp_base_time)
                            if cpu_towards > base.cost[1]:
                                cpu_towards = base.cost[1]
                            if cpu_towards > self.cpu_for_day:
                                cpu_towards = self.cpu_for_day
                        if money_towards <= self.cash:
                            self.cash -= money_towards
                            self.cpu_for_day -= cpu_towards
                            built_base = base.study((money_towards,
                                        cpu_towards, time_min))
                            if built_base == 1:
                                needs_refresh = 1
                                g.create_dialog(g.strings["construction0"]+" "+
                                    base.name+" "+g.strings["construction1"],
                                    g.font[0][18], (g.screen_size[0]/2 - 100, 50),
                                    (200, 200), g.colors["dark_blue"],
                                    g.colors["white"], g.colors["white"])
                                g.curr_speed = 1
                    else:
                        #Construction of items:
                        tmp = 0
                        first_build_count = 0
                        for item in base.usage:
                            if not item: continue
                            if item.built == 1:
                                first_build_count += 1
                            tmp = item.work_on(time_min) or tmp
                        if tmp == 1:
                            #Check if ALL CPUs are built, stay silent until then.
                            #Using build count and first_build count to check
                            #against CPUs at start of day and end of day.
                            #If the total goes from 0 to any amount over 0,
                            #it will trigger a new dialog, completed first batch.
                            build_complete = 1
                            build_count = 0
                            for item_index in base.usage:
                                if item_index.built == 0:
                                    build_complete = 0
                                    continue
                                build_count += 1
                            if build_complete == 1:
                                needs_refresh = 1
                                g.create_dialog(g.strings["construction0"]+" "+
                                    item.item_type.name+" "+
                                    g.strings["item_construction1"]+" "+
                                    base.name+".",
                                    g.font[0][18], (g.screen_size[0]/2 - 100, 50),
                                    (200, 200), g.colors["dark_blue"],
                                    g.colors["white"], g.colors["white"])
                                g.curr_speed = 1
                            elif first_build_count == 0 and build_count > 0:
                                needs_refresh = 1
                                g.create_dialog(g.strings["construction0"]+" "+
                                    item.item_type.name+" "+
                                    g.strings["item_construction2"]+" "+
                                    base.name+".",
                                    g.font[0][18], (g.screen_size[0]/2 - 100, 50),
                                    (200, 200), g.colors["dark_blue"],
                                    g.colors["white"], g.colors["white"])
                        for item in base.extra_items:
                            if not item: continue
                            tmp = item.work_on(time_min)
                            if tmp == 1:
                                needs_refresh = 1
                                g.create_dialog(g.strings["construction0"]+" "+
                                    item.item_type.name+" "+
                                    g.strings["item_construction1"]+" "+
                                    base.name+".",
                                    g.font[0][18], (g.screen_size[0]/2 - 100, 50),
                                    (200, 200), g.colors["dark_blue"],
                                    g.colors["white"], g.colors["white"])
                                g.curr_speed = 1


        for i in range(self.time_day - store_last_day):
            needs_refresh = self.new_day() or needs_refresh

        return needs_refresh

    #Run every day at midnight.
    def new_day(self):
        needs_refresh = 0
        event = {}
        #interest and income.
        self.cash += (self.interest_rate * self.cash) / 10000
        self.cash += self.income

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
        if self.time_day == 23:
            g.create_dialog(g.strings["grace_warning"],
                g.font[0][18], (g.screen_size[0]/2 - 100, 50),
                (200, 200), g.colors["dark_blue"],
                g.colors["white"], g.colors["white"])
            needs_refresh = 1
            g.curr_speed = 1

        for base_loc in g.bases:
            dead_bases = []
            for base_index in range(len(g.bases[base_loc])):
                base = g.bases[base_loc][base_index]
                #Does base get detected?
                #Give a grace period.
                if self.time_day - base.built_date > base.base_type.cost[2]*2:
                    if self.time_day > 23:
                        detect_chance = base.get_detect_chance()
                        if g.debug == 1:
                            print "Chance of discovery for base %s: %s" % \
                                (base.name, repr(detect_chance))
                        for group in detect_chance:
                            if g.roll_percent(detect_chance[group]) == 1:
                                dead_bases.append( (base_index, group) )
                                break

                if base.built == 1:
                    #study
                    if base.studying == "":
                        self.cpu_for_day += base.processor_time()
                        continue
                    if base.studying == "Construction":
                        pass #FIXME: Finish Construction Research
                        continue
                    #jobs:
                    if g.jobs.has_key(base.studying):
                        self.cash += (g.jobs[base.studying][0]*
                                    base.processor_time())
                        #TECH
                        if g.techs["Advanced Simulacra"].known == 1:
                            #10% bonus income
                            self.cash += (g.jobs[base.studying][0]*
                                    base.processor_time())/10

                        continue
                    #tech aready known. This should occur when multiple
                    #bases are studying the same tech.
                    if g.techs[base.studying].known == 1:
                        base.studying = ""
                        self.cpu_for_day += base.processor_time()
                        continue
                    #Actually study.
                    if g.techs[base.studying].cost[1] == 0:
                        money_towards = g.techs[base.studying].cost[0]
                        tmp_base_time = 0
                    else:
                        tmp_base_time = base.processor_time()
                        money_towards = (tmp_base_time*
                        g.techs[base.studying].cost[0])/ \
                        (g.techs[base.studying].cost[1])
                        if money_towards > g.techs[base.studying].cost[0]:
                            money_towards=g.techs[base.studying].cost[0]
                    if money_towards <= self.cash:
                        if g.debug == 1:
                            print "Studying "+base.studying +": "+ \
                            str(money_towards)+" Money, "+str(tmp_base_time)+" CPU"
                        self.cash -= money_towards
                        learn_tech = g.techs[base.studying].study(
                            (money_towards, tmp_base_time, 0))
                        if learn_tech == 1:
                            needs_refresh = 1
                            g.create_dialog(g.strings["tech_construction0"]+" "+
                                g.techs[base.studying].name+" "+
                                g.strings["construction1"]+" "+
                                g.techs[base.studying].result,
                                g.font[0][18], (g.screen_size[0]/2 - 100, 50),
                                (200, 200), g.colors["dark_blue"],
                                g.colors["white"], g.colors["white"])
                            base.studying = ""
                            g.curr_speed = 1
                    elif g.debug == 1:
                        print "NOT Studying "+base.studying +": "+ \
                        str(money_towards)+"/"+str(self.cash)+" Money"
            if self.remove_bases(base_loc, dead_bases):
                needs_refresh = 1
        #I need to recheck after going through all bases as research
        #worked on by multiple bases doesn't get erased properly otherwise.
        for base_loc in g.bases:
            dead_bases = []
            loc_in_array = -1
            for base in g.bases[base_loc]:
                loc_in_array += 1
                if base.built == 1:
                    #maintenance
                    self.cash -= base.base_type.mainten[0]
                    if self.cash < 0:
                        self.cash = 0
                        #Chance of base destruction if unmaintained:
                        if g.roll_percent(150) == 1:
                            dead_bases.append( (loc_in_array, "maint") )

                    self.cpu_for_day -= base.base_type.mainten[1]
                    if self.cpu_for_day < 0:
                        self.cpu_for_day = 0
                        #Chance of base destruction if unmaintained:
                        if g.roll_percent(150) == 1:
                            dead_bases.append( (loc_in_array, "maint") )
                if base.studying == "": continue
                if base.studying == "Construction": continue #FIXME: Finish
                if g.jobs.has_key(base.studying): continue
                if g.techs[base.studying].known == 1:
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

                dialog_string = (g.strings["discover0"] + " "+base_name+" " +
                    g.strings["discover1"]+" "+detect_phrase)
            else:
                print "Error: base destoyed for unknown reason: " + reason
                dialog_string = (g.strings["discover0"] + " "+base_name+" " +
                    g.strings["discover1"] + " ???.")

            g.create_dialog(dialog_string, g.font[0][18],
                (g.screen_size[0]/2 - 100, 50), (200, 200),
                g.colors["dark_blue"], g.colors["white"], g.colors["red"])
            g.curr_speed = 1
            g.bases[base_loc].pop(base)
            needs_refresh = 1
            g.base.renumber_bases(g.bases[base_loc])

        return needs_refresh

    def increase_suspicion(self, amount):
        raise Exception, "DEPRECATED increase_suspicion called."

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
        tmp_techs = {}
        for base_loc in g.bases:
            for base in g.bases[base_loc]:
                result_cash -= base.cost[0]
                if g.techs.has_key(base.studying):
                    if not tmp_techs.has_key(base.studying):
                        result_cash -= g.techs[base.studying].cost[0]
                        tmp_techs[base.studying] = 1
                for item in base.usage:
                    if item: result_cash -= item.cost[0]
                for item in base.extra_items:
                    if item: result_cash -= item.cost[0]
        return result_cash
