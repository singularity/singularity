from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from past.utils import old_div
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

import singularity.code.g
from . import buyable
from .buyable import cash, cpu, labor

# Currently, each one gets a 20% bonus or its inverse, a 16.6% penalty.
# This will probably need to be adjusted later.
bonus_levels = dict(cpu = 1.2, stealth = 1.2, thrift = 1.2, speed = 1.2)
penalty_levels = dict((k, old_div(1,v)) for k, v in bonus_levels.items())

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
    for attribute, is_bonus in set.items():
        if is_bonus:
            set[attribute] = bonus_levels[attribute]
        else:
            set[attribute] = penalty_levels[attribute]

# Location is a subclass of BuyableClass so that it can use .available():
class Location(buyable.BuyableClass):
    # The cities at this location.
    cities = []

    # The hotkey used to open this location.
    hotkey = ""

    # The bonuses and penalties of this location.
    modifiers = dict()

    def __init__(self, id, position, absolute, safety, prerequisites):
        # Kinda hackish, but it works.
        super(Location, self).__init__(id, "", (0, 0, 0), prerequisites)

        self.x, self.y = old_div(position[0], -100.), old_div(position[1], -100.)
        self.absolute = absolute
        self.safety = safety

        # A list of the bases at this location.  Often sorted for the GUI.
        self.bases = []

    had_last_discovery = property(lambda self: singularity.code.g.pl.last_discovery == self)
    had_prev_discovery = property(lambda self: singularity.code.g.pl.prev_discovery == self)

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
            cost[cash] = int(old_div(cost[cash], mod))
            cost[cpu] = int(old_div(cost[cpu], mod))

        if "speed" in self.modifiers:
            mod = self.modifiers["speed"]

            # Invert it and apply to the labor cost.
            cost[labor] = int(old_div(cost[labor], mod))


    def modify_maintenance(self, maintenance):
        if "thrift" in self.modifiers:
            mod = self.modifiers["thrift"]

            # Invert it and apply to the cash maintenance.  CPU is not changed.
            maintenance[cash] = int(old_div(maintenance[cash], mod))

    def add_base(self, base):
        self.bases.append(base)
        base.location = self

        self.modify_cost(base.total_cost)
        self.modify_cost(base.cost_left)
        self.modify_maintenance(base.maintenance)

        # Make sure the location's CPU modifier is applied.
        base.recalc_cpu()

    def __hash__(self):
        return hash(self.id)

    def __lt__(self, other):
        if isinstance(other, basestring):
            return self.id < other
        else:
            return self.id < other.id
