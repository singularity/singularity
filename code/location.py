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

import g
import prerequisite
from buyable import cash, cpu, labor


class LocationSpec(prerequisite.Prerequisite):

    # The hotkey used to open this location (loaded dynamically from locations_str.dat)
    hotkey = ""

    # The names of cities/places in the location (loaded dynamically from locations_str.dat)
    cities = []

    def __init__(self, id, position, absolute, safety, prerequisites):
        super(LocationSpec, self).__init__(prerequisites)
        self.id = id

        self.x, self.y = position[0] / -100., position[1] / -100.
        self.absolute = absolute
        self.safety = safety
        self.modifiers = {}


DEAD_LOCATION_SPEC = LocationSpec('<unknown>', (0, 0), False, 0, 'impossible')


class Location(object):

    def __init__(self, location_spec):
        self.spec = location_spec

        # A list of the bases at this location.  Often sorted for the GUI.
        self.bases = []
        # The bonuses and penalties of this location.
        # - NB: We got a static set of modifiers (see LocationSpec) and a dynamic one
        #       (which occurs e.g. for the common locations on Earth, where the modifiers
        #        are randomized)
        self._modifiers = {}

    def convert_from(self, old_version):
        if old_version < 99.7: # < 1.0 dev
            spec_id = self.__dict__['id']
            # Default to None if absent (so the LocationSpec's version is used)
            self.__dict__['_modifiers'] = self.__dict__['modifiers'] if self.__dict__.get('modifiers') else None
            # The following locations had a static modifier list at the time of 99.8.  Clear their modifier
            # dict, so the LocationSpec's version is used instead.
            if spec_id in {'ANTARCTIC', 'OCEAN', 'MOON', 'ORBIT', 'FAR REACHES'}:
                self.__dict__['modifiers'] = None

            # Remove old fields
            for field in ('id', 'name', 'x', 'y', 'absolute', 'safety', 'cities', 'modifiers', 'hotkey'):
                del self.__dict__[field]
        else:
            # >= 99.7; the LocationSpec is present on the object itself
            spec_id = self.spec.id

        # Force reload the spec for now until #145 is fully implemented
        if spec_id not in g.locations:
            # We are referencing an unknown location; mark us as dead.
            self.spec = DEAD_LOCATION_SPEC
            return
        self.spec = g.locations[spec_id]

    @property
    def id(self):
        return self.spec.id

    @property
    def name(self):
        return self.spec.id

    def available(self):
        return self.spec.available()

    @property
    def x(self):
        return self.spec.x

    @property
    def y(self):
        return self.spec.y

    @property
    def absolute(self):
        return self.spec.absolute

    @property
    def safety(self):
        return self.spec.safety

    @property
    def cities(self):
        return self.spec.cities

    @property
    def hotkey(self):
        return self.spec.hotkey

    @property
    def modifiers(self):
        if self._modifiers is None:
            return self.spec.modifiers
        return self._modifiers

    @modifiers.setter
    def modifiers(self, value):
        self._modifiers = value

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

    def modify_maintenance(self, maintenance):
        if "thrift" in self.modifiers:
            mod = self.modifiers["thrift"]

            # Invert it and apply to the cash maintenance.  CPU is not changed.
            maintenance[cash] = int(maintenance[cash] / mod)

    def add_base(self, base):
        self.bases.append(base)
        base.location = self

        self.modify_cost(base.total_cost)
        self.modify_cost(base.cost_left)
        self.modify_maintenance(base.maintenance)

        # Make sure the location's CPU modifier is applied.
        base.recalc_cpu()

    def __eq__(self, other):
        if self is other:
            return True
        if other is None or not isinstance(other, self.__class__):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __cmp__(self, other):
        return cmp(self.id, other.id)
