# file: region.py
# Copyright (C) 2008 FunnyMan3595
# This file is part of Endgame: Singularity.

# Endgame: Singularity is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# Endgame: Singularity is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Endgame: Singularity; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

# This file contains the Region class.

import random
from singularity import g


class RegionSpec(object):
    def __init__(self, id, modifiers_list):
        self.id = id
        self.modifiers_list = modifiers_list
        self.locations = []


class Region(object):
    def __init__(self, spec, loading_savegame=False):
        self.spec = spec
        self.modifier_by_location = {}
        self._modifier_entry_by_location = {}

        if not loading_savegame:
            modifiers_entry_list = list(range(len(self.spec.locations)))
            self._assign_modifiers(modifiers_entry_list, self.spec.locations)

    def _assign_modifiers(self, entry_list, location_id_list, shuffle_entry_list=True):
        modifiers_list = self.spec.modifiers_list
        if shuffle_entry_list:
            random.shuffle(entry_list)
        for entry_id, loc in zip(entry_list, location_id_list):
            self._modifier_entry_by_location[loc] = entry_id
            # There can be more locations than modifiers (e.g. URBAN has 6 locations but
            # 5 modifiers)
            if entry_id < len(modifiers_list):
                self.modifier_by_location[loc] = modifiers_list[entry_id]
            else:
                self.modifier_by_location[loc] = {}

    def serialize_obj(self):
        return {
            "id": g.to_internal_id("region", self.spec.id),
            # We only store the modifier entry per location as we can trivially get the
            # most recent modifier from that.
            "modifier_entry_by_location": [
                {
                    "loc_id": k,
                    "modifier_entry": v,
                }
                for k, v in self._modifier_entry_by_location.items()
            ],
        }

    @classmethod
    def deserialize_obj(cls, obj_data, game_version):
        spec_id = g.convert_internal_id("region", obj_data["id"])
        spec = g.regions[spec_id]
        region = Region(spec, loading_savegame=True)
        modifiers_list = spec.modifiers_list
        region_locations = frozenset(spec.locations)
        used_entries = set()

        # Load and assign existing entries - data quality permitting
        for modifier_data in obj_data["modifier_entry_by_location"]:
            loc_id = g.convert_internal_id("location", modifier_data["loc_id"])
            if loc_id not in region_locations:
                # Location is no longer in this Region
                continue

            modifier_entry = modifier_data.get("modifier_entry")

            # Check for corrupt data
            assert (
                modifier_entry is not None
                and modifier_entry >= 0
                and modifier_entry not in used_entries
            )

            used_entries.add(modifier_entry)
            region._modifier_entry_by_location[loc_id] = modifier_entry
            if modifier_entry < len(modifiers_list):
                region.modifier_by_location[loc_id] = modifiers_list[modifier_entry]
            else:
                region.modifier_by_location[loc_id] = {}

        # Handle new locations being added to the region after the savegame was made.
        new_locations = [
            loc_id
            for loc_id in region_locations
            if loc_id not in region._modifier_entry_by_location
        ]
        missing_entries = [
            entry for entry in range(len(region_locations)) if entry not in used_entries
        ]
        assert len(missing_entries) == len(new_locations)
        region._assign_modifiers(missing_entries, new_locations)

        return region

    @classmethod
    def guess_region_data_in_old_savegame(cls, serialized_location_data, game_version):
        # Prior to 1.0 (beta1), there was only one region (URBAN) and we can mostly
        # recreate it by looking at the location modifiers.
        # Only these 6 locations were in the URBAN region prior to 1.0 (beta1)
        urban_location_ids = {
            "N AMERICA",
            "S AMERICA",
            "EUROPE",
            "ASIA",
            "AFRICA",
            "AUSTRALIA",
        }
        modifier_entry_by_location = []
        # We use this set to ensure a modifier is only given once; the deserialize_obj method
        # checks for it.
        remaining_mods = {
            1,  # Mod 1: CPU bonus, stealth malus
            2,  # Mod 2: Stealth bonus, CPU malus
            3,  # Mod 3: Thrift bonus, speed malus
            4,  # Mod 4: Speed bonus, thrift malus
            5,  # Mod 5: CPU bonus, thrift malus
        }

        for loc_data in serialized_location_data:
            raw_loc_id = loc_data["id"]
            loc_id = g.convert_internal_id("location", raw_loc_id)
            if loc_id not in urban_location_ids:
                continue
            modifier = loc_data.get("_modifiers")
            if not modifier:
                continue
            cpu_mod = modifier.get("cpu", 1)
            thrift_mod = modifier.get("thrift", 1)
            # Actual bonuses were 1.2 and maluses were 0.83 - we use 1.05 and 0.95 here
            # because it is sufficient to detect whether it was a bonus or malus without
            # having to worry about floating point rounding errors.
            if cpu_mod < 0.95:
                # Mod 2 (Stealth bonus, CPU malus)
                modifier_entry = 2
            elif cpu_mod > 1.05:
                # Either 1 or 5
                modifier_entry = 5 if thrift_mod < 0.95 else 1
            else:
                # Either 3 or 4
                modifier_entry = 3 if thrift_mod > 1.05 else 4

            if modifier_entry in remaining_mods:
                remaining_mods.discard(modifier_entry)
                modifier_entry_by_location.append(
                    {
                        "loc_id": raw_loc_id,
                        "modifier_entry": modifier_entry - 1,
                    }
                )
            # else:
            #   Do nothing - the region deserialization will assign them a random
            #   entry

        # Finally, generate what the serialized data should have looked like
        return [
            {
                "id": g.to_internal_id("region", "URBAN"),
                "modifier_entry_by_location": modifier_entry_by_location,
            }
        ]
