#file: item.py
#Copyright (C) 2005,2006,2008 Evil Mr Henry, Phil Bordelon, and FunnyMan3595
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

#This file contains the item class.

from __future__ import absolute_import

from singularity.code import g, buyable
from singularity.code.stats import stat
from singularity.code.spec import GenericSpec, SpecDataField, validate_must_be_list, promote_to_list


class ItemType(GenericSpec):

    spec_type = 'item_type'
    spec_data_fields = [
        SpecDataField('is_extra', data_field_name='is_extra', converter=lambda v:bool(int(v))),
    ]

    """ Item type """
    def __init__(self, id, is_extra, **kwargs):

        self.id       = id
        self.is_extra = is_extra

        self.text = ""

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        # Updates language-dependent data
        try:
            hotkey = g.hotkey(value)
        except AttributeError:
            # g.hotkey() wasn't declared yet, mimic its defaults
            hotkey = dict(text= value,
                          key = value[0:1],
                          pos = 0,)
        self._text  = value
        self.label  = hotkey['text'] # "Friendly" name for screens and buttons
        self.hotkey = hotkey['key']  # Hotkey char
        self.pos    = hotkey['pos']  # Hotkey index in Label

    def __repr__(self):
        return self.id

def all_types():
    for item_type in item_types.values():
        yield item_type

def convert_item_types(raw_value):
    try:
        item_type = item_types[raw_value]
    except KeyError:  # pragma: no cover
        raise ValueError("Unknown item type %s, please use one of: %s" % (raw_value, ", ".join(item_types)))
    return item_type

def convert_item_qualities(raw_value):
    validate_must_be_list(raw_value)

    if len(raw_value) % 2 == 1:
        raise ValueError("item quality list must have pair elements, got %d (value: %s)"
                         % (len(raw_value), repr(raw_value)))

    # Create a dict from the list with impair as string key and pair as integer value
    return {key: int(value) for key, value in zip(*[iter(raw_value)]*2)}

class ItemSpec(buyable.BuyableSpec):
    """ Item as a buyable item """

    spec_type = 'item'
    created = stat(spec_type + "_created")
    spec_data_fields = [
        buyable.SPEC_FIELD_COST,
        buyable.SPEC_FIELD_PREREQUISITES,
        SpecDataField('item_type', data_field_name='type', converter=convert_item_types),
        SpecDataField('qualities', data_field_name='quality', converter=convert_item_qualities),
        SpecDataField('buildable', data_field_name='build', converter=promote_to_list, default_value=list),
    ]

    def __init__(self, id, cost, prerequisites, item_type, qualities, buildable):
        super(ItemSpec, self).__init__(id, cost, prerequisites)

        self.item_type = item_type
        self.item_qual = qualities

        self.regions = buildable

    def get_info(self):
        basic_text = super(ItemSpec, self).get_info()
        if self.has_quality_for("cpu"):
            cpu = self.get_quality_for("cpu")
            return basic_text.replace("---", _("Generates {0} CPU.".format(
                                               g.add_commas(cpu))) + \
                                      "\n---")
        return basic_text

    def get_total_cost_info(self, count):
        total_cost = self.cost * count
        total_cost_str = self.describe_cost(total_cost, hide_time=True)
        return _("Total Cost: %(total_cost)s") % {"total_cost": total_cost_str}

    def has_quality_for(self, quality):
        return quality in self.item_qual

    def get_quality_for(self, quality):
        return self.item_qual.get(quality, 0)

    def get_quality_info(self, if_installed_in_base=None, count=1):
        bonus_text = ""

        for qual, value in self.item_qual.items():
            if qual == "cpu":
                if if_installed_in_base is not None:
                    value = max(1, int(value * if_installed_in_base.compute_bonus // 10000))
                bonus_text += _("CPU per day:")+" "
                bonus_text += g.add_commas(value * count)
            elif qual == "cpu_modifier":
                bonus_text += _("CPU bonus:")+" "
                bonus_text += g.to_percent(value)
            elif qual == "discover_modifier":
                bonus_text += _("Detection chance reduction:")+" "
                bonus_text += g.to_percent(value)
            else:
                continue
            bonus_text += "\n"

        return bonus_text

class Item(buyable.Buyable):
    """ An installed Item in a Player's Base """

    def __init__(self, item_spec, base=None, count=1):
        super(Item, self).__init__(item_spec, count)
        self.base = base

    def serialize_obj(self):
        return self.serialize_buyable_fields({
            'id': g.to_internal_id('item', self.spec.id),
        })

    @classmethod
    def deserialize_obj(cls, base, obj_data, game_version):
        spec_id = g.convert_internal_id('item', obj_data.get('id', None) or obj_data['spec_id'])
        spec = g.items[spec_id]
        count = obj_data.get('count', 1)
        obj = Item(spec, base, count=count)
        obj.restore_buyable_fields(obj_data, game_version)
        return obj

    def convert_from(self, load_version):
        if load_version < 4.91: # < r5_pre
            self.type = g.items[self.type.id]
        if load_version < 99.4:
            self.type.item_type = item_types[self.type.item_type]
        super(Item, self).convert_from(load_version)

    def get_quality_for(self, quality):
        item_qual = self.spec.get_quality_for(quality)

        # Modifiers are not affected by count.
        # TODO: Allow modifiers to be multiplied by count. Need a custom function.
        if quality.endswith("_modifier"):
            return item_qual

        return item_qual * self.count

    def finish(self, is_player=True, loading_savegame=False):
        super(Item, self).finish(is_player=is_player, loading_savegame=loading_savegame)
        if self.base:
            self.base.recalc_cpu()
            self.base.check_power()

    def __iadd__(self, other):
        if isinstance(other, Item) and self.base == other.base \
                and self.spec == other.spec:
            if other.count == 0:
                return self

            # Calculate what's been paid and what is left to be paid.
            total_cost_paid = self.cost_paid + other.cost_paid
            self.total_cost += other.total_cost

            # Labor takes as long as the less complete item would need.
            total_cost_paid[buyable.labor] = min(self.cost_paid[buyable.labor],
                                                 other.cost_paid[buyable.labor])
            self.total_cost[buyable.labor] = other.total_cost[buyable.labor]

            # Set what we've paid (and hence what we have left to pay).
            self.cost_paid = total_cost_paid

            # Increase the size of this stack.
            self.count += other.count

            # Tell the base it has no CPU for now.
            self.base.raw_cpu = 0

            # See if we're done or not.
            self.done = False
            self.work_on(0, 0, 0)

            return self
        else:
            return NotImplemented
