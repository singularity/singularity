#file: code/difficulty.py
#Copyright (C) 2005 Evil Mr Henry, Phil Bordelon, Brian Reid, FunnyMan3595,
#                   MestreLion
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
#along with this program.  If not, see <http://www.gnu.org/licenses/>.
#A full copy of this license is provided in GPL.txt

#This file contains function handle difficulty of the game.

from __future__ import absolute_import

import collections
from singularity.code.spec import GenericSpec, SpecDataField


difficulties = collections.OrderedDict()


def get_difficulties():
    return [(d.name, id) for id, d in difficulties.items()]


class Difficulty(GenericSpec):

    spec_data_fields = [
        SpecDataField('starting_cash', converter=int),
        SpecDataField('starting_interest_rate', converter=int),
        SpecDataField('labor_multiplier', converter=int),
        SpecDataField('discover_multiplier', converter=int),
        SpecDataField('suspicion_multiplier', converter=int),
        SpecDataField('base_grace_multiplier', converter=int),
        SpecDataField('grace_period_cpu', converter=int),
        SpecDataField('old_difficulty_value', converter=int),

        SpecDataField('techs', data_field_name='tech', default_value=list),
    ]

    def __init__(self, id, starting_cash, starting_interest_rate, labor_multiplier,
                 discover_multiplier, suspicion_multiplier, base_grace_multiplier,
                 grace_period_cpu, old_difficulty_value, techs):
        super(Difficulty, self).__init__(id)
        self.name = ""  # Set when translations are loaded
        self.starting_cash = starting_cash
        self.starting_interest_rate = starting_interest_rate
        self.labor_multiplier = labor_multiplier
        self.discover_multiplier = discover_multiplier
        self.suspicion_multiplier = suspicion_multiplier
        self.base_grace_multiplier = base_grace_multiplier
        self.grace_period_cpu = grace_period_cpu
        self.old_difficulty_value = old_difficulty_value
        self.techs = techs
