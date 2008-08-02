#file: listbox.py
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

#This file contains the listbox widget.

import pygame

import constants
import g
import widget
import text
import scrollbar

class Listbox(widget.FocusWidget, text.SelectableText):
    list = widget.causes_rebuild("_list")
    list_pos = widget.causes_rebuild("_list_pos")
    list_size = widget.causes_rebuild("_list_size")

    def __init__(self, parent, pos, size, anchor, list = None, list_pos = 0,
                 list_size = -20, borders = constants.ALL, **kwargs):
        super(Listbox, self).__init__(parent, pos, size, anchor = anchor,
                                      **kwargs)
        
        self.list = list or []
        self.display_elements = []
        self.borders = borders

        self.list_size = list_size
        self.list_pos = list_pos

        self.auto_scroll = True
        self.scrollbar = scrollbar.UpdateScrollbar(self, 
                                                   update_func = self.on_scroll)

    def add_hooks(self):
        super(Listbox, self).add_hooks()
        self.parent.add_handler(constants.CLICK, self.on_click, 150)
        self.parent.add_key_handler(pygame.K_UP, self.got_key)
        self.parent.add_key_handler(pygame.K_DOWN, self.got_key)
        self.parent.add_key_handler(pygame.K_PAGEUP, self.got_key)
        self.parent.add_key_handler(pygame.K_PAGEDOWN, self.got_key)

    def remove_hooks(self):
        super(Listbox, self).remove_hooks()
        self.parent.remove_handler(constants.CLICK, self.on_click)
        self.parent.remove_key_handler(pygame.K_UP, self.got_key)
        self.parent.remove_key_handler(pygame.K_DOWN, self.got_key)
        self.parent.remove_key_handler(pygame.K_PAGEUP, self.got_key)
        self.parent.remove_key_handler(pygame.K_PAGEDOWN, self.got_key)

    def on_scroll(self, scroll_pos):
        self.needs_rebuild = True

    def on_click(self, event):
        if self.collision_rect.collidepoint(event.pos):
            self.has_focus = True
            self.took_focus(self)
            
            # Figure out which element was clicked...
            local_vert_abs = event.pos[1] - self.collision_rect[1]
            local_vert_pos = local_vert_abs / float(self.collision_rect.height)
            index = int(local_vert_pos * len(self.display_elements))

            # ... and select it.
            self.list_pos = index + self.scrollbar.scroll_pos

    def safe_pos(self, raw_pos):
        return max(0, min(len(self.list) - 1, raw_pos))

    def got_key(self, event):
        if not self.has_focus:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                new_pos = self.list_pos - 1
            elif event.key == pygame.K_DOWN:
                new_pos = self.list_pos + 1
            elif event.key == pygame.K_PAGEUP:
                new_pos = self.list_pos - (self.scrollbar.window - 1)
            elif event.key == pygame.K_PAGEDOWN:
                new_pos = self.list_pos + (self.scrollbar.window - 1)
            else:
                return

            self.list_pos = self.safe_pos(new_pos)
            self.scrollbar.scroll_to(self.list_pos)
            raise constants.Handled

    def remake_elements(self):
        # If self.list_size is negative, we interpret it as a minimum height
        # for each element and calculate the number of elements to show.
        list_size = self.list_size
        if list_size < 0:
            min_height = -list_size
            list_size = max(1, self._make_collision_rect().height // min_height)
        
        # Remove the old ones.
        for child in self.display_elements:
            self.children.remove(child)

        # Create the new ones.
        self.display_elements = []
        for i in range(list_size):
            element = text.SelectableText(self, None, None,
                                          anchor = constants.TOP_LEFT,
                                          borders = (constants.TOP,
                                                     constants.LEFT),
                                          border_color = self.border_color,
                                          selected_color = self.selected_color,
                                          unselected_color =
                                                          self.unselected_color)
            self.display_elements.append(element)

        self.display_elements[-1].borders = (constants.TOP, constants.LEFT,
                                             constants.BOTTOM)

        # Move the scrollbar to the end so that it gets drawn on top.
        self.children.remove(self.scrollbar)
        self.children.append(self.scrollbar)

    def rebuild(self):
        super(Listbox, self).rebuild()

        self.remake_elements()

        window_size = len(self.display_elements)
        list_size = len(self.list)

        self.scrollbar.window = window_size
        self.scrollbar.elements = list_size

        if self.auto_scroll:
            self.auto_scroll = False
            self.scrollbar.center(self.list_pos)

        offset = self.scrollbar.scroll_pos
        for index, element in enumerate(self.display_elements):
            list_index = index + offset

            # Position and size the element.
            element.pos = (0, -index / float(window_size))
            element.size = (-.9, -1 / float(window_size))

            # Set up the element contents.
            element.selected = (list_index == self.list_pos)
            if list_index < list_size:
                element.text = self.list[list_index]
            else:
                element.text = ""


class UpdateListbox(Listbox):
    def _on_selection_change(self):
        self.update_func(self.list_pos)

    _list_pos = widget.call_on_change("__list_pos", _on_selection_change)

    def __init__(self, *args, **kwargs):
        self.update_func = kwargs.pop("update_func", lambda value: None)
        super(UpdateListbox, self).__init__(*args, **kwargs)
