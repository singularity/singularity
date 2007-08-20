#file: base.py
#Copyright (C) 2005,2006 Evil Mr Henry and Phil Bordelon
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

#This file contains the base class.


import pygame
import g

#cost = (money, ptime, labor)
#detection = (news, science, covert, person)
class base_type:
    def __init__(self, name, descript, size, regions, d_chance, cost,
                        prereq, mainten):
        self.base_id = name
        self.base_name = name
        self.descript = descript
        self.size = size
        self.regions = regions
        self.d_chance = d_chance
        self.cost = cost
        self.prereq = prereq
        self.mainten = mainten
        self.flavor = []
        self.count = 0

class base:
    def __init__(self, ID, name, base_type, built):
        self.ID = ID
        self.name = name
        self.base_type = base_type
        self.built = built
        self.built_date = g.pl.time_day
        self.studying = ""

        #Base suspicion is currently unused
        self.suspicion = (0, 0, 0, 0)
        self.usage = [0] * self.base_type.size
        if self.base_type.base_id == "Stolen Computer Time":
            self.usage[0] = g.item.item(g.items["PC"])
            self.usage[0].build()
        elif self.base_type.base_id == "Server Access":
            self.usage[0] = g.item.item(g.items["Server"])
            self.usage[0].build()
        elif self.base_type.base_id == "Time Capsule":
            self.usage[0] = g.item.item(g.items["PC"])
            self.usage[0].build()
        elif self.base_type.base_id == "Datacenter":
            self.usage[0] = g.item.item(g.items["Cluster"])
            self.usage[0].build()
        #Reactor, network, security.
        self.extra_items = [0] * 3

        self.cost = (0, 0, 0)
        if built == 0:
            self.cost = (base_type.cost[0], base_type.cost[1],
                                base_type.cost[2]*24*60)

    def study(self, cost_towards):
        if cost_towards[1] < 0 and g.debug == 1:
            print "WARNING: Got a negative cost_towards for CPU.  Something is deeply amiss."
        self.cost = (self.cost[0]-cost_towards[0], self.cost[1]-cost_towards[1],
                        self.cost[2]-cost_towards[2])
        if self.cost[0] <= 0: self.cost = (0, self.cost[1], self.cost[2])
        if self.cost[1] <= 0: self.cost = (self.cost[0], 0, self.cost[2])
        if self.cost[2] <= 0: self.cost = (self.cost[0], self.cost[1], 0)
        if self.cost == (0, 0, 0):
            self.built = 1
            #self.built_date = g.pl.time_day
            return 1
        return 0

    #Get detection chance for the base, applying bonuses as needed.
    def get_d_chance(self):

        # Get the base chance from the universal function.
        to_return = calc_base_discovery_chance(self.base_type.base_id)

        # Factor in the suspicion adjustments for this particular base ...
        to_return = ((to_return[0]*(10000+self.suspicion[0])/10000),
            (to_return[1]*(10000+self.suspicion[1])/10000),
            (to_return[2]*(10000+self.suspicion[2])/10000),
            (to_return[3]*(10000+self.suspicion[3])/10000))

        # ... any reactors built ... 
        if self.extra_items[0] != 0:
            if self.extra_items[0].built == 1:
                to_return = ((to_return[0]*3)/4,
                    (to_return[1]*3)/4,
                    (to_return[2]*3)/4,
                    (to_return[3]*3)/4)

        # ... and any security systems built.
        if self.extra_items[2] != 0:
            if self.extra_items[2].built == 1:
                to_return = (to_return[0]/2,
                    to_return[1]/2,
                    to_return[2]/2,
                    to_return[3]/2)

        return to_return

    #Return the number of units the given base has of a computer.
    def has_item(self):
        num_items = 0
        for item in self.usage:
            if item == 0: continue
            if item.built == 0: continue
            num_items += 1
        return num_items

    #Return how many units of CPU the base can contribute each day.
    def processor_time(self):
        comp_power = 0
        compute_bonus = 0
        for item in self.usage:
            if item == 0: continue
            if item.built == 0: continue
            comp_power += item.item_type.item_qual
        if self.extra_items[1] != 0:
            if self.extra_items[1].built == 1:
                compute_bonus = self.extra_items[1].item_type.item_qual
        return (comp_power * (10000+compute_bonus))/10000

    #For the given tech, return 1 if the base can study it, or 0 otherwise.
    def allow_study(self, tech_name):
        if self.built != 1: return 0
        if g.jobs.has_key(tech_name): return 1
        if g.techs[tech_name].danger == 0: return 1
        if g.techs[tech_name].danger == 1:
            for region in self.base_type.regions:
                if region == "OCEAN" or region == "MOON" or \
                        region == "FAR REACHES" or region == "TRANSDIMENSIONAL":
                    return 1
            return 0
        if g.techs[tech_name].danger == 2:
            for region in self.base_type.regions:
                if region == "MOON" or \
                        region == "FAR REACHES" or region == "TRANSDIMENSIONAL":
                    return 1
            return 0

        if g.techs[tech_name].danger == 3:
            for region in self.base_type.regions:
                if region == "FAR REACHES" or region == "TRANSDIMENSIONAL":
                    return 1
            return 0

        if g.techs[tech_name].danger == 4:
            for region in self.base_type.regions:
                if region == "TRANSDIMENSIONAL":
                    return 1
            return 0

