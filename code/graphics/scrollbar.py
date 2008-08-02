#file: scrollbar.py
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

#This file contains the scrollbar widget.

import pygame

import constants
import g
import widget
import button
import slider

class _ArrowButton(button.FunctionButton, button.ImageButton):
    def __init__(self, parent, *args, **kwargs):
        assert "first" in kwargs
        self.first = kwargs.pop("first")
        if "horizontal" in kwargs:
            self.horizontal = kwargs.pop("horizontal")
        else:
            self.horizontal = False

        kwargs["function"] = parent.adjust
        kwargs["args"] = (self.first,)
        super(_ArrowButton, self).__init__(parent, *args, **kwargs)

        base_image = g.images['arrow.png']
        if self.first and self.horizontal:
            angle = 90
            self.borders = (constants.LEFT, constants.TOP, constants.BOTTOM)
        elif self.first:
            angle = 0
            self.borders = (constants.LEFT, constants.TOP, constants.RIGHT)
        elif self.horizontal:
            angle = -90
            self.borders = (constants.TOP, constants.RIGHT, constants.BOTTOM)
        else:
            angle = -180
            self.borders = (constants.RIGHT, constants.BOTTOM, constants.LEFT)
        rotated_image = pygame.transform.rotate(base_image, angle)
        self.image.image = rotated_image.convert_alpha()

class Scrollbar(widget.Widget):
    scroll_pos = widget.causes_rebuild("_scroll_pos")
    elements = widget.causes_rebuild("_elements")
    window = widget.causes_rebuild("_window")
    horizontal = widget.causes_rebuild("_horizontal")

    def __init__(self, parent, pos = (1,0), size = (-.025, 1), 
                 anchor = constants.TOP_RIGHT, scroll_pos = 0,
                 elements = 15, window = 5, horizontal = False):
        super(Scrollbar, self).__init__(parent, pos, size, anchor)
        
        self.scroll_pos = scroll_pos
        self.elements = elements
        self.window = window
        self.horizontal = horizontal

        self.slider = slider.UpdateSlider(self, (.5,.5), None,
                                          anchor = constants.MID_CENTER,
                                          horizontal = horizontal,
                                          update_func = self.on_change)

        self.button1 = _ArrowButton(self, (0,0), None, 
                                    anchor = constants.TOP_LEFT,
                                    first = True, horizontal = horizontal)

        self.button2 = _ArrowButton(self, (1,1), None, 
                                    anchor = constants.BOTTOM_RIGHT,
                                    first = False, horizontal = horizontal)

    def rebuild(self):
        super(Scrollbar, self).rebuild()
        if self.horizontal:
            long = self.real_size[0]
            short = self.real_size[1]
            size = short / float(long)
            self.button1.size = (size, 1)
            self.button2.size = (size, 1)
            self.slider.size = (1 - (size * 2), 1)
        else:
            long = self.real_size[1]
            short = self.real_size[0]
            size = short / float(long)
            self.button1.size = (1, size)
            self.button2.size = (1, size)
            self.slider.size = (1, 1 - (size * 2))

        self.slider.slider_pos = self.scroll_pos
        self.slider.slider_size = self.window
        self.slider.slider_max = slider.calc_max(self.elements, self.window)

    def adjust(self, lower):
        if lower:
            self.slider.slider_pos = self.slider.safe_pos(self.scroll_pos - 1)
        else:
            self.slider.slider_pos = self.slider.safe_pos(self.scroll_pos + 1)

    def center(self, element):
        self.slider.slider_pos = self.slider.safe_pos(element - self.window//2)

    def scroll_to(self, element):
        if element < self.scroll_pos:
            self.slider.slider_pos = self.slider.safe_pos(element)
        elif element >= self.scroll_pos + self.window:
            self.slider.slider_pos = self.slider.safe_pos(element - self.window
                                                          + 1)

    def on_change(self, value):
        self.scroll_pos = value


class UpdateScrollbar(Scrollbar):
    def __init__(self, *args, **kwargs):
        if "update_func" in kwargs:
            self.update_func = kwargs.pop("update_func")
        else:
            self.update_func = lambda value: None
        super(UpdateScrollbar, self).__init__(*args, **kwargs)

    def on_change(self, value):
        self.scroll_pos = value
        self.update_func(value)
