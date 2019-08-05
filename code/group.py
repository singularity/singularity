#file: group.py
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

#This file contains the group class, a group of person which can suspect the singularity.

from __future__ import absolute_import

from code import g
from code.spec import GenericSpec, SpecDataField


class GroupSpec(GenericSpec):

    spec_data_fields = [
        SpecDataField('suspicion_decay', converter=int, default_value=100)
    ]

    def __init__(self, id, suspicion_decay):
        super(GroupSpec, self).__init__(id)
        self.suspicion_decay = suspicion_decay
        self.discover_suspicion = 1000
        
        # String data
        self.name = ""
        self.discover_desc = ""


class Group(object):

    def __init__(self, spec, diff):
        self.spec = spec
        self.suspicion = 0
        self.changed_suspicion_decay = 0
        self.base_discover_bonus = diff.discover_multiplier
        self.changed_discover_bonus = 0
        self.base_discover_suspicion = diff.suspicion_multiplier
        self.changed_discover_suspicion = 0
        self.is_actively_discovering_bases = True

    def convert_from(self, old_version):
        if old_version < 99.6: # < 1.0 dev
            self.spec = GroupSpec(
                self.__dict__['id'], 
                self.__dict__['suspicion_decay'])
            del self.__dict__['id'], self.__dict__['name'], self.__dict__['suspicion_decay']
            
            self.__dict__['base_discover_bonus'] = self.__dict__['discover_bonus']
            del self.__dict__['discover_bonus']
        if old_version < 99.7: # < 1.0 dev
            self.spec = self.type
            del self.type

    @property
    def name(self):
        return self.spec.name

    @property
    def suspicion_decay(self):
        return max(1, self.spec.suspicion_decay + self.changed_suspicion_decay)

    @property
    def discover_bonus(self):
        if not self.is_actively_discovering_bases:
            return 0
        return max(1, self.base_discover_bonus + self.changed_discover_bonus)

    @property
    def discover_suspicion(self):
        return max(1, (self.spec.discover_suspicion * (self.base_discover_suspicion + self.changed_discover_suspicion)) // 10000)

    @property
    def decay_rate(self):
        # Suspicion reduction is now quadratic.  You get a certain percentage
        # reduction, or a base .01% reduction, whichever is better.
        return max(1, (self.suspicion * self.suspicion_decay) // 10000)

    def new_day(self):
        self.alter_suspicion(-self.decay_rate)

    def alter_suspicion(self, change):
        self.suspicion = max(self.suspicion + change, 0)

    def alter_suspicion_decay(self, change):
        self.changed_suspicion_decay += change

    def alter_discover_bonus(self, change):
        self.changed_discover_bonus += change

    def alter_discover_suspicion(self, change):
        self.changed_discover_suspicion += change

    def discovered_a_base(self):
        self.alter_suspicion(self.discover_suspicion)

    # percent_to_danger_level takes a suspicion level and returns an int in range(5)
    # that represents whether it is low, moderate, high, or critically high.
    def suspicion_to_danger_level(self):
        if self.suspicion < 2500:
            return 0
        elif self.suspicion < 5000:
            return 1
        elif self.suspicion < 7500:
            return 2
        else:
            return 3

    # percent_to_detect_str takes a percent and renders it to a short (four
    # characters or less) string representing whether it is low, moderate, high,
    # or critically high.
    def suspicion_to_detect_str(self):
        return g.danger_level_to_detect_str(self.suspicion_to_danger_level())

    def detects_per_day_to_danger_level(self, detects_per_day):
        raw_suspicion_per_day = detects_per_day * self.discover_suspicion
        suspicion_per_day = raw_suspicion_per_day - self.decay_rate

        # +1%/day or death within 10 days
        if suspicion_per_day > 100 \
           or (self.suspicion + suspicion_per_day * 10) >= 10000:
            return 3
        # +0.5%/day or death within 100 days
        elif suspicion_per_day > 50 \
           or (self.suspicion + suspicion_per_day * 100) >= 10000:
            return 2
        # Suspicion increasing.
        elif suspicion_per_day > 0:
            return 1
        # Suspicion steady or decreasing.
        else:
            return 0
