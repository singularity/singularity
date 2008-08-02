#file: button.py
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

#This file contains the Button class.

import pygame

import constants
import g
import widget
import text

class Button(text.Text):
    select_color = widget.causes_rebuild("_select_color")
    hotkey = widget.causes_rebuild("_hotkey")
    force_underline = widget.causes_rebuild("_force_underline")
    selected = widget.causes_rebuild("_selected")

    # A second layer of property wraps .hotkey, to update key handlers.
    __hotkey = ""
    def _on_set_hotkey(self, value):
        if self.parent and value != self.__hotkey:
            if self.__hotkey:
                self.parent.remove_key_handler(self.__hotkey, self.handle_event)
            if value:
                self.parent.add_key_handler(value, self.handle_event)
        self.__hotkey = value

    _hotkey = property(lambda self: self.__hotkey, _on_set_hotkey)

    def __init__(self, parent, pos, size = (0, -.05),
                 anchor = constants.TOP_LEFT, text = "", base_font = None,
                 color = None, borders=(0,2,3,5), border_color = None,
                 unselected_color = None, selected_color = None,
                 hotkey = "", force_underline = None):
        super(Button, self).__init__(parent, pos, size, anchor,
                                     text, base_font, color, borders)

        self.border_color = border_color or g.colors["white"]
        self.selected_color = selected_color or g.colors["light_blue"]
        self.unselected_color = unselected_color or g.colors["dark_blue"]
        self.hotkey = hotkey
        self.force_underline = force_underline

        self.selected = False

        if self.parent:
            self.parent.add_handler(constants.MOUSEMOTION, self.handle_event)
            self.parent.add_handler(constants.CLICK, self.handle_event)
            if self.hotkey:
                self.parent.add_key_handler(self.hotkey, self.handle_event)

    def rebuild(self):
        if self.selected:
            self.background_color = self.selected_color
        else:
            self.background_color = self.unselected_color
        self.calc_underline()
        super(Button, self).rebuild()

    def calc_underline(self):
        if self.force_underline != None:
            self.underline = self.force_underline
        elif self.hotkey and self.hotkey in self.text:
            self.underline = self.text.index(self.hotkey)
        else:
            self.underline = -1

    def is_over(self, position):
        pos = self.abs_pos
        if position == (0,0): # Special case, for when the mouse hasn't been
            return False      # initialized properly yet.
        elif position[0] < pos[0] or position[1] < pos[1]:
            return False # Above/left of the button
        elif position[0] >= pos[0] + self.real_size[0]:
            return False # Right of the button.
        elif position[1] >= pos[1] + self.real_size[1]:
            return False # Below the button.
        else:
            return True # Right on the button

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.selected = self.is_over(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.is_over(event.pos):
                self.activated()
        elif event.type == pygame.KEYDOWN:
            if event.unicode == self.hotkey:
                self.activated()

    def activated(self):
        """Called when the button is pressed or otherwise triggered."""
        raise constants.ExitDialog
