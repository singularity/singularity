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
            return 0

        if selected >= self.viewable_items:
            print "Error in refresh_listbox(). selected =" + str(selected)
            selected = 0

        if len(lines_array) % (self.viewable_items*self.lines_per_item) != 0:
            print "Error in refresh_listbox(). len(lines_array)="+ \
                                str(len(lines_array))
            return 0

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
        return 1

    def is_over(self, xy):
        if xy[0] >= self.xy[0] and xy[1] >= self.xy[1] and \
                    xy[0] <= self.xy[0] + self.size[0] \
                    and xy[1] < self.xy[1] + self.size[1]:
            return (xy[1]-self.xy[1])*self.viewable_items / self.size[1]

        return -1

    def key_handler(self, keycode, cur_pos, array_length):
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

        if lastpos != cur_pos: refresh = True
        return cur_pos, refresh


def refresh_list(listbox, scrollbar, list_pos, list_array):
    tmp=listbox.refresh_listbox(list_pos%listbox.viewable_items,
        list_array[(list_pos/listbox.viewable_items)*
        listbox.viewable_items:(list_pos/listbox.viewable_items)*
        listbox.viewable_items+ listbox.viewable_items])
    if tmp==0:
        print list_array
    if scrollbar != 0:
        scrollbar.refresh_scroll(list_pos,
        ((len(list_array)/listbox.viewable_items)+1)*listbox.viewable_items-1)
    pygame.display.flip()

