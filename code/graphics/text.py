#file: text.py
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

#This file contains the (non-editable) text widget AKA label.

import widget
import constants
import g

class Text(widget.Widget):
    text = widget.causes_rebuild("_text")

    def __init__(self, parent, pos, size = (0, -.05), 
                 anchor = constants.MID_CENTER, text = ""):
        super(Text, self).__init__(parent, pos, size, anchor)
        
        self.text = text

    def _calc_size(self):
        base_size = list(super(Text, self)._calc_size())
        if base_size[0] == 0:
            base_size[0] = 200 # TODO
        return tuple(base_size)

    def rebuild(self):
        super(Text, self).rebuild()
        g.print_string(self.internal_surface, self.text, g.font[0][20], -1, 
                       (0, 0), g.colors["green"])
