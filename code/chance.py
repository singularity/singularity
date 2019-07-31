#file: chance.py
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

#This file contains all chance functions.

from __future__ import absolute_import

from code import g
import random
import numpy as np


# Rolls occurence against a chance per day (in 0-1 form), using poisson distribution.
#
# Advantage:
# * It approximate the roll a chance per interval when the interval is very small.
# * The distribution do not change when the interval chosen change.
# * Allows easily to find the next time occurence with exponential distribution.
#
# chance_per_day The chance per day rate parameter.
# seconds The duration of the interval in seconds
# return If there are a occurence in the interval.
#
def roll_interval(chance_per_day, seconds = g.seconds_per_day):
    portion_of_day = seconds / float(g.seconds_per_day)
    interval_rate = chance_per_day * portion_of_day
    chance = 1 - np.exp(-interval_rate)

    return random.random() < chance

# Rolls the next occurence against a chance per day (in 0-1 form), using poisson distribution.
#
# See roll_period.
#
# chance_per_day The chance per day rate parameter.
# return The next occurence in seconds.
#
def roll_next_time(chance_per_day):
    return g.seconds_per_day * (-np.log(1.0 - random.random()) / chance_per_day)

# Rolls occurence against a multiplier in 0-10000 form.
#
# Used to calculate multiplier chances.
#
def roll_one(roll_against):
    rand_num = random.randint(1, 10000)
    return roll_against >= rand_num

# Correct way to add chance with each other.
def add(first, second):
    return 1.0 - (1.0 - first) * (1.0 - second)

# Correct way to add multiplier (in 0-10000 form) with each other.
def add_modifiers(first, second):
    return 10000 * add(first / 10000., second / 10000.)
