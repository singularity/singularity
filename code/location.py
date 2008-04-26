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

import g

class Location(object):
    def __init__(self, id, position, safety, prerequisites):
        # .name should be changed by load_location_defs, but we initialize it
        # just in case.
        self.id = self.name = id 
        self.y, self.x = position
        self.safety = safety
        self.prerequisites = prerequisites

    def open(self):
        for prerequisite in self.prerequisites:
            if not g.techs[prerequisite].done:
                return False
        return True
