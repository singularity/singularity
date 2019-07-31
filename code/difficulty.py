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


difficulties = collections.OrderedDict()

columns = (
    'starting_cash', 
    'starting_interest_rate',
    'labor_multiplier',
    'discover_multiplier',
    'suspicion_multiplier',
    'base_grace_multiplier',
    'story_grace_difficulty',
    'grace_period_cpu'
)

list_columns = (
    ("tech", "techs"),
)

def get_difficulties():
    return [(d.name, id) for id, d in difficulties.iteritems()]

class Difficulty(object):
    pass
