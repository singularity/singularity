#file: location.py
#Copyright (C) 2005,2006 Evil Mr Henry and Phil Bordelon
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

import bisect
import g, buyable

# Location is a subclass of Buyable_Class so that it can use .available():
class Location(buyable.Buyable_Class):
    def __init__(self, id, position, safety, prerequisites):
        # Kinda hackish, but it works.
        super(Location, self).__init__(id, "", (0,0,0), prerequisites)

        self.y, self.x = position
        self.safety = safety
        self.cities = []
        self.hotkey = ""

        self.bases = []

    had_last_discovery = property(lambda self: g.pl.last_discovery == self)
    had_prev_discovery = property(lambda self: g.pl.prev_discovery == self)

    def discovery_bonus(self):
        discovery_bonus = 1
        if self.had_last_discovery:
            discovery_bonus *= 1.2
        if self.had_prev_discovery:
            discovery_bonus *= 1.1
        return int(discovery_bonus * 100)

    def add_base(self, base):
        where = bisect.bisect(self.bases, base)
        self.bases.insert(where, base)
        base.location = self

        if len(self.bases) == 1:
           # The rest wouldn't cause any harm... but it also wouldn't do 
           # anything.
           return

        # Will correctly wrap to -1.
        prev = self.bases[where-1]
        prev.next = base
        base.prev = prev
        if where < len(self.bases)-1:
            next = self.bases[where+1]
        else:
            next = self.bases[0]
        next.prev = base
        base.next = next

    def __hash__(self):
        return hash(self.id)

    def __cmp__(self, other):
        if type(other) in (str, unicode):
            return cmp(self.id, other)
        else:
            return cmp(self.id, other.id)
