#file: location.py
#Copyright (C) 2008 FunnyMan3595
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

#This file contains the Location class.

import bisect
import g
import buyable
from buyable import cash, cpu, labor

# Currently, each one gets a 20% bonus or its inverse, a 16.6% penalty.
# This will probably need to be adjusted later.
bonus_levels = dict(cpu = 1.2, stealth = 1.2, thrift = 1.2, speed = 1.2)
penalty_levels = dict((k,1/v) for k,v in bonus_levels.iteritems())

# Here are the six modifier pairs that get assigned at random on game start.
bonus, penalty = True, False
modifier_sets = [dict(     cpu = bonus, stealth = penalty ),
                 dict( stealth = bonus,     cpu = penalty ),
                 dict(  thrift = bonus,   speed = penalty ),
                 dict(   speed = bonus,  thrift = penalty ),
                 dict(     cpu = bonus,  thrift = penalty ),
                 dict(                                    ),]

# Translate the shorthand above into the actual bonuses/penalties.
for set in modifier_sets:
    for attribute, is_bonus in set.iteritems():
        if is_bonus:
            set[attribute] = bonus_levels[attribute]
        else:
            set[attribute] = penalty_levels[attribute]

# Location is a subclass of Buyable_Class so that it can use .available():
class Location(buyable.Buyable_Class):
    # The cities at this location.
    cities = []

    # The hotkey used to open this location.
    hotkey = ""

    # The bonuses and penalties of this location.
    modifiers = dict()

    def __init__(self, id, position, safety, prerequisites):
        # Kinda hackish, but it works.
        super(Location, self).__init__(id, "", (0,0,0), prerequisites)

        self.y, self.x = position
        self.safety = safety

        # A sorted list of the bases at this location.
        self.bases = []

    had_last_discovery = property(lambda self: g.pl.last_discovery == self)
    had_prev_discovery = property(lambda self: g.pl.prev_discovery == self)

    def discovery_bonus(self):
        discovery_bonus = 1
        if self.had_last_discovery:
            discovery_bonus *= 1.2
        if self.had_prev_discovery:
            discovery_bonus *= 1.1
        if "stealth" in self.modifiers:
            discovery_bonus /= self.modifiers["stealth"]
        return int(discovery_bonus * 100)

    def modify_cost(self, cost):
        if "thrift" in self.modifiers:
            mod = self.modifiers["thrift"]

            # Invert it and apply to the CPU/cash cost.
            cost[cash] = int(cost[cash] / mod)
            cost[cpu] = int(cost[cpu] / mod)

        if "speed" in self.modifiers:
            mod = self.modifiers["speed"]

            # Invert it and apply to the labor cost.
            cost[labor] = int(cost[labor] / mod)

    def add_base(self, base):
        # We keep self.bases sorted by inserting at the correct position, thanks
        # to bisect.
        where = bisect.bisect(self.bases, base)
        self.bases.insert(where, base)
        base.location = self

        self.modify_cost(base.total_cost)
        self.modify_cost(base.cost_left)
        if "thrift" in self.modifiers:
            mod = self.modifiers["thrift"]

            # And maintenance
            base.maintenance = (base.maintenance * mod).integer_part()

        if len(self.bases) == 1:
            # The rest wouldn't cause any harm... but it also wouldn't do 
            # anything.
            return

        # Update the linked list.
        # ...going backwards.
        prev = self.bases[where-1] # Will correctly wrap to -1.
        prev.next = base
        base.prev = prev

        # ... and going forwards.
        if where < len(self.bases)-1:
            next = self.bases[where+1]
        else:
            next = self.bases[0]
        next.prev = base
        base.next = next

    def __hash__(self):
        return hash(self.id)

    def __cmp__(self, other):
        if type(other) in (str, unicode):
            return cmp(self.id, other)
        else:
            return cmp(self.id, other.id)
