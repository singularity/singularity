#file: buttons.py
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

#This file contains button code.

import pygame
import g

class button:
    def __init__(self, xy, size, text, underline_char, bg_color, out_color,
                                sel_color, text_color, font, button_id=""):
        self.xy = xy
        self.size = size
        self.text = text
        self.visible = 1
        self.bg_color = bg_color
        self.out_color = out_color
        self.sel_color = sel_color
        self.text_color = text_color
        self.underline_char = underline_char
        self.activate_key = ""
        if underline_char != -1:
            self.activate_key = self.text[self.underline_char]
        self.font = font
        self.button_id = button_id
        self.stay_selected = 0
        if button_id == "":
            self.button_id = self.text


        self.color_change = 1
        if self.sel_color == self.bg_color:
            self.color_change = 0

        temp_size = font.size(text)
        if size == -1: #Autofit
            self.autosize = 1
            self.size = (temp_size[0]+4, temp_size[1]+3)
        else: self.autosize = 0
        self.button_surface = pygame.Surface(self.size)
        self.sel_button_surface = pygame.Surface(self.size)

        self.remake_button()
    def remake_button(self):
        if self.autosize == 1:
            temp_size = self.font.size(self.text)
            self.size = (temp_size[0]+4, temp_size[1]+3)
            self.button_surface = pygame.Surface(self.size)
            self.sel_button_surface = pygame.Surface(self.size)

        #Regular button:
        #create outline
        self.button_surface.fill(self.out_color)
        #create inner
        self.button_surface.fill(self.bg_color, (1, 1, self.size[0]-2, self.size[1]-2))
        temp_size = self.font.size(self.text)
        #create text
        offsets = ((self.size[0] - temp_size[0])/2, (self.size[1] - temp_size[1])/2)
        g.print_string(self.button_surface, self.text, self.font, self.underline_char,
                    offsets, self.text_color)
        #Selected button
        #create outline
        self.sel_button_surface.fill(self.out_color)
        #create inner
        self.sel_button_surface.fill(self.sel_color, (1, 1, self.size[0]-2, self.size[1]-2))
        temp_size = self.font.size(self.text)
        #create text
        offsets = ((self.size[0] - temp_size[0])/2, (self.size[1] - temp_size[1])/2)
        g.print_string(self.sel_button_surface, self.text, self.font, self.underline_char,
                    offsets, self.text_color)

        #Recheck the activate key in case the text was changed.
        if self.underline_char != -1:
            self.activate_key = self.text[self.underline_char]



    def refresh_button(self, selected):
        if self.visible == 0: return 0
        if self.stay_selected == 1: selected = 1
        if selected == 0:
            g.screen.blit(self.button_surface, self.xy)
        else:
            g.screen.blit(self.sel_button_surface, self.xy)
    def is_over(self, xy):
        if self.visible == 0: return 0
        if xy[0] >= self.xy[0] and xy[1] >= self.xy[1] and \
        xy[0] <= self.xy[0] + self.size[0] and xy[1] <= self.xy[1] + self.size[1]:
            return 1
        return 0
    #Returns 1 if the event should activate this button. Checks for keypresses
    #and button clicks.
    def was_activated(self, event):
        if self.visible == 0: return 0
        if event.type == pygame.KEYDOWN and self.activate_key != "":
            if event.unicode.lower() == self.activate_key.lower():
                return 1
            return 0
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            return self.is_over(event.pos)
        else: return 0

#refreshes a set of buttons. Takes an int for the current button,
#references to the button set, and an event to use for checking mouseover on.
def refresh_buttons(sel_button, menu_buttons, event):
    new_sel_button = -1
    for button_num in range(len(menu_buttons)):
        if menu_buttons[button_num].is_over(event.pos) == 1:
            new_sel_button = button_num
            break
    if sel_button != new_sel_button:
        if sel_button != -1:
            menu_buttons[sel_button].refresh_button(0)
        if new_sel_button != -1:
            menu_buttons[new_sel_button].refresh_button(1)
        pygame.display.flip()
    return new_sel_button

#while buttons allow for creation of any button style needed, most of the
#buttons are of one style.
def make_norm_button(xy, size, text, select_char, font, button_id=""):
    return button(xy, size, text, select_char,
        g.colors["dark_blue"], g.colors["white"],
        g.colors["light_blue"], g.colors["white"], font, button_id)

