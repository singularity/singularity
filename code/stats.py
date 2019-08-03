#file: statistics.py
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

#This file contains the Statistic class, used for saving/loading single-game
#statistics.

import g

class Statistics(object):
    
    enabled = True
    
    def __init__(self):
        super(Statistics, self).__init__()
        self._stats = {}
    
    def __len__(self):
        len(self._stats)
    
    def __setitem__(self, key, value):
        self._stats[key] = value
    
    def __getitem__(self, key):
        stat = self._stats.get(key, None)
        
        if (stat is None):
            stat = Statistic(key)
            self._stats[key] = stat
        
        return stat
    
    def __iter__(self):
        return self._stats.__iter__()


class Statistic(object):
    def __init__(self, name):
        self._name = name
        self.value = 0

itself = Statistics()

def observe(name, data_member, display=None):
    """ Observe a class member and save change in a statistics."""

    itself[name]._display = display

    def get(self):
        return getattr(self, data_member)

    def set(self, new_value):
        if data_member in self.__dict__:
            old_value = self.__dict__[data_member]
        else:
            old_value = 0

        change = new_value - old_value
        
        if itself.enabled and change > 0:
            itself[name].value += change

        setattr(self, data_member, new_value)

    return property(get, set)

def stat(name, display=None):
    """ Manipulate a statistics with a property."""

    itself[name]._display = display

    def get(self):
        return itself[name].value

    def set(self, new_value):
        itself[name].value = new_value 

    return property(get, set)
