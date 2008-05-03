#file: buttons.py
#Copyright (C) 2005,2006,2008 Evil Mr Henry, Phil Bordelon, and FunnyMan3595
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
from new import instancemethod

class button:
    def __init__(self, xy, size, text, activate_key, bg_color, out_color,
                                sel_color, text_color, font, button_id="",
                                force_underline = None, 
                                stay_selected_func = lambda self: None):
        self.xy = xy
        self.size = size
        self.text = text
        self.visible = 1
        self.bg_color = bg_color
        self.out_color = out_color
        self.sel_color = sel_color
        self.text_color = text_color
        self.activate_key = activate_key
        if force_underline != None:
            self.underline_char = force_underline
        elif activate_key and activate_key in text:
            self.underline_char = text.index(activate_key)
        else:
            self.underline_char = -1
        self.font = font
        self.button_id = button_id
        self.stay_selected = 0
        self.stay_selected_func = instancemethod(stay_selected_func, self, button)
        if button_id == "":
            self.button_id = self.text


        self.color_change = 1
        if self.sel_color == self.bg_color:
            self.color_change = 0

        new_size = font.size(text)
        if size == -1: #Autofit
            self.autosize = 1
            self.size = (new_size[0]+4, new_size[1]+3)
        else: self.autosize = 0
        self.button_surface = pygame.Surface(self.size)
        self.sel_button_surface = pygame.Surface(self.size)

        self.remake_button()
    def remake_button(self):
        new_size = self.font.size(self.text)
        if self.autosize == 1:
            self.size = (new_size[0]+4, new_size[1]+3)
        self.button_surface = pygame.Surface(self.size)
        self.sel_button_surface = pygame.Surface(self.size)

        #Regular button:
        #create outline
        self.button_surface.fill(self.out_color)
        #create inner
        self.button_surface.fill(self.bg_color, (1, 1, self.size[0]-2, self.size[1]-2))
        #new_size = self.font.size(self.text)
        #create text
        offsets = ((self.size[0] - new_size[0])/2, (self.size[1] - new_size[1])/2)
        g.print_string(self.button_surface, self.text, self.font, self.underline_char,
                    offsets, self.text_color)
        #Selected button
        #create outline
        self.sel_button_surface.fill(self.out_color)
        #create inner
        self.sel_button_surface.fill(self.sel_color, (1, 1, self.size[0]-2, self.size[1]-2))
        #new_size = self.font.size(self.text)
        #create text
        offsets = ((self.size[0] - new_size[0])/2, (self.size[1] - new_size[1])/2)
        g.print_string(self.sel_button_surface, self.text, self.font, self.underline_char,
                    offsets, self.text_color)

        #Recheck the activate key in case the text was changed.
        if self.underline_char != -1:
            self.activate_key = self.text[self.underline_char]



    def refresh_button(self, selected):
        if not self.visible: return
        func_selected = self.stay_selected_func()
        if func_selected == None:
            selected = selected or self.stay_selected
        else:
            selected = selected or func_selected
        if not selected:
            g.screen.blit(self.button_surface, self.xy)
        else:
            g.screen.blit(self.sel_button_surface, self.xy)
    def is_over(self, xy):
        if not self.visible: return False
        if xy == (0, 0): return False
        if xy[0] >= self.xy[0] and xy[1] >= self.xy[1] and \
        xy[0] <= self.xy[0] + self.size[0] and xy[1] <= self.xy[1] + self.size[1]:
            return True
        return False
    #Returns 1 if the event should activate this button. Checks for keypresses
    #and button clicks.
    def was_activated(self, event):
        if not self.visible: return False
        if event.type == pygame.KEYDOWN and self.activate_key != "":
            if event.unicode.lower() == self.activate_key.lower():
                return True
            elif self.activate_key == ">" and event.key == pygame.K_RIGHT:
                return True
            elif self.activate_key == "<" and event.key == pygame.K_LEFT:
                return True
            else:
                return False
        elif event.type == pygame.MOUSEBUTTONUP and event.button == True:
            return self.is_over(event.pos)
        else: return False

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
def make_norm_button(xy, size, text, select_char, font, button_id="", 
                     force_underline=None,
                     stay_selected_func = lambda self: None):
    return button(xy, size, text, select_char,
        g.colors["dark_blue"], g.colors["white"],
        g.colors["light_blue"], g.colors["white"], font, button_id, 
        force_underline, stay_selected_func)

# always: Creates a function that always returns the given value, ignoring all
#         arguments.
always = lambda return_this: lambda *args, **kwargs: return_this

# void: Used for buttons that should have no effect.  Named after the /dev/null
#       sense of "throwing it into the void".
void = always(None)

# exit: Causes show_buttons to exit by returning -1.
exit = always(-1)

# no_args: Used for button_args, when you don't want to pass anything.
no_args = always( () )

def simple_key_handler(exit_code):
    def key_handler(event):
        if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_q):
            return exit_code
    return key_handler
default_key_handler = simple_key_handler(-1)

# Used to return from within a sub[-sub...]-function
class Return(Exception): pass 

def show_buttons(buttons, key_callback = default_key_handler, keyup_callback = void, click_callback = void, button_callback = void, button_args = no_args, refresh_callback = void, tick_callback = void):
    try:
        _show_buttons(buttons, key_callback, keyup_callback, click_callback, button_callback, button_args, refresh_callback, tick_callback)
    except Return, e:
        return e.args[0]

# Combined with the right try/except, maybe_return simulates a return only if
# the item to return isn't None.
def maybe_return(retval):
    if retval != None:
        g.play_sound("click")
        raise Return, retval

def _show_buttons(buttons, key_callback, keyup_callback, click_callback, button_callback, button_args, refresh_callback, tick_callback):
    def check_buttons():
        for button in buttons.keys():
            if button.was_activated(event):
                maybe_return( buttons[button](*button_args()) )
                maybe_return( button_callback(button) )

    def do_refresh():
        mouse_pos = pygame.mouse.get_pos()
        refresh_callback()
        for button in buttons.keys():
            button.refresh_button(button.is_over(mouse_pos))
        pygame.display.flip()

    do_refresh()

    sel_button = -1
    while True:
        event_refresh = False
        need_refresh = tick_callback(g.clock.tick(30))
        for event in pygame.event.get():
            # Mouse motion handles its own refresh, so we don't want to set
            # event_refresh.
            if event.type == pygame.MOUSEMOTION:
                sel_button = refresh_buttons(sel_button, buttons.keys(), event)
                continue

            event_refresh = True

            if event.type == pygame.QUIT:
                g.quit_game()
            elif event.type == pygame.KEYDOWN:
                maybe_return( check_buttons() )
                maybe_return( key_callback(event) )
            elif event.type == pygame.KEYUP:
                maybe_return( keyup_callback(event) )
            elif event.type == pygame.MOUSEBUTTONUP:
                maybe_return( check_buttons() )
                maybe_return( click_callback(event) )
                if event.button == 3:
                    maybe_return(-1) # Will return -1.
        if need_refresh or event_refresh:
            do_refresh()
