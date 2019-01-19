#file: prerequisite.py
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

#This file contains the Prequisite class.

import g

class Prerequisite(object):

    def __init__(self, prerequisites):
        self.prerequisites = prerequisites

    def available(self):
        or_mode = False
        assert type(self.prerequisites) == list
        for prerequisite in self.prerequisites:
            if prerequisite == "impossible":
                return False
            if prerequisite == "OR":
                or_mode = True
            if prerequisite in g.techs and g.techs[prerequisite].done:
                if or_mode:
                    return True
            else:
                if not or_mode:
                    return False
        # If we're not in OR mode, we met all our prerequisites.  If we are, we
        # didn't meet any of the OR prerequisites.
        return not or_mode
