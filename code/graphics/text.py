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

#given a surface, string, font, char to underline (int; -1 to len(string)),
#xy coord, and color, print the string to the surface.
#Align (0=left, 1=Center, 2=Right) changes the alignment of the text
def print_string(surface, string_to_print, font, underline_char, xy, color, align=0):
    if align != 0:
        size = font.size(string_to_print)
        if align == 1: xy = (xy[0] - size[0]/2, xy[1])
        elif align == 2: xy = (xy[0] - size[0], xy[1])
    if underline_char == -1 or underline_char >= len(string_to_print):
        text = font.render(string_to_print, 1, color)
        surface.blit(text, xy)
    else:
        text = font.render(string_to_print[:underline_char], 1, color)
        surface.blit(text, xy)
        size = font.size(string_to_print[:underline_char])
        xy = (xy[0] + size[0], xy[1])
        font.set_underline(1)
        text = font.render(string_to_print[underline_char], 1, color)
        surface.blit(text, xy)
        font.set_underline(0)
        size = font.size(string_to_print[underline_char])
        xy = (xy[0] + size[0], xy[1])
        text = font.render(string_to_print[underline_char+1:], 1, color)
        surface.blit(text, xy)

class Text(widget.BorderedWidget):
    text = widget.causes_rebuild("_text")
    base_font = widget.causes_rebuild("_base_font")
    color = widget.causes_rebuild("_color")
    shrink_factor = widget.causes_rebuild("_shrink_factor")
    underline = widget.causes_rebuild("_underline")

    def __init__(self, parent, pos, size = (0, -.05), 
                 anchor = constants.TOP_LEFT, text = "", base_font = None,
                 color = None, shrink_factor = 1, underline = -1, **kwargs):
        super(Text, self).__init__(parent, pos, size, anchor, **kwargs)
        
        self.text = text
        self.base_font = base_font or g.font[0]
        self.color = color or g.colors["white"]
        self.shrink_factor = shrink_factor
        self.underline = underline

    def pick_font(self, height = 0):
        if height:
            # Run a binary search for the correct height font.
            # Thanks to bisect.bisect_left for the basic implementation.
            left = 8
            right = len(self.base_font)

            while left + 1 < right:
                test_me = (left + right) // 2

                #if self.base_font[test_me].size("")[1] > height:
                if self.base_font[test_me].get_linesize() > height:
                    right = test_me
                else:
                    left = test_me

            self._font = self.base_font[left]

        return self._font

    font = property(pick_font)

    def _calc_size(self):
        base_size = list(super(Text, self)._calc_size())

        # Calculate the font height.
        vert_borders = (constants.TOP in self.borders) \
                       + (constants.BOTTOM in self.borders)
        vert_offset = vert_borders + 2
        height = int( (base_size[1] - vert_offset) * self.shrink_factor )

        # Pick a font based on that height.
        font = self.pick_font(height)

        # If the width is unspecified, calculate it from the font and text.
        if base_size[0] == 0:
            horiz_borders = (constants.LEFT in self.borders) \
                            + (constants.RIGHT in self.borders)
            horiz_offset = horiz_borders + 2
            base_size[0] = font.size(self.text)[0] + horiz_offset
        return tuple(base_size)

    def rebuild(self):
        super(Text, self).rebuild()

        text_size = self.font.size(self.text)
        hgap = ( self.real_size[0] - text_size[0] ) // 2
        vgap = ( self.real_size[1] - text_size[1] ) // 2

        # Print the text itself
        print_string(self.internal_surface, self.text, self.font, 
                     self.underline, (hgap, vgap), self.color)


class SelectableText(Text):
    selected = widget.causes_rebuild("_selected")
    selected_color = widget.causes_rebuild("_selected_color")
    unselected_color = widget.causes_rebuild("_unselected_color")

    def __init__(self, parent, pos, size, border_color = None,
                 unselected_color = None, selected_color = None, **kwargs):
        super(SelectableText, self).__init__(parent, pos, size, **kwargs)

        self.border_color = border_color or g.colors["white"]
        self.selected_color = selected_color or g.colors["light_blue"]
        self.unselected_color = unselected_color or g.colors["dark_blue"]

        self.selected = False

    def rebuild(self):
        if self.selected:
            self.background_color = self.selected_color
        else:
            self.background_color = self.unselected_color
        super(SelectableText, self).rebuild()
