#file: base.py
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

#This file contains the base class.

from __future__ import division

from functools import reduce

from singularity.code import g, chance, item, buyable
from singularity.code.buyable import cpu
from singularity.code.stats import stat

from singularity.code.spec import SpecDataField, promote_to_list, validate_must_be_list

from numpy import int64

#TODO: Use this list and convert Base.power_state to a property to enforce this
#TODO: Consider converting to dict, so it can have colors and names and modifiers
#      (Base.power_state would need to be a property, with setter and getter)
#This list only applies to 'Base' class, not 'BaseClass'
#Changes to this list should also be reflected in Base.power_state_name property

power_states = ['active','sleep']
#power_states.extend(['overclocked','suicide','stasis','entering_stasis','leaving_stasis'])


def parse_detect_chance(parsed_value):
    validate_must_be_list(parsed_value)
    chance_dict = {}

    for chance_str in parsed_value:
        key, value = chance_str.split(":")
        chance_dict[key] = int(value)

    return chance_dict


class BaseSpec(buyable.BuyableSpec):
    """Base as a buyable item (New Base in Location menu)"""

    spec_type = 'base'
    created = stat(spec_type + "_created")
    spec_data_fields = [
        SpecDataField('size', converter=int),
        SpecDataField('force_cpu', default_value=None),
        SpecDataField('regions', data_field_name='allowed', converter=promote_to_list),
        SpecDataField('detect_chance', converter=parse_detect_chance),
        buyable.SPEC_FIELD_COST,
        buyable.SPEC_FIELD_PREREQUISITES,
        SpecDataField('danger', converter=int, default_value=0),
        SpecDataField('maintenance', data_field_name='maint', converter=buyable.spec_parse_cost),
    ]

    def __init__(self, id, size, force_cpu, regions,
                 detect_chance, cost, prerequisites, maintenance):
        super(BaseSpec, self).__init__(id, cost, prerequisites)
        self.size = size
        self.force_cpu = force_cpu
        self.regions = regions

        self.detect_chance = detect_chance
        self.maintenance = maintenance
        self.flavor = []

    def calc_discovery_chance(self, extra_factor = 1):
        # Get the default settings for this base type.
        detect_chance = self.detect_chance.copy()

        # Adjust by the current suspicion levels ...
        for group in detect_chance:
            suspicion = g.pl.groups[group].suspicion
            detect_chance[group] *= 10000 + suspicion
            detect_chance[group] //= 10000

        # ... and further adjust based on technology ...
        for group in detect_chance:
            discover_bonus = g.pl.groups[group].discover_bonus
            detect_chance[group] *= discover_bonus
            detect_chance[group] //= 10000

        # ... and the given factor.
        for group in detect_chance:
            detect_chance[group] = int(detect_chance[group] * extra_factor)

        return detect_chance

    def get_detect_info(self, location=None):

        detect_modifier = 1 / location.modifiers.get("stealth", 1) if location else 1
        chance = self.calc_discovery_chance(detect_modifier)

        return get_detect_info(chance)

    def get_info(self, location):
        raw_cost = self.cost[:]
        location.modify_cost(raw_cost)
        cost = self.describe_cost(raw_cost)

        raw_maintenance = self.maintenance[:]
        location.modify_maintenance(raw_maintenance)
        # describe_cost() expects CPU-seconds, not CPU-days
        raw_maintenance[cpu] *= g.seconds_per_day
        maint = self.describe_cost(raw_maintenance, True)

        detect = self.get_detect_info(location)

        size = ""
        if self.size > 1:
            size = "\n" + _("Has space for %d computers.") % self.size

        location_message = ""
        if location.has_modifiers():
            location_message = "---\n\n" + _("Location modifiers: {MODIFIERS}", 
                                           MODIFIERS=location.get_modifiers_info())

        template = "%s\n" + _("Build cost:").replace(" ",u"\xA0") + u"\xA0%s\n" + \
                   _("Maintenance:") + u"\xA0%s\n%s%s\n---\n%s\n%s"
        return template % (self.name, cost, maint, detect, size, self.description, location_message)

