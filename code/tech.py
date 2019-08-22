#file: tech.py
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

#This file contains the tech class.

from __future__ import absolute_import

from code import buyable, effect, g
from code.stats import stat
from code.spec import SpecDataField, spec_field_effect


TECH_RESET_EVENT = []
TECH_RESEARCH_EVENT = []


def register_on_tech_reset_handler(func):
    TECH_RESET_EVENT.append(func)
    return func


def register_on_tech_researched_handler(func):
    TECH_RESEARCH_EVENT.append(func)
    return func


def tech_reinitialized():
    for handler in TECH_RESET_EVENT:
        handler()


class TechSpec(buyable.BuyableSpec):
    spec_type = 'tech'
    created = stat(spec_type + "_created")
    spec_data_fields = [
        buyable.SPEC_FIELD_COST,
        buyable.SPEC_FIELD_PREREQUISITES,
        SpecDataField('danger', converter=int, default_value=0),
        spec_field_effect(mandatory=False),
    ]

    def __init__(self, id, cost, prerequisites, danger,
                 effect_data):
        super(TechSpec, self).__init__(id, cost, prerequisites)

        self.result = ""
        self.danger = danger
        self.effect = effect.Effect(self, effect_data)


class Tech(buyable.Buyable):

    def __init__(self, spec):
        super(Tech, self).__init__(spec)

    def __lt__(self, other):
        if not isinstance(other, Tech):
            return True
        else:
            return self.spec.id < other.spec.id

    @property
    def result(self):
        return self.spec.result

    @property
    def danger(self):
        return self.spec.danger

    def get_info(self):
        cost = self.spec.describe_cost(self.total_cost, True)
        left = self.spec.describe_cost(self.cost_left, True)
        return ("%s\n%s: %s\n%s: %s\n---\n%s" %
                (self.name,
                 _("Total cost"), cost,
                 _("Cost left"), left,
                 self.description))

    def finish(self, is_player=True, loading_savegame=False):
        super(Tech, self).finish(is_player=is_player, loading_savegame=loading_savegame)
        self.spec.effect.trigger(loading_savegame=loading_savegame)
        if not loading_savegame:
            for handler in TECH_RESEARCH_EVENT:
                handler(self)

    def serialize_obj(self):
        return self.serialize_buyable_fields({
            'id': self.spec.id,
        })

    @classmethod
    def deserialize_obj(cls, obj_data, game_version):
        from code import savegame
        spec_id = savegame.convert_id('tech', obj_data['id'] , game_version)
        spec = g.techs[spec_id]
        tech = Tech(spec)

        tech.restore_buyable_fields(obj_data, game_version)
        return tech
