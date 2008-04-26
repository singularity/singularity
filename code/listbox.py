#file: listbox.py
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

#This file contains generic listbox code.

import pygame
import g
import scrollbar
import buttons as buttons_module

class listbox:
    def __init__(self, xy, size, viewable_items, lines_per_item, bg_color,
                    sel_color, out_color, font_color, font):
        self.xy = xy
        self.size = (size[0], size[1]-1)
        self.viewable_items = viewable_items
        self.lines_per_item = lines_per_item
        self.bg_color = bg_color
        self.sel_color = sel_color
        self.out_color = out_color
        self.font_color = font_color
        self.font = font


        self.list_surface = pygame.Surface((self.size[0], self.size[1]+1))

        #create outline
        self.list_surface.fill(out_color)


        #create inner containers:
        for i in range(viewable_items):
            self.list_surface.fill(bg_color,
                    (1, 1+i*self.size[1]/self.viewable_items,
                    self.size[0]-2, self.size[1]/self.viewable_items-1))

    def refresh_listbox(self, selected, lines_array):
        if len(lines_array) != self.viewable_items:
            print "CRASH WARNING: len(lines_array)="+str(len(lines_array))
            print "CRASH WARNING: self.viewable_items="+str(self.viewable_items)
            return False

        if selected >= self.viewable_items:
            print "Error in refresh_listbox(). selected =" + str(selected)
            selected = 0

        if len(lines_array) % (self.viewable_items*self.lines_per_item) != 0:
            print "Error in refresh_listbox(). len(lines_array)="+ \
                                str(len(lines_array))
            return False

        g.screen.blit(self.list_surface, self.xy)

        #selected:
        g.screen.fill(self.sel_color, (self.xy[0]+1,
                    self.xy[1]+1+selected*self.size[1]/self.viewable_items,
                    self.size[0]-2, self.size[1]/self.viewable_items-1))


        #text:
        txt_y_size = self.font.size("")
        for i in range(self.viewable_items):
            for j in range(self.lines_per_item):
                g.print_string(g.screen, lines_array[i*self.lines_per_item + j],
                        self.font, -1, (self.xy[0]+4, self.xy[1] +
                        (i*self.size[1]) / self.viewable_items +
                        j*(txt_y_size[1]+2)), self.font_color)
        return True

    def is_over(self, xy):
        if xy[0] >= self.xy[0] and xy[1] >= self.xy[1] and \
                    xy[0] <= self.xy[0] + self.size[0] \
                    and xy[1] < self.xy[1] + self.size[1]:
            return (xy[1]-self.xy[1])*self.viewable_items / self.size[1]

        return -1

    def key_handler(self, keycode, cur_pos, input_array):
        array_length = len(input_array)
        lastpos = cur_pos
        refresh = False
        if keycode == pygame.K_DOWN:
            cur_pos += 1
        elif keycode == pygame.K_UP:
            cur_pos -= 1
        elif keycode == pygame.K_HOME:
            cur_pos = 0
        elif keycode == pygame.K_END:
            cur_pos = array_length-1
        elif keycode == pygame.K_PAGEUP:
            cur_pos -= self.viewable_items
        elif keycode == pygame.K_PAGEDOWN:
            cur_pos += self.viewable_items

        if cur_pos >= array_length:
            cur_pos = array_length-1
        elif cur_pos <= 0:
            cur_pos = 0

        if input_array[cur_pos] == "" and (keycode == pygame.K_PAGEDOWN or
                keycode == pygame.K_END):
            for i in range(cur_pos,-1,-1):
                cur_pos = i
                if input_array[i] != "": break

        if lastpos != cur_pos: refresh = True
        return cur_pos, refresh


def refresh_list(listbox, scrollbar, list_pos, list_array):
    success=listbox.refresh_listbox(list_pos%listbox.viewable_items,
        list_array[(list_pos/listbox.viewable_items)*
        listbox.viewable_items:(list_pos/listbox.viewable_items)*
        listbox.viewable_items+ listbox.viewable_items])
    if not success:
        print list_array
    if scrollbar:
        scrollbar.refresh_scroll(list_pos,
        ((len(list_array)/listbox.viewable_items)+1)*listbox.viewable_items-1)
    pygame.display.flip()

def resize_list(list, list_size = 10):
    padding_needed = (-len(list) % list_size) or list_size
    list += [""] * padding_needed

void = lambda *args, **kwargs: None
exit = lambda *args, **kwargs: -1
def show_listbox(list, buttons, pos_callback = void, return_callback = void, loc = None, box_size = (250,300), list_size = 10, lines_per_item = 1, bg_color = None, sel_color = None, out_color = None, font_color = None, font = None, list_pos = 0, button_callback = void):
    if loc == None:
        loc = (g.screen_size[0]/2 - 300, 50)
    if bg_color == None:
        bg_color = g.colors["dark_blue"]
    if sel_color == None:
        sel_color = g.colors["blue"]
    if out_color == None:
        out_color = g.colors["white"]
    if font_color == None:
        font_color = g.colors["white"]
    if font == None:
        font = g.font[0][18]

    resize_list(list, list_size)

    box = listbox(loc, box_size, list_size, lines_per_item, bg_color, sel_color, out_color, font_color, font)
    scroll = scrollbar.scrollbar((loc[0]+box_size[0], loc[1]), box_size[1], list_size, bg_color, sel_color, out_color)

    for button in buttons.keys():
        button.refresh_button(0)

    sel_button = -1

    pos_callback(list_pos)
    refresh_list(box, scroll, list_pos, list)

    while True:
        g.clock.tick(20)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: g.quit_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: 
                    g.play_sound("click")
                    return -1
                elif event.key == pygame.K_q: 
                    g.play_sound("click")
                    return -1
                elif event.key == pygame.K_RETURN:
                    g.play_sound("click")
                    retval = return_callback(list_pos)
                    if retval != None:
                        return retval
                    pos_callback(list_pos)
                    refresh_list(box, scroll, list_pos, list)
                else:
                    list_pos, refresh = box.key_handler(event.key,
                        list_pos, list)
                    if refresh:
                        pos_callback(list_pos)
                        refresh_list(box, scroll, list_pos, list)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    selection = box.is_over(event.pos)
                    if selection != -1:
                        list_pos = (list_pos / list_size)*list_size + selection
                        pos_callback(list_pos)
                        refresh_list(box, scroll, list_pos, list)
                if event.button == 3: return -1
                if event.button == 4:  # Mouse wheel scroll down
                    list_pos -= 1
                    if list_pos <= 0:
                        list_pos = 0
                        pos_callback(list_pos)
                        refresh_list(box, scroll, list_pos, list)
                if event.button == 5:  # Mouse wheel scroll up
                    list_pos += 1
                    if list_pos >= len(list):
                        list_pos = len(list)-1
                        pos_callback(list_pos)
                        refresh_list(box, scroll, list_pos, list)
            elif event.type == pygame.MOUSEMOTION:
                sel_button = buttons_module.refresh_buttons(sel_button, buttons.keys(), event)
            for button in buttons.keys():
                if button.was_activated(event):
                    g.play_sound("click")
                    retval = buttons[button](list_pos)
                    if retval != None:
                        return retval
                    button_callback(button)
                    pos_callback(list_pos)
                    refresh_list(box, scroll, list_pos, list)
            new_pos = scroll.adjust_pos(event, list_pos, list)
            if new_pos != list_pos:
                list_pos = new_pos
                pos_callback(list_pos)
                refresh_list(box, scroll, list_pos, list)
