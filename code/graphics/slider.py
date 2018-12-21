#file: slider.py
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

#This file contains the slider widget.

import pygame

import constants
import g
import widget
import button

def calc_max(elements, size):
    return max(elements - size, 0)

class Slider(button.Button):
    slider_pos = widget.causes_rebuild("_slider_pos")
    slider_max = widget.causes_rebuild("_slider_max")
    slider_size = widget.causes_rebuild("_slider_size")
    horizontal = widget.causes_rebuild("_horizontal")

    slider_color = widget.auto_reconfig("_slider_color", g.resolve_color_alias)
    _slider_color = widget.causes_redraw("__slider_color")

    def __init__(self, parent, pos = (-1,0), size = (-.1, -1),
                 anchor = constants.TOP_RIGHT, borders = constants.ALL,
                 border_color=None, background_color=None, slider_color=None,
                 slider_pos=0, slider_max=10, slider_size=5, horizontal=False,
                 **kwargs):
        kwargs.setdefault("priority", 80)
        super(Slider, self).__init__(parent, pos, size, anchor=anchor, **kwargs)

        border_color = border_color or "slider_border"
        background_color = background_color or "slider_background"
        slider_color = slider_color or "slider_background_slider"

        self.borders = borders
        self.border_color = border_color
        self.background_color = background_color
        self.selected_color = background_color
        self.unselected_color = background_color
        self.slider_color = slider_color

        self.slider_pos = slider_pos
        self.slider_max = slider_max
        self.slider_size = slider_size
        self.horizontal = horizontal

        self.drag_state = None
        self.button = button.Button(self, pos = None, size = None,
                                    anchor = constants.TOP_LEFT,
                                    border_color = border_color,
                                    selected_color = slider_color,
                                    unselected_color = slider_color,
                                    priority = self.priority - 5)

    def redraw(self):
        super(Slider, self).redraw()
        self.button.selected_color = self.slider_color
        self.button.unselected_color = self.slider_color

    def add_hooks(self):
        super(Slider, self).add_hooks()
        self.parent.add_handler(constants.DRAG, self.handle_drag)
        self.parent.add_handler(constants.CLICK, self.handle_click, 50)

    def remove_hooks(self):
        super(Slider, self).remove_hooks()
        self.parent.remove_handler(constants.DRAG, self.handle_drag)
        self.parent.remove_handler(constants.CLICK, self.handle_click)

    def _calc_length(self, items):
        return items / float(self.slider_size + self.slider_max)

    def rebuild(self):
        super(Slider, self).rebuild()
        self.needs_resize = True

    def resize(self):
        super(Slider, self).resize()
        bar_start = self._calc_length(self.slider_pos)
        bar_length = self._calc_length(self.slider_size)

        if self.horizontal:
            self.button.pos = (-bar_start, 0)
            self.button.size = (-bar_length, -1)
            borders = [constants.TOP, constants.BOTTOM]

            self.button.resize()
            real_pos = self.button.real_pos[0]
            real_size = self.button.real_size[0]
            if real_pos == 0:
                borders.append(constants.LEFT)
            if real_pos + real_size == self.real_size[0]:
                borders.append(constants.RIGHT)
            self.button.borders = tuple(borders)
        else:
            self.button.pos = (0, -bar_start)
            self.button.size = (-1, -bar_length)
            borders = [constants.LEFT, constants.RIGHT]

            self.button.resize()
            real_pos = self.button.real_pos[1]
            real_size = self.button.real_size[1]
            if real_pos == 0:
                borders.append(constants.TOP)
            if real_pos + real_size == self.real_size[1]:
                borders.append(constants.BOTTOM)
            self.button.borders = tuple(borders)

    def handle_drag(self, event):
        if not self.visible:
            return

        if self.drag_state == None:
            self.start_pos = tuple(event.pos[i]-event.rel[i] for i in range(2))
            self.start_slider_pos = self.slider_pos
            if self.button.is_over(self.start_pos):
                self.drag_state = True
            else:
                self.drag_state = False

        if self.drag_state == True:
            if self.horizontal:
                dir = 0
            else:
                dir = 1

            mouse_pos = pygame.mouse.get_pos()
            rel = mouse_pos[dir] - self.start_pos[dir]
            unit = self._calc_length(1) * self.real_size[dir]
            movement = int( ( rel + (unit / 2.) ) // unit )

            new_pos = self.safe_pos(self.start_slider_pos + movement)
            self.slider_pos = new_pos

            raise constants.Handled

    def safe_pos(self, value):
        return max(0, min(self.slider_max, value))

    def handle_click(self, event):
        if self.drag_state == True:
            self.drag_state = None
            if not self.is_over(pygame.mouse.get_pos()):
                raise constants.Handled
        else:
            self.drag_state = None

    def jump(self, go_lower, big_jump=False, tiny_jump=False):
        if big_jump:
            jump_dist = max(1, self.slider_max // 2)
        elif tiny_jump:
            jump_dist = max(1, self.slider_max // 100)
        else:
            jump_dist = max(1, self.slider_size - 1)
        if go_lower:
            self.slider_pos = self.safe_pos(self.slider_pos - jump_dist)
        else:
            self.slider_pos = self.safe_pos(self.slider_pos + jump_dist)

    def activated(self, event):
        assert event.type == pygame.MOUSEBUTTONUP
        if self.horizontal:
            self.jump(go_lower=(event.pos[0] < self.button.collision_rect[0]))
        else:
            self.jump(go_lower = event.pos[1] < self.button.collision_rect[1])
        raise constants.Handled


class UpdateSlider(Slider):
    def _on_slider_move(self):
        self.update_func(self.slider_pos)

    _slider_pos = widget.call_on_change("__slider_pos", _on_slider_move)

    def __init__(self, *args, **kwargs):
        self.update_func = kwargs.pop("update_func", lambda value: None)
        super(UpdateSlider, self).__init__(*args, **kwargs)