class Base(buyable.Buyable):
    """A Player's Base in a Location (Open Base in Location menu)"""

    def __init__(self, name, spec, built=False):
        super(Base, self).__init__(spec)

        self.name = name
        self.started_at = g.pl.raw_min

        self.location = None

        self.raw_cpu = 0
        self.cpu = 0

        self.items = {
            "cpu": None,
            "reactor": None,
            "network": None,
            "security": None,
        }

        if self.spec.force_cpu:
            self.cpus = item.Item(g.items[self.spec.force_cpu],
                                  base=self, count=self.spec.size)
            self.cpus.finish(is_player=False)

        if built:
            self.finish(is_player=False)

        self._power_state = "active"
        self.grace_over = False

        self.maintenance = buyable.array(self.spec.maintenance, int64)

    @property
    def cpus(self):
        return self.items.get("cpu", None)

    @cpus.setter
    def cpus(self, value):
        self.items["cpu"] = value

    @property
    def maintains_singularity(self):
        """Whether the singularity can be sustained by this base"""
        if not self.done or not self.cpus or self.cpus.count < 1 or not self.cpus.done:
            # Incomplete bases or bases without any active CPUs cannot keep the singularity
            # alive
            return False
        return True

    @property
    def power_state(self):
        return self._power_state

    @power_state.setter
    def power_state(self, value):
        self._power_state = value
        self.check_power()
        g.pl.recalc_cpu()

    @property
    def power_state_name(self):
        """A read-only i18'zable version of power_state attribute, suitable for
        printing labels, captions, etc"""
        if self.power_state == "active"         : return _("Active")
        if self.power_state == "sleep"          : return _("Sleep")
        if self.power_state == "overclocked"    : return _("Overclocked")
        if self.power_state == "suicide"        : return _("Suicide")
        if self.power_state == "stasis"         : return _("Stasis")
        if self.power_state == "entering_stasis": return _("Entering Stasis")
        if self.power_state == "leaving_stasis" : return _("Leaving Stasis")
        return ""

    def space_left_for(self, item_type):
        space_left = self.spec.size

        # Different cpus will replace the previous one, so these take full space.
        if self.cpus is not None \
                and self.cpus.spec == item_type:
            space_left -= self.cpus.count
            
        return space_left

    def check_power(self):
        if self.power_state == "sleep":
            if self.done:
                for item in self.all_items():
                    if item is not None and not item.done:
                        self.power_state = "active"
            else:
                self.power_state = "active"

    def recalc_cpu(self):
        self.raw_cpu = self.get_quality_for("cpu")

        if self.raw_cpu == 0:
            self.cpu = 0
            return

        compute_bonus = 10000

        # Item bonus
        compute_bonus += self.get_quality_for("cpu_modifier")

        # Location modifier
        if self.location and "cpu" in self.location.modifiers:
            compute_bonus = compute_bonus * self.location.modifiers["cpu"]

        self.cpu = max(1, int(self.raw_cpu * compute_bonus // 10000))

    def serialize_obj(self):
        return self.serialize_buyable_fields({
            'id': g.to_internal_id('base', self.spec.id),
            'name': self.name,
            'started_at_min': self.started_at,
            'power_state': self.power_state,
            'grace_over': self.grace_over,
            # Note that we store all items even for "force_cpu"'ed bases.  This enables
            # use to load the base with that CPU item even if the "force_cpu" flag is
            # later removed from the spec.
            'items': [it.serialize_obj() for it in self.items.values() if it is not None],
        })

    @classmethod
    def deserialize_obj(cls, obj_data, game_version):
        spec_id = g.convert_internal_id('base', obj_data.get('id', None) or obj_data['spec_id'])
        spec = g.base_type[spec_id]
        name = obj_data.get('name')
        base = Base(name, spec)
        
        base.restore_buyable_fields(obj_data, game_version)

        if not base.spec.force_cpu:
            item_data_list = obj_data['items']
            for item_data in item_data_list:
                it = item.Item.deserialize_obj(base, item_data, game_version)
                base.items[it.spec.item_type.id] = it

        base.started_at = obj_data['started_at_min']
        base.grace_over = obj_data.get('grace_over', True)
        # Note that power_state is subject to whether the base and items are built,
        # so we deliberately restore it late.
        #
        # IMPORTANT: Avoid changing base.power_state as it triggers a "recalc_cpu"
        # for the player.  As not we might not have restored everything this either
        # breaks or makes recalc_cpu throw away all allocations as most of the CPU
        # power is missing at this stage.
        stored_power_state = obj_data['power_state']
        if stored_power_state in power_states:
            base._power_state = stored_power_state
        else:
            # Unknown power states revert to "active" except for the historical "statis"
            # states (which are reverted to "sleep")
            base._power_state = 'sleep' if stored_power_state in ('statis', 'entering_stasis') else 'active'
        base.check_power()
        return base

    # Get the detection chance for the base, applying bonuses as needed.  If
    # accurate is False, we just return the value to the nearest full
    # percent.
    def get_detect_chance(self, accurate = True):
        # Get the base chance from the universal function.
        detect_chance = calc_base_discovery_chance(self.spec.id)

        for group in g.pl.groups:
            detect_chance.setdefault(group, 0)

        # Factor in any items built with discover_bonus ...
        base_qual = self.get_quality_for("discover_modifier")
        for group in detect_chance:
            detect_chance[group] *= 10000 - base_qual
            detect_chance[group] //= 10000

        # ... and its location ...
        if self.location:
            multiplier = self.location.discovery_bonus()
            for group in detect_chance:
                detect_chance[group] *= multiplier
                detect_chance[group] //= 100

        # ... and its power state.
        if self.done and self.power_state == "sleep":
            for group in detect_chance:
                detect_chance[group] //= 4

        # Lastly, if we're not returning the accurate values, adjust
        # to the nearest percent.
        if not accurate:
            for group in detect_chance:
                detect_chance[group] = g.nearest_percent(detect_chance[group])

        return detect_chance

    def get_quality_for(self, quality):
        gen = (item.get_quality_for(quality) for item in self.all_items()
                                             if item and item.done)
        
        if quality.endswith("_modifier"):
            # Use add_chance to sum modifier.
            return reduce(chance.add, (qual / 10000 for qual in gen), 0) * 10000
        else:
            return sum(gen)

    def is_empty(self):
        for item in self.all_items():
            if item: return False
        return True

    def is_building(self):
        for item in self.all_items():
            if item and not item.done:
                return True
        return False
        
    def is_building_extra(self):
        for item in self.all_items():
            if item and item.spec.item_type.is_extra and not item.done:
                return True
        return False

    def has_grace(self):
        if self.grace_over:
            return False

        age = g.pl.raw_min - self.started_at
        grace_time = (self.total_cost[buyable.labor] * g.pl.base_grace_multiplier) / 10000
        if age > grace_time:
            self.grace_over = True
            return False
        else:
            return True

    def destroy(self):
        super(Base, self).destroy()

        if self.location:
            self.location.bases.remove(self)

        for item in self.all_items():
            if item is not None:
                item.destroy()

        g.pl.recalc_cpu()

    def next_base(self, forwards):
        index = self.location.bases.index(self)
        if forwards > 0:
            increment = 1
        else:
            increment = -1

        while True:
            index += increment
            index %= len(self.location.bases)
            base = self.location.bases[index]
            if base.done:
                return base

    def sort_tuple(self):
        # We sort based on size (descending), CPU (descending),
        # then name (ascending).
        # id(self) is thrown in at the end to make sure identical-looking
        # bases aren't considered equal.
        return (-self.spec.size, -self.cpu, self.name, id(self))

    def __lt__(self, other):
        if isinstance(other, Base):
            return self.sort_tuple() < other.sort_tuple()
        else:
            return True

    def all_items(self):
        for item in self.items.values():
            if item: yield item

    def get_detect_info(self):
        accurate = (g.pl.display_discover == "full")
        chance = self.get_detect_chance(accurate)
        
        return get_detect_info(chance)
        

# calc_base_discovery_chance is a globally-accessible function that can
# calculate basic discovery chances given a particular class of base.
def calc_base_discovery_chance(base_type_name,
                               extra_factor = 1):
    return g.base_type[base_type_name].calc_discovery_chance(extra_factor)

def detect_chance_to_danger_level(detects_per_day):
    if detects_per_day > 225:
        return 3
    elif detects_per_day > 150:
        return 2
    elif detects_per_day > 75:
        return 1
    else:
        return 0

def get_detect_info(detect_chance):
    detect_template = _("Detection chance:") + "\n"
    chances = []
    
    for group in g.pl.groups.values():
        detect_template += group.name + u":\xA0%s\n"
        chances.append(detect_chance.get(group.spec.id, 0))

    if g.pl.display_discover == "full":
        return detect_template % tuple(g.to_percent(c) for c in chances)
    elif g.pl.display_discover == "partial":                                 
        return detect_template % tuple(g.to_percent(g.nearest_percent(c, 25)) for c in chances)                               
    else:              
        return detect_template % tuple(g.danger_level_to_detect_str(detect_chance_to_danger_level(c)) 
                                       for c in chances)

