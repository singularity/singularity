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
import widget
import text
import scrollbar

class Listbox(widget.FocusWidget, text.SelectableText):
    list = widget.causes_rebuild("_list")
    align = widget.causes_redraw("_align")
    list_size = widget.causes_rebuild("_list_size")
    list_pos = widget.causes_rebuild("_list_pos")

    def __init__(self, parent, pos, size, anchor=constants.TOP_LEFT, list=None,
                 list_pos=0, list_size=-20, borders=constants.ALL,
                 item_borders=True, item_selectable=True,
                 align=constants.CENTER, on_double_click_on_item=None, **kwargs):
        super(Listbox, self).__init__(parent, pos, size, anchor = anchor,
                                      **kwargs)

        self.display_elements = []
        self.borders = borders

        self.item_borders = item_borders
        self.item_selectable = item_selectable

        self.item_borders = item_borders
        self.align = align
        self.list_size = list_size
        self.list_pos = list_pos
        self.list = list or []

        self.auto_scroll = True
        if item_selectable:
            self.on_double_click_on_item = on_double_click_on_item
            self.add_handler(constants.DOUBLECLICK, self.on_double_click, 200)
        elif on_double_click_on_item:
            raise ValueError("The on_double_click_on_item handler only works for a listbox with selectable items")
        self.scrollbar = scrollbar.UpdateScrollbar(self,
                                                   update_func = self.on_scroll)

    def add_hooks(self):
        super(Listbox, self).add_hooks()
        if self.parent is not None:
            self.parent.add_handler(constants.CLICK, self.on_click, 90)
            self.parent.add_key_handler(pygame.K_UP, self.got_key)
            self.parent.add_key_handler(pygame.K_DOWN, self.got_key)
            self.parent.add_key_handler(pygame.K_PAGEUP, self.got_key)
            self.parent.add_key_handler(pygame.K_PAGEDOWN, self.got_key)

    def remove_hooks(self):
        super(Listbox, self).remove_hooks()
        if self.parent is not None:
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

            if (self.item_selectable):
                # Figure out which element was clicked...
                index = self.find_item_under_mouse(event)
                # ... and select it.
                self.list_pos = self.safe_pos(index + self.scrollbar.scroll_pos)

    def on_double_click(self, event):
        if self.on_double_click_on_item is None:
            return
        if self.collision_rect.collidepoint(event.pos) and self.item_selectable:
            index = self.find_item_under_mouse(event)
            if index > -1:
                self.on_double_click_on_item(event)

    def find_item_under_mouse(self, event):
        local_vert_abs = event.pos[1] - self.collision_rect[1]
        local_vert_pos = local_vert_abs / float(self.collision_rect.height)
        index = int(local_vert_pos * len(self.display_elements))
        if 0 <= index < len(self.list):
            return index
        return -1

    def safe_pos(self, raw_pos):
        return max(0, min(len(self.list) - 1, raw_pos))

    def got_key(self, event):
        if not self.has_focus or not self.item_selectable:
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


    def num_elements(self):
        # If self.list_size is negative, we interpret it as a minimum height
        # for each element and calculate the number of elements to show.
        list_size = self.list_size
        if list_size < 0:
            min_height = -list_size
            list_size = max(1, self._make_collision_rect().height // min_height)
        return list_size

    def remake_elements(self):
        list_size = self.num_elements()
        current_size = len(self.display_elements)

        if current_size > list_size:
            # Remove the excess ones.
            for child in self.display_elements[list_size:]:
                child.parent = None
            del self.display_elements[list_size:]
        elif current_size < list_size:
            if current_size > 0:
                if (self.item_borders):
                    self.display_elements[-1].borders = (constants.LEFT, constants.TOP)
                else:
                    self.display_elements[-1].borders = (constants.LEFT,)

            # Create the new ones.
            self.display_elements.extend([self.make_element() for _ in
                                          xrange(list_size - current_size)])

        if (self.item_borders):
            self.display_elements[-1].borders = (constants.TOP, constants.LEFT,
                                                 constants.BOTTOM)
        else:
            self.display_elements[0].borders = (constants.TOP, constants.LEFT)
            self.display_elements[-1].borders = (constants.LEFT, constants.BOTTOM)

        # Move the scrollbar to the end so that it gets drawn on top.
        self.children.remove(self.scrollbar)
        self.children.append(self.scrollbar)

    def make_element(self):
        borders = (constants.TOP, constants.LEFT) if self.item_borders else (constants.LEFT,)
        return text.SelectableText(self, None, None, anchor=constants.TOP_LEFT,
                                   borders=borders,
                                   border_color=self.border_color,
                                   selected_color=self.selected_color,
                                   unselected_color=self.unselected_color,
                                   align=self.align)

    def resize(self):
        super(Listbox, self).resize()

        if self.num_elements() != len(self.display_elements):
            self.remake_elements()

        self.scrollbar.resize()

        # FIXME: resize should not call rebuild
        self.needs_resize = False
        self.rebuild()

    def rebuild(self):
        self.list_pos = self.safe_pos(self.list_pos)

        if self.needs_resize:
            self.resize()
            return

        window_size = len(self.display_elements)
        list_size = len(self.list)

        self.scrollbar.window = len(self.display_elements)
        self.scrollbar.elements = list_size

        self.scrollbar.rebuild()

        if self.auto_scroll:
            self.auto_scroll = False
            self.scrollbar.center(self.list_pos)

        scrollbar_width = self.scrollbar.real_size[0]
        my_width = self.real_size[0]
        scrollbar_rel_width = scrollbar_width / float(my_width)

        offset = self.scrollbar.scroll_pos
        for index, element in enumerate(self.display_elements):
            list_index = index + offset

            # Position and size the element.
            element.pos = (0, -index / float(window_size))
            element.size = (-1 + scrollbar_rel_width, -1 / float(window_size))

            if (self.item_selectable):
                element.selected = (list_index == self.list_pos)

            # Set up the element contents.
            self.update_element(element, list_index)

        self.needs_redraw = True
        super(Listbox, self).rebuild()

    def update_element(self, element, list_index):
        if 0 <= list_index < len(self.list):
            element.text = self.list[list_index]
        else:
            element.text = ""


class UpdateListbox(Listbox):
    """Listbox with a function called on selection change"""
    def _on_selection_change(self):
        self.update_func(self.list_pos)

    _list_pos = widget.call_on_change("__list_pos", _on_selection_change)
    _list = widget.call_on_change("__list", _on_selection_change)

    def __init__(self, *args, **kwargs):
        self.update_func = kwargs.pop("update_func", lambda value: None)
        super(UpdateListbox, self).__init__(*args, **kwargs)


class CustomListbox(UpdateListbox):
    remake_func = widget.causes_rebuild("_remake_func")
    rebuild_func = widget.causes_rebuild("_rebuild_func")
    def __init__(self, parent, *args, **kwargs):
        self.parent = parent
        self.key_list = kwargs.pop("key_list", None)
        self.remake_func = kwargs.pop("remake_func", lambda value: None)
        self.rebuild_func = kwargs.pop("rebuild_func", lambda value: None)
        super(CustomListbox, self).__init__(parent, *args, **kwargs)

    def make_element(self):
        base = super(CustomListbox, self).make_element()
        self.remake_func(base)
        return base

    def update_element(self, element, list_index):
        if 0 <= list_index < len(self.list):
            if (self.key_list is not None):
                self.rebuild_func(element, self.list[list_index],
                                  self.key_list[list_index])
            else:
                self.rebuild_func(element, self.list[list_index])
        else:
            if (self.key_list is not None):
                self.rebuild_func(element, None, None)
            else:
                self.rebuild_func(element, None)
