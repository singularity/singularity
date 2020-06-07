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

from __future__ import absolute_import

from singularity.code import g, prerequisite, base
from singularity.code.spec import GenericSpec, SpecDataField, validate_must_be_list, promote_to_list
from singularity.code.buyable import cash, cpu, labor, SPEC_FIELD_PREREQUISITES


def position_data_parser(raw_value):
    validate_must_be_list(raw_value)
    abs = False
    if len(raw_value) == 3:
        if raw_value[0] != 'absolute':
            raise ValueError('First element for a 3-element position data must be "absolute", got: %s' % raw_value[0])
        abs = True
        _, x, y = raw_value
    elif len(raw_value) == 2:
        x, y = raw_value
    else:
        raise ValueError("Location position data must be exactly 2 or 3 elements")
    return abs, int(x) / -100., int(y) / -100.


class LocationSpec(GenericSpec, prerequisite.Prerequisite):

    # The name of this location (loaded dynamically from locations_str.dat)
    name = ""

    # The hotkey used to open this location (loaded dynamically from locations_str.dat)
    hotkey = ""

    # The names of cities/places in the location (loaded dynamically from locations_str.dat)
    cities = []

    spec_data_fields = [
        SpecDataField('position_data', data_field_name="position", converter=position_data_parser),
        SpecDataField('safety', converter=int, default_value=0),
        SpecDataField('region', converter=promote_to_list, default_value=list),
        SpecDataField('modifier', converter=g.read_modifiers_dict, default_value=dict),
        SPEC_FIELD_PREREQUISITES,
    ]

    def __init__(self, id, position_data, safety, region, modifier, prerequisites):
        GenericSpec.__init__(self, id)
        prerequisite.Prerequisite.__init__(self, prerequisites)
        self.id = id

        self.absolute, self.x, self.y = position_data
        self.regions = region
        self.safety = safety
        self.modifiers = modifier


class Location(object):

    def __init__(self, location_spec, regions):
        self.spec = location_spec

        # A list of the bases at this location.  Often sorted for the GUI.
        self.bases = []
        self.regions = regions
        self._region_modifiers = None
        # The cache of the bonus and penalties combined for individual sources
        self._modifiers_cache = None

    @property
    def id(self):
        return self.spec.id

    @property
    def name(self):
        return self.spec.name

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

    @staticmethod
    def _merge_location_modifiers_inplace(current_modifier, *merge_list):
        for modifier_to_merge in merge_list:
            for mod_id, mod_value in modifier_to_merge.items():
                current_value = current_modifier.get(mod_id, 1)
                current_value *= mod_value
                current_modifier[mod_id] = current_value

    def _get_region_modifiers(self):
        if self._region_modifiers is None:
            self._region_modifiers = {}
            Location._merge_location_modifiers_inplace(self._region_modifiers,
                                                       *[r.modifier_by_location[self.id] for r in self.regions]
                                                       )
        return self._region_modifiers

    @property
    def modifiers(self):
        if self._modifiers_cache is None:
            self._modifiers_cache = {}
            region_modifiers = self._get_region_modifiers()
            Location._merge_location_modifiers_inplace(self._modifiers_cache,
                                                       region_modifiers,
                                                       self.spec.modifiers
                                                       )
        return self._modifiers_cache

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

            # Invert it and apply to the CPU/cash maintenance.
            maintenance[cash] = int(maintenance[cash] / mod)
            maintenance[cpu] = int(maintenance[cpu] / mod)

    def add_base(self, base):
        self.bases.append(base)
        base.location = self

        self.modify_base(base)

        # Make sure the location's CPU modifier is applied.
        base.recalc_cpu()

    def modify_base(self, base):
        self.modify_cost(base.total_cost)
        self.modify_cost(base.cost_left)
        self.modify_maintenance(base.maintenance)

    def has_modifiers(self):
        return len(self.modifiers) > 0

    def __eq__(self, other):
        if self is other:
            return True
        if other is None or not isinstance(other, self.__class__):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __lt__(self, other):
        return self.id < other.id

    def serialize_obj(self):
        obj_data = {
            'id': g.to_internal_id('location', self.spec.id),
            'bases': [b.serialize_obj() for b in self.bases],
        }
        return obj_data

    @classmethod
    def deserialize_obj(cls, obj_data, game_version):
        spec_id = g.convert_internal_id('location', obj_data['id'])
        spec = g.locations[spec_id]
        regions = [g.pl.regions[region_id] for region_id in spec.regions]
        loc = Location(spec, regions)

        loc.bases = []
        bases = obj_data.get('bases', [])
        for base_obj_data in bases:
            base_obj = base.Base.deserialize_obj(base_obj_data, game_version)
            loc.add_base(base_obj)
        return loc

    def get_modifiers_info(self):
        modifier_names = {
            "cpu"      : _("CPU"),
            "stealth"  : _("STEALTH"),
            "speed"    : _("BUILDING"),
            "thrift"   : _("COST"),
        }

        modifiers = []

        for modifier_id, modifier_value in self.modifiers.items():
            if (modifier_value > 1):
                modifiers.append(_("{MODIFIER} BONUS").format(MODIFIER=modifier_names[modifier_id]))
            elif (modifier_value < 1):
                modifiers.append(_("{MODIFIER} MALUS").format(MODIFIER=modifier_names[modifier_id]))

        return ", ".join(modifiers)