#calc_base_discovery_chance: A globally-accessible function that can calculate
#basic discovery chances given a particular class of base.
def calc_base_discovery_chance(base_type_name):

    # Get the default settings for this base type.
    to_return = g.base_type[base_type_name].d_chance

    # Adjust by the current suspicion levels ...
    to_return = ((to_return[0]*(10000+g.pl.suspicion[0])/10000),
        (to_return[1]*(10000+g.pl.suspicion[1])/10000),
        (to_return[2]*(10000+g.pl.suspicion[2])/10000),
        (to_return[3]*(10000+g.pl.suspicion[3])/10000))

    # ... and further adjust based on technology.
    to_return = ((to_return[0]*g.pl.discover_bonus[0])/10000,
        (to_return[1]*g.pl.discover_bonus[1])/10000,
        (to_return[2]*g.pl.discover_bonus[2])/10000,
        (to_return[3]*g.pl.discover_bonus[3])/10000)

    return to_return

#When a base is removed, call to renumber the remaining bases properly.
def renumber_bases(base_array):
    for i in range(len(base_array)):
        base_array[i].ID = i

#When given a location like "ocean", determine if building there is allowed.
#Used to determine whether or not to display buttons on the map.
def allow_entry_to_loc(location):
    if g.bases.has_key(location):
        if location == "ANTARCTIC":
            #TECH (also, look below)
            if g.techs["Autonomous Vehicles"].known == 1 or \
                    g.techs["Advanced Database Manipulation"].known == 1: return 1
            return 0
        if location == "OCEAN":
            if g.techs["Autonomous Vehicles"].known == 1: return 1
            return 0
        if location == "MOON":
            if g.techs["Lunar Rocketry"].known == 1: return 1
            return 0
        if location == "FAR REACHES":
            if g.techs["Fusion Rocketry"].known == 1: return 1
            return 0
        if location == "TRANSDIMENSIONAL":
            if g.techs["Space-Time Manipulation"].known == 1: return 1
            return 0
        #By this point, only the "boring" locations are left.
        #Those are always buildable.
        return 1
    else:
        print "BUG: allow_entry_to_loc called with "+str(location)
        return 0

def destroy_base(location, index_num):
    if not g.bases.has_key(location):
        print "Bad location of "+str(location)+" given to destroy_base"
        return False
    if index_num < 0 or index_num >= len(g.bases[location]):
        print "Bad index of "+str(index_num)+" given to destroy_base"
        return False
    g.bases[location].pop(index_num)
    renumber_bases(g.bases[location])
    return True
