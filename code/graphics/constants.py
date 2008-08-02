#file: constants.py
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

#This file contains GUI constants.

# Anchor positions.
TOP, MID, BOTTOM = range(3)
LEFT, CENTER, RIGHT = range(3,6)
TOP_LEFT = (TOP, LEFT)
TOP_CENTER = (TOP, CENTER)
TOP_RIGHT = (TOP, RIGHT)
MID_LEFT = (MID, LEFT)
MID_CENTER = (MID, CENTER)
MID_RIGHT = (MID, RIGHT)
BOTTOM_LEFT = (BOTTOM, LEFT)
BOTTOM_CENTER = (BOTTOM, CENTER)
BOTTOM_RIGHT = (BOTTOM, RIGHT)


# Used when an unambiguous "No Result" return is required.  (None may have a
# meaning.)

class _NoResult(object):
    def __eq__(self, other):
        return type(self) == type(other)
    def __ne__(self, other):
        return type(self) != type(other)

NO_RESULT = _NoResult()


# Handler types.
KEY, KEYDOWN, KEYUP, CLICK, MOUSEMOTION, DRAG = range(6)


# Handler "errors", used to throw a return value up several levels.
class Handled(Exception): pass
class ExitDialog(Exception): pass
