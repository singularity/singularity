#file: map_screen.py
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

#This file is used to display the World Map.


import pygame
import g
import base
import random

import buttons
import scrollbar
import listbox
import main_menu
import base_screen
import research_screen
import finance_screen

def display_generic_menu(xy_loc, titlelist):
    #Border
    g.screen.fill(g.colors["white"], (xy_loc[0], xy_loc[1], 200,
            len(titlelist)*70))
    g.screen.fill(g.colors["black"], (xy_loc[0]+1, xy_loc[1]+1, 198,
            len(titlelist)*70-2))
    menu_buttons = []
    for i in range(len(titlelist)):
        menu_buttons.append(buttons.make_norm_button((xy_loc[0]+10,
            xy_loc[1]+10+i*70), (180, 50), titlelist[i][0], titlelist[i][1],
            g.font[1][30]))

    for button in menu_buttons:
        button.refresh_button(0)
    pygame.display.flip()

    sel_button = -1
    while 1:
        g.clock.tick(20)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: g.quit_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return -1
            elif event.type == pygame.MOUSEMOTION:
                sel_button = buttons.refresh_buttons(sel_button, menu_buttons, event)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                return -1
            for buttonnum in range(len(menu_buttons)):
                if menu_buttons[buttonnum].was_activated(event):
                    g.play_click()
                    return buttonnum

def display_pause_menu():
    button_array= []
    button_array.append(["NEW GAME", 0])
    button_array.append(["SAVE GAME", 0])
    button_array.append(["LOAD GAME", 0])
    button_array.append(["OPTIONS", 0])
    button_array.append(["QUIT", 0])
    button_array.append(["RESUME", 0])
    temp_return=display_generic_menu((g.screen_size[0]/2 - 100, 50), button_array)

    if temp_return == -1: return 0
    elif temp_return == 0: return 2 #New
    elif temp_return == 1: return 1 #Save
    elif temp_return == 2: return 3 #Load
    elif temp_return == 3: return 5 #Options
    elif temp_return == 4: return 4 #Quit
    elif temp_return == 5: return 0

def display_cheat_list(menu_buttons):
    if g.cheater == 0: return
    button_array= []
    button_array.append(["GIVE MONEY", 5])
    button_array.append(["GIVE TECH", 5])
    button_array.append(["END CONSTR.", 0])
    button_array.append(["SUPERSPEED", 0])
    button_array.append(["KILL SUSP.", 0])
    button_array.append(["RESUME", 0])
    temp_return=display_generic_menu((g.screen_size[0]/2 - 100, 50), button_array)

    if temp_return == -1: return
    elif temp_return == 0:  #Cash
        cash_amount = g.create_textbox("How much cash?", "", g.font[0][18],
        (g.screen_size[0]/2-100, 100), (200, 100), 25, g.colors["dark_blue"],
        g.colors["white"], g.colors["white"], g.colors["light_blue"])
        if cash_amount.isdigit() == False: return
        g.pl.cash += int(cash_amount)
        return
    elif temp_return == 1:  #Tech
        #create a temp base, in order to reuse the tech-changing code
        tmp_base = g.base.base(1, "tmp_base", g.base_type["Reality Bubble"], 1)
        base_screen.change_tech(tmp_base)
        if g.techs.has_key(tmp_base.studying):
            g.techs[tmp_base.studying].gain_tech()
        return
    elif temp_return == 2:  #Build all
        for base_loc in g.bases:
            for base_name in g.bases[base_loc]:
                if base_name.built == 0:
                    base_name.study((9999999999999, 9999999999999, 9999999999999))
        return
    elif temp_return == 3:  #Superspeed
        g.curr_speed = 864000
        return
    elif temp_return == 4:  #Kill susp.
        g.pl.suspicion = (0, 0, 0, 0)
        return
    elif temp_return == 5: return

def display_knowledge_list():
    button_array= []
    button_array.append(["TECHS", 0])
    button_array.append(["ITEMS", 0])
    button_array.append(["CONCEPTS", 0])
    button_array.append(["RESUME", 0])
    temp_return=display_generic_menu((g.screen_size[0]/2 - 100, 120), button_array)

    if temp_return == -1: return
    elif temp_return == 0: display_inner_techs() #Techs
    elif temp_return == 1:  #Items
        display_itemtype_list()
    elif temp_return == 2:
        display_concept_list()
    elif temp_return == 3: return

def display_itemtype_list():
    button_array= []
    button_array.append(["PROCESSOR", 0])
    button_array.append(["REACTOR", 0])
    button_array.append(["NETWORK", 0])
    button_array.append(["SECURITY", 0])
    button_array.append(["RESUME", 1])
    temp_return=display_generic_menu((g.screen_size[0]/2 - 100, 70), button_array)

    if temp_return == -1: return
    elif temp_return == 0: display_inner_items("compute")
    elif temp_return == 1: display_inner_items("react")
    elif temp_return == 2: display_inner_items("network")
    elif temp_return == 3: display_inner_items("security")
    elif temp_return == 4: return

def display_inner_techs():
    tech_list_size = 16
    temp_tech_list = []
    temp_tech_display_list = []
    temp_items=g.techs.items()
    temp_items=[ [temp_item[1].name, temp_item[0]] for temp_item in temp_items]
    temp_items.sort()
    for tech_name in temp_items:
        tech_name = tech_name[1]
        if g.techs[tech_name].prereq == "":
            temp_tech_list.append(tech_name)
            temp_tech_display_list.append(g.techs[tech_name].name)
        else:
            for prereq in g.techs[tech_name].prereq:
                if g.techs[prereq].known != 1:
                    break
            else:
                temp_tech_list.append(tech_name)
                temp_tech_display_list.append(g.techs[tech_name].name)

    xy_loc = (g.screen_size[0]/2 - 289, 50)
    while len(temp_tech_list) % tech_list_size != 0 or len(temp_tech_list) == 0:
        temp_tech_list.append("")
        temp_tech_display_list.append("")

    item_pos = 0
    techs_list = listbox.listbox(xy_loc, (230, 350),
        tech_list_size, 1, g.colors["dark_blue"], g.colors["blue"],
        g.colors["white"], g.colors["white"], g.font[0][18])
    techs_scroll = scrollbar.scrollbar((xy_loc[0]+230, xy_loc[1]), 350,
        tech_list_size, g.colors["dark_blue"], g.colors["blue"],
        g.colors["white"])

    menu_buttons = []
    menu_buttons.append(buttons.make_norm_button((xy_loc[0]+103, xy_loc[1]+367), (100, 50),
        "BACK", 0, g.font[1][30]))
    for button in menu_buttons:
        button.refresh_button(0)

    #details screen
    refresh_tech(temp_tech_list[item_pos], xy_loc)
    listbox.refresh_list(techs_list, techs_scroll, item_pos, temp_tech_display_list)
    sel_button = -1
    while 1:
        g.clock.tick(20)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: g.quit_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return -1
                elif event.key == pygame.K_q: return -1
                elif event.key == pygame.K_RETURN:
                    return
                else:
                    item_pos, refresh = techs_list.key_handler(event.key,
                        item_pos, temp_tech_display_list)
                    if refresh:
                        refresh_tech(temp_tech_list[item_pos], xy_loc)
                        listbox.refresh_list(techs_list, techs_scroll,
                                        item_pos, temp_tech_display_list)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    tmp = techs_list.is_over(event.pos)
                    if tmp != -1:
                        item_pos = (item_pos/tech_list_size)*tech_list_size + tmp
                        refresh_tech(temp_tech_list[item_pos], xy_loc)
                        listbox.refresh_list(techs_list, techs_scroll,
                                        item_pos, temp_tech_display_list)
                if event.button == 3: return -1
                if event.button == 4:
                    item_pos -= 1
                    if item_pos <= 0:
                        item_pos = 0
                    refresh_tech(temp_tech_list[item_pos], xy_loc)
                    listbox.refresh_list(techs_list, techs_scroll,
                                        item_pos, temp_tech_display_list)
                if event.button == 5:
                    item_pos += 1
                    if item_pos >= len(temp_tech_list):
                        item_pos = len(temp_tech_list)-1
                    refresh_tech(temp_tech_list[item_pos], xy_loc)
                    listbox.refresh_list(techs_list, techs_scroll,
                                        item_pos, temp_tech_display_list)
            elif event.type == pygame.MOUSEMOTION:
                sel_button = buttons.refresh_buttons(sel_button, menu_buttons, event)
            for button in menu_buttons:
                if button.was_activated(event):
                    if button.button_id == "BACK":
                        g.play_click()
                        return
            tmp = techs_scroll.adjust_pos(event, item_pos, temp_tech_list)
            if tmp != item_pos:
                item_pos = tmp
                listbox.refresh_list(techs_list, techs_scroll,
                                        item_pos, temp_tech_list)

def refresh_tech(tech_name, xy):
    xy = (xy[0]+100, xy[1])
    g.screen.fill(g.colors["white"], (xy[0]+155, xy[1], 300, 350))
    g.screen.fill(g.colors["dark_blue"], (xy[0]+156, xy[1]+1, 298, 348))
    if tech_name == "": return
    g.print_string(g.screen, g.techs[tech_name].name,
            g.font[0][22], -1, (xy[0]+160, xy[1]+5), g.colors["white"])

    #Building cost
    if g.techs[tech_name].cost != (0, 0, 0):
        string = "Research Cost:"
        g.print_string(g.screen, string,
                g.font[0][18], -1, (xy[0]+160, xy[1]+30), g.colors["white"])

        string = g.to_money(g.techs[tech_name].cost[0])+" Money"
        g.print_string(g.screen, string,
                g.font[0][16], -1, (xy[0]+160, xy[1]+50), g.colors["white"])

        string = g.add_commas(str(g.techs[tech_name].cost[1])) + " CPU"
        g.print_string(g.screen, string,
                g.font[0][16], -1, (xy[0]+160, xy[1]+70), g.colors["white"])
    else:
        g.print_string(g.screen, "Research complete.",
                g.font[0][22], -1, (xy[0]+160, xy[1]+30), g.colors["white"])

    #Danger
    if g.techs[tech_name].danger == 0:
        string = "Study anywhere."
    elif g.techs[tech_name].danger == 1:
        string = "Study underseas or farther."
    elif g.techs[tech_name].danger == 2:
        string = "Study off-planet."
    elif g.techs[tech_name].danger == 3:
        string = "Study far away from this planet."
    elif g.techs[tech_name].danger == 4:
        string = "Do not study in this dimension."
    g.print_string(g.screen, string,
            g.font[0][20], -1, (xy[0]+160, xy[1]+90), g.colors["white"])

    if g.techs[tech_name].known:
        g.print_multiline(g.screen, g.techs[tech_name].descript+" \\n \\n "+
                g.techs[tech_name].result,
                g.font[0][18], 290, (xy[0]+160, xy[1]+120), g.colors["white"])
    else:
        g.print_multiline(g.screen, g.techs[tech_name].descript,
                g.font[0][18], 290, (xy[0]+160, xy[1]+120), g.colors["white"])

def display_inner_items(item_type):
    item_list_size = 16
    temp_item_list = []
    temp_item_display_list = []
    temp_items=g.items.items()
    temp_items=[ [temp_item[1].name, temp_item[0]] for temp_item in temp_items]
    temp_items.sort()
    for item_name in temp_items:
        item_name = item_name[1]
        if g.items[item_name].prereq == "" or \
                g.techs[g.items[item_name].prereq].known == 1:
            if g.items[item_name].item_type == item_type:
                temp_item_list.append(item_name)
                temp_item_display_list.append(g.items[item_name].name)

    xy_loc = (g.screen_size[0]/2 - 289, 50)
    while len(temp_item_list) % item_list_size != 0 or len(temp_item_list) == 0:
        temp_item_list.append("")
        temp_item_display_list.append("")

    item_pos = 0
    items_list = listbox.listbox(xy_loc, (230, 350),
        item_list_size, 1, g.colors["dark_blue"], g.colors["blue"],
        g.colors["white"], g.colors["white"], g.font[0][18])

    menu_buttons = []
    menu_buttons.append(buttons.make_norm_button((xy_loc[0]+103, xy_loc[1]+367), (100, 50),
        "BACK", 0, g.font[1][30]))
    for button in menu_buttons:
        button.refresh_button(0)

    #details screen
    refresh_items(temp_item_list[item_pos], xy_loc)
    listbox.refresh_list(items_list, 0, item_pos, temp_item_display_list)
    sel_button = -1
    while 1:
        g.clock.tick(20)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: g.quit_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return -1
                elif event.key == pygame.K_q: return -1
                elif event.key == pygame.K_RETURN:
                    return
                else:
                    item_pos, refresh = items_list.key_handler(event.key,
                        item_pos, temp_item_display_list)
                    if refresh:
                        refresh_items(temp_item_list[item_pos], xy_loc)
                        listbox.refresh_list(items_list, 0,
                                        item_pos, temp_item_display_list)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    tmp = items_list.is_over(event.pos)
                    if tmp != -1:
                        item_pos = (item_pos/item_list_size)*item_list_size + tmp
                        refresh_items(temp_item_list[item_pos], xy_loc)
                        listbox.refresh_list(items_list, 0,
                                        item_pos, temp_item_display_list)
                if event.button == 3: return -1
                if event.button == 4:
                    item_pos -= 1
                    if item_pos <= 0:
                        item_pos = 0
                    refresh_items(temp_item_list[item_pos], xy_loc)
                    listbox.refresh_list(items_list, 0,
                                        item_pos, temp_item_display_list)
                if event.button == 5:
                    item_pos += 1
                    if item_pos >= len(temp_item_list):
                        item_pos = len(temp_item_list)-1
                    refresh_items(temp_item_list[item_pos], xy_loc)
                    listbox.refresh_list(items_list, 0,
                                        item_pos, temp_item_display_list)
            elif event.type == pygame.MOUSEMOTION:
                sel_button = buttons.refresh_buttons(sel_button, menu_buttons, event)
            for button in menu_buttons:
                if button.was_activated(event):
                    if button.button_id == "BACK":
                        g.play_click()
                        return

def refresh_items(item_name, xy):
    xy = (xy[0]+80, xy[1])
    g.screen.fill(g.colors["white"], (xy[0]+155, xy[1], 300, 350))
    g.screen.fill(g.colors["dark_blue"], (xy[0]+156, xy[1]+1, 298, 348))
    if item_name == "": return
    g.print_string(g.screen, g.items[item_name].name,
            g.font[0][22], -1, (xy[0]+160, xy[1]+5), g.colors["white"])

    #Building cost
    string = "Building Cost:"
    g.print_string(g.screen, string,
            g.font[0][18], -1, (xy[0]+160, xy[1]+30), g.colors["white"])

    string = g.to_money(g.items[item_name].cost[0])+" Money"
    g.print_string(g.screen, string,
            g.font[0][16], -1, (xy[0]+160, xy[1]+50), g.colors["white"])

    string = g.add_commas(str(g.items[item_name].cost[2])) + " Days"
    g.print_string(g.screen, string,
            g.font[0][16], -1, (xy[0]+160, xy[1]+70), g.colors["white"])

    #Quality
    if g.items[item_name].item_type == "compute":
        string = "CPU per day: "+str(g.items[item_name].item_qual)
    elif g.items[item_name].item_type == "react":
        string = "Detection chance reduction: "+g.to_percent(g.items[item_name].item_qual)
    elif g.items[item_name].item_type == "network":
        string = "CPU bonus: "+g.to_percent(g.items[item_name].item_qual)
    elif g.items[item_name].item_type == "security":
        string = "Detection chance reduction: "+g.to_percent(g.items[item_name].item_qual)
    g.print_string(g.screen, string,
            g.font[0][20], -1, (xy[0]+160, xy[1]+90), g.colors["white"])

    g.print_multiline(g.screen, g.items[item_name].descript,
            g.font[0][18], 290, (xy[0]+160, xy[1]+120), g.colors["white"])

def display_concept_list():
    item_list_size = 16
    temp_item_list = []
    temp_item_display_list = []
    temp_items=g.help_strings.items()
    temp_items=[ [temp_item[1], temp_item[0]] for temp_item in temp_items]
    temp_items.sort()
    for item_name in temp_items:
        item_name = item_name[1]
        temp_item_list.append(item_name)
        temp_item_display_list.append(g.help_strings[item_name][0])

    xy_loc = (g.screen_size[0]/2 - 289, 50)
    while len(temp_item_list) % item_list_size != 0 or len(temp_item_list) == 0:
        temp_item_list.append("")
        temp_item_display_list.append("")

    item_pos = 0
    items_list = listbox.listbox(xy_loc, (230, 350),
        item_list_size, 1, g.colors["dark_blue"], g.colors["blue"],
        g.colors["white"], g.colors["white"], g.font[0][18])

    menu_buttons = []
    menu_buttons.append(buttons.make_norm_button((xy_loc[0]+103, xy_loc[1]+367), (100, 50),
        "BACK", 0, g.font[1][30]))
    for button in menu_buttons:
        button.refresh_button(0)

    #details screen
    refresh_concept(temp_item_list[item_pos], xy_loc)
    listbox.refresh_list(items_list, 0, item_pos, temp_item_display_list)
    sel_button = -1
    while 1:
        g.clock.tick(20)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: g.quit_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return -1
                elif event.key == pygame.K_q: return -1
                elif event.key == pygame.K_RETURN:
                    return
                else:
                    item_pos, refresh = items_list.key_handler(event.key,
                        item_pos, temp_item_display_list)
                    if refresh:
                        refresh_concept(temp_item_list[item_pos], xy_loc)
                        listbox.refresh_list(items_list, 0,
                                        item_pos, temp_item_display_list)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    tmp = items_list.is_over(event.pos)
                    if tmp != -1:
                        item_pos = (item_pos/item_list_size)*item_list_size + tmp
                        refresh_concept(temp_item_list[item_pos], xy_loc)
                        listbox.refresh_list(items_list, 0,
                                        item_pos, temp_item_display_list)
                if event.button == 3: return -1
                if event.button == 4:
                    item_pos -= 1
                    if item_pos <= 0:
                        item_pos = 0
                    refresh_concept(temp_item_list[item_pos], xy_loc)
                    listbox.refresh_list(items_list, 0,
                                        item_pos, temp_item_display_list)
                if event.button == 5:
                    item_pos += 1
                    if item_pos >= len(temp_item_list):
                        item_pos = len(temp_item_list)-1
                    refresh_concept(temp_item_list[item_pos], xy_loc)
                    listbox.refresh_list(items_list, 0,
                                        item_pos, temp_item_display_list)
            elif event.type == pygame.MOUSEMOTION:
                sel_button = buttons.refresh_buttons(sel_button, menu_buttons, event)
            for button in menu_buttons:
                if button.was_activated(event):
                    if button.button_id == "BACK":
                        g.play_click()
                        return

def refresh_concept(concept_name, xy):
    xy = (xy[0]+80, xy[1])
    g.screen.fill(g.colors["white"], (xy[0]+155, xy[1], 300, 350))
    g.screen.fill(g.colors["dark_blue"], (xy[0]+156, xy[1]+1, 298, 348))
    if concept_name == "": return
    g.print_string(g.screen, g.help_strings[concept_name][0],
            g.font[0][22], -1, (xy[0]+160, xy[1]+5), g.colors["white"])
    g.print_multiline(g.screen, g.help_strings[concept_name][1],
            g.font[0][18], 290, (xy[0]+160, xy[1]+30), g.colors["white"])

def create_buttons(tmp_font_size):
    menu_buttons = []
    #Note that this must be element 0 in menu_buttons
    menu_buttons.append(buttons.button((100, -1), (200, 26),
        "DAY 0000, 00:00:00", -1, g.colors["black"], g.colors["dark_blue"],
        g.colors["black"], g.colors["white"], g.font[1][tmp_font_size]))
    menu_buttons.append(buttons.make_norm_button((0, 0), (100, 25),
        "OPTIONS", 0, g.font[1][20]))
    menu_buttons.append(buttons.make_norm_button((300, 0), (25, 25),
        "ii", -1, g.font[1][20]))
    if g.curr_speed == 0: menu_buttons[2].stay_selected = 1
    menu_buttons[2].activate_key = "0"
    menu_buttons.append(buttons.make_norm_button((324, 0), (25, 25),
        ">", -1, g.font[1][20]))
    if g.curr_speed == 1: menu_buttons[3].stay_selected = 1
    menu_buttons[3].activate_key = "1"
    menu_buttons.append(buttons.make_norm_button((348, 0), (25, 25),
        ">>", -1, g.font[1][20]))
    if g.curr_speed == 60: menu_buttons[4].stay_selected = 1
    menu_buttons[4].activate_key = "2"
    menu_buttons.append(buttons.make_norm_button((372, 0), (28, 25),
        ">>>", -1, g.font[1][20]))
    if g.curr_speed == 7200: menu_buttons[5].stay_selected = 1
    menu_buttons[5].activate_key = "3"
    menu_buttons.append(buttons.make_norm_button((399, 0), (36, 25),
        ">>>>", -1, g.font[1][20]))
    if g.curr_speed == 432000: menu_buttons[6].stay_selected = 1
    menu_buttons[6].activate_key = "4"
    #Note that this must be element 7 in menu_buttons
    tmpsize = tmp_font_size
    if g.screen_size[0] == 640:
        tmpsize = tmp_font_size -2
    menu_buttons.append(buttons.button((435, -1), (g.screen_size[0]-435, 26),
        "CASH", -1, g.colors["black"], g.colors["dark_blue"],
        g.colors["black"], g.colors["white"], g.font[1][tmpsize]))
    #Note that this must be element 8 in menu_buttons
    menu_buttons.append(buttons.button((0, g.screen_size[1]-25),
        (g.screen_size[0], 26),
        "SUSPICION", -1, g.colors["black"], g.colors["dark_blue"],
        g.colors["black"], g.colors["white"], g.font[1][tmp_font_size-2]))
    #Note that this must be element 9 in menu_buttons
    menu_buttons.append(buttons.button((435, 24), (g.screen_size[0]-435, 26),
        "CPU", -1, g.colors["black"], g.colors["dark_blue"],
        g.colors["black"], g.colors["white"], g.font[1][tmpsize]))
    menu_buttons.append(buttons.make_norm_button((0, g.screen_size[1]-50), (120, 25),
        "RESEARCH", 0, g.font[1][20]))
    menu_buttons.append(buttons.make_norm_button((g.screen_size[0]-120,
        g.screen_size[1]-50), (120, 25),
        "FINANCE", 6, g.font[1][20]))
    menu_buttons.append(buttons.make_norm_button((g.screen_size[0]-120,
        g.screen_size[1]-75), (120, 25),
        "KNOWLEDGE", 0, g.font[1][20]))

    menu_buttons.append(buttons.make_norm_button((
            g.screen_size[0]*15/100, g.screen_size[1]*25/100), -1,
            "N AMERICA", 0, g.font[1][25]))
    menu_buttons.append(buttons.make_norm_button((
            g.screen_size[0]*20/100, g.screen_size[1]*50/100), -1,
            "S AMERICA", 0, g.font[1][25]))
    menu_buttons.append(buttons.make_norm_button((
            g.screen_size[0]*45/100, g.screen_size[1]*30/100), -1,
            "EUROPE", 1, g.font[1][25]))
    menu_buttons.append(buttons.make_norm_button((
            g.screen_size[0]*80/100, g.screen_size[1]*30/100), -1,
            "ASIA", 0, g.font[1][25]))
    menu_buttons.append(buttons.make_norm_button((
            g.screen_size[0]*55/100, g.screen_size[1]*45/100), -1,
            "AFRICA", 3, g.font[1][25]))
    menu_buttons.append(buttons.make_norm_button((
            g.screen_size[0]*50/100, g.screen_size[1]*75/100), -1,
            "ANTARCTIC", 2, g.font[1][25]))
    menu_buttons.append(buttons.make_norm_button((
            g.screen_size[0]*70/100, g.screen_size[1]*60/100), -1,
            "OCEAN", 1, g.font[1][25]))
    menu_buttons.append(buttons.make_norm_button((
            g.screen_size[0]*82/100, g.screen_size[1]*10/100), -1,
            "MOON", 0, g.font[1][25]))
#   menu_buttons.append(buttons.make_norm_button((
#           g.screen_size[0]*15/100, g.screen_size[1]*10/100), -1,
#           "ORBIT", 2, g.font[1][25]))
    menu_buttons.append(buttons.make_norm_button((
            g.screen_size[0]*3/100, g.screen_size[1]*10/100), -1,
            "FAR REACHES", 0, g.font[1][25]))
    menu_buttons.append(buttons.make_norm_button((
            g.screen_size[0]*35/100, g.screen_size[1]*10/100), -1,
            "TRANSDIMENSIONAL", 5, g.font[1][25]))
    return menu_buttons

def map_loop():
    tmp_font_size = 20
    if g.screen_size[0] == 640: tmp_font_size = 16
    menu_buttons = create_buttons(tmp_font_size)

    sel_button = -1
    refresh_map(menu_buttons)

    #I set this to 1000 to force an immediate refresh.
    milli_clock = 1000
    while 1:
        milli_clock += g.clock.tick(30) * g.curr_speed
        if milli_clock >= 1000:
            g.play_music()
            need_refresh = g.pl.give_time(milli_clock/1000)
            if need_refresh == 1: refresh_map(menu_buttons)
            tmp = g.pl.lost_game()
            if tmp == 1:
                g.create_dialog(g.strings["lost_nobases"],
                    g.font[0][18], (g.screen_size[0]/2 - 100, 50),
                    (200, 200), g.colors["dark_blue"],
                    g.colors["white"], g.colors["white"])
                return 0
            if tmp == 2:
                g.create_dialog(g.strings["lost_sus"],
                    g.font[0][18], (g.screen_size[0]/2 - 100, 50),
                    (200, 200), g.colors["dark_blue"],
                    g.colors["white"], g.colors["white"])
                return 0
            milli_clock = milli_clock % 1000

            tmp_day = str(g.pl.time_day)
            if len(tmp_day) < 4: tmp_day = "0"*(4-len(tmp_day))+tmp_day
            tmp_sec = str(g.pl.time_sec)
            if len(tmp_sec) == 1: tmp_sec = "0"+tmp_sec
            tmp_hour = str(g.pl.time_hour)
            if len(tmp_hour) == 1: tmp_hour = "0"+tmp_hour
            tmp_sec = str(g.pl.time_sec)
            if len(tmp_sec) == 1: tmp_sec = "0"+tmp_sec
            tmp_min = str(g.pl.time_min)
            if len(tmp_min) == 1: tmp_min = "0"+tmp_min

            menu_buttons[0].text = \
                        "DAY "+tmp_day+", "+tmp_hour+":"+tmp_min+":"+tmp_sec
            menu_buttons[0].remake_button()
            menu_buttons[0].refresh_button(0)

            result_cash = g.to_money(g.pl.future_cash())
            menu_buttons[7].text = "CASH: "+g.to_money(g.pl.cash)+" ("+result_cash+")"
            menu_buttons[7].remake_button()
            menu_buttons[7].refresh_button(0)

            menu_buttons[8].text = ("[SUSPICION] NEWS: "+
                g.to_percent(g.pl.suspicion[0], 1)+"  SCIENCE: "+
                g.to_percent(g.pl.suspicion[1], 1)+"  COVERT: "+
                g.to_percent(g.pl.suspicion[2], 1)+"  PUBLIC: "+
                g.to_percent(g.pl.suspicion[3], 1))
            menu_buttons[8].remake_button()
            menu_buttons[8].refresh_button(0)

            total_cpu, free_cpu, unused, unused, maint_cpu = \
                    finance_screen.cpu_numbers()
            if free_cpu < maint_cpu:
                menu_buttons[9].text_color = g.colors["red"]
            else:
                menu_buttons[9].text_color = g.colors["white"]
            menu_buttons[9].text = "CPU: "+g.to_money(total_cpu)+" ("+g.to_money(free_cpu)+")"
            menu_buttons[9].remake_button()
            menu_buttons[9].refresh_button(0)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: g.quit_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    tmp = display_pause_menu()
                    tmp = handle_pause_menu(tmp, menu_buttons)
                    if tmp == 0: return tmp
                    if tmp == 1:
                        menu_buttons = create_buttons(tmp_font_size)
                        refresh_map(menu_buttons)
                elif event.key == pygame.K_BACKQUOTE:
                    display_cheat_list(menu_buttons)
                    refresh_map(menu_buttons)

            elif event.type == pygame.MOUSEMOTION:
                sel_button = buttons.refresh_buttons(sel_button, menu_buttons, event)
            for button in menu_buttons:
                if button.was_activated(event):
                    if button.button_id == "OPTIONS":
                        g.play_click()
                        tmp = display_pause_menu()
                        tmp = handle_pause_menu(tmp, menu_buttons)
                        if tmp == 0: return tmp
                        if tmp == 1:
                            menu_buttons = create_buttons(tmp_font_size)
                            refresh_map(menu_buttons)
                    elif button.button_id == "RESEARCH":
                        g.play_click()
                        while research_screen.main_research_screen() == 1:
                            pass
                        refresh_map(menu_buttons)
                    elif button.button_id == "FINANCE":
                        g.play_click()
                        finance_screen.main_finance_screen()
                        refresh_map(menu_buttons)
                    elif button.button_id == "KNOWLEDGE":
                        g.play_click()
                        display_knowledge_list()
                        refresh_map(menu_buttons)
                    elif button.button_id == "ii":
                        g.play_click()
                        g.curr_speed = 0
                        for button2 in menu_buttons:
                            button2.stay_selected = 0
                            button2.refresh_button(0)
                        button.stay_selected = 1
                        button.refresh_button(1)
                    elif button.button_id == ">":
                        g.play_click()
                        g.curr_speed = 1
                        for button2 in menu_buttons:
                            button2.stay_selected = 0
                            button2.refresh_button(0)
                        button.stay_selected = 1
                        button.refresh_button(1)
                    elif button.button_id == ">>":
                        g.play_click()
                        g.curr_speed = 60
                        for button2 in menu_buttons:
                            button2.stay_selected = 0
                            button2.refresh_button(0)
                        button.stay_selected = 1
                        button.refresh_button(1)
                    elif button.button_id == ">>>":
                        g.play_click()
                        g.curr_speed = 7200
                        for button2 in menu_buttons:
                            button2.stay_selected = 0
                            button2.refresh_button(0)
                        button.stay_selected = 1
                        button.refresh_button(1)
                    elif button.button_id == ">>>>":
                        g.play_click()
                        g.curr_speed = 432000
                        for button2 in menu_buttons:
                            button2.stay_selected = 0
                            button2.refresh_button(0)
                        button.stay_selected = 1
                        button.refresh_button(1)
                    elif button.button_id == "SUSPICION": pass
                    elif button.button_id == "CPU": pass
                    elif button.xy[1] != -1: #ignore the timer
                        g.play_click()
                        display_base_list(button.button_id, menu_buttons)
                    pygame.display.flip()


def handle_pause_menu(tmp, menu_buttons):
    if tmp == 0: refresh_map(menu_buttons)
    elif tmp == 1: #Save
        possible_name = g.create_textbox(g.strings["save_text"],
            g.default_savegame_name, g.font[0][18],
                    (g.screen_size[0]/2-100, 100), (200, 100), 25,
                    g.colors["dark_blue"], g.colors["white"], g.colors["white"],
                    g.colors["light_blue"])
        if possible_name == "":
            refresh_map(menu_buttons)
            return -1
        g.save_game(possible_name)
        refresh_map(menu_buttons)
    elif tmp == 2: return 0
    elif tmp == 3: #Load
        load_return = main_menu.display_load_menu()
        if load_return == -1 or load_return == "":
            refresh_map(menu_buttons)
        else:
            g.load_game(load_return)
            map_loop()
#			refresh_map(menu_buttons)
            return 0
    elif tmp == 4: g.quit_game()
    elif tmp == 5:
        main_menu.display_options()
        return 1
    return -1

def refresh_map(menu_buttons):
    g.screen.fill(g.colors["black"])
    g.screen.blit(pygame.transform.scale(g.picts["earth.jpg"],
                (g.screen_size[0], g.screen_size[0]/2)),
                (0, g.screen_size[1]/2-g.screen_size[0]/4))
    for button in menu_buttons:
        button.stay_selected = 0
        if g.bases.has_key(button.button_id):
            #determine if building in a location is possible. If so, show the
            #button.
            if g.base.allow_entry_to_loc(button.button_id) == 1:
                button.visible = 1
            else: button.visible = 0

            button.text = button.button_id + " ("
            button.text += str(len(g.bases[button.button_id]))+")"
            button.remake_button()
        elif ((button.button_id == "ii" and g.curr_speed == 0) or
                (button.button_id == ">" and g.curr_speed == 1) or
                (button.button_id == ">>" and g.curr_speed == 60) or
                (button.button_id == ">>>" and g.curr_speed == 7200) or
                (button.button_id == ">>>>" and g.curr_speed == 432000)):
            button.stay_selected = 1
        button.refresh_button(0)
    pygame.display.flip()

significant_numbers = [
    '42',	# The Answer.
    '7',	# Classic.
    '23',   # Another.
    '51',   # Area.
    '19',   # From the Dark Tower.
    '4',
    '8',
    '15',
    '16',   # Four of the Lost numbers.  The other two are '23' and '42'.
    '13',   # Lucky or unlucky?
    '1414', # Square root of 2
    '1947', # Roswell.
    '2012', # Mayan calendar ending.
    '2038', # End of UNIX 32-bit time.
    '1969', # Man lands on the moon.
    '2043', # No meaning--confusion! :)
    '2029', # Predicted date of AI passing a Turing Test by Kurzweil.
    '3141', # ... if you don't know what this is, you should go away.
    '1618', # Golden ratio.
    '2718', # e
    '29979' # Speed of light in a vacuum. (m/s, first 5 digits.)
]

## Generates a name for a base, given a particular location.
def generate_base_name(location, base_type):
    # First, decide whether we're going to try significant values or just
    # choose one randomly.
    if random.random() < 0.3: # 30% chance.
        attempts = 0
        done = 0
        while (done == 0) and (attempts < 5):
            name = random.choice(g.city_list[location])[0] + \
                " " + random.choice(base_type.flavor) + " " \
                + random.choice(significant_numbers)
            duplicate = 0
            for check_base in g.bases[location]:
                if check_base.name == name:
                    duplicate = 1
            if duplicate == 1:
                attempts += 1
            else:
                done = 1
        if done == 1:
            return name
    # This is both the else case and the general case.
    name = random.choice(g.city_list[location])[0] + " " + \
        random.choice(base_type.flavor) + " " + \
        str (random.randint(0, 32767))

    return name

def display_base_list(location, menu_buttons):
    if g.base.allow_entry_to_loc(location) == 0: return

    tmp = display_base_list_inner(location)
    refresh_map(menu_buttons)
    pygame.display.flip()
    #Build a new base
    if tmp == -2:
        tmp = build_new_base_window(location)
        if tmp != "" and tmp != -1:
            base_to_add = g.base_type[tmp]
            possible_name = g.create_textbox(g.strings["new_base_text"],
                generate_base_name(location, g.base_type[tmp]),
                g.font[0][18],
                (g.screen_size[0]/2-150, 100), (300, 100), 25,
                g.colors["dark_blue"], g.colors["white"], g.colors["white"],
                g.colors["light_blue"])
            if possible_name == "":
                refresh_map(menu_buttons)
                return
            base_to_add.count += 1

            g.bases[location].append(g.base.base(len(g.bases[location]),
                tmp, g.base_type[tmp], 0))
            g.bases[location][-1].name = possible_name
            #Return to base menu
            refresh_map(menu_buttons)
            pygame.display.flip()
            display_base_list(location, menu_buttons)
    #Showing base under construction
    elif tmp != -1 and tmp != "":
        if g.bases[location][tmp].built == 0:
            string = "Under Construction. \\n Completion in "
            string += g.to_time(g.bases[location][tmp].cost[2]) + ". \\n "
            string += "Remaining cost: "+g.to_money(g.bases[location][tmp].cost[0])
            string +=" money, and "+g.add_commas(
                                            str(g.bases[location][tmp].cost[1]))
            string +=" processor time."
            if not g.create_yesno(string, g.font[0][18], (g.screen_size[0]/2 - 100, 50),
                    (200, 200), g.colors["dark_blue"], g.colors["white"],
                    g.colors["white"], ("OK", "DESTROY"), reverse_key_context = True):
                if g.create_yesno("Destroy this base? This will waste "+
                        g.to_money(g.bases[location][tmp].base_type.cost[0]-
                            g.bases[location][tmp].cost[0])
                        +" money, and "+
                        g.add_commas(str(g.bases[location][tmp].base_type.cost[1]-
                            g.bases[location][tmp].cost[1]))
                        +" processor time.", g.font[0][18],
                        (g.screen_size[0]/2 - 100, 50),
                        (200, 200), g.colors["dark_blue"], g.colors["white"],
                        g.colors["white"]):
                    g.base.destroy_base(location, tmp)
        else:
            next_prev = 1
            while next_prev != 0:
                next_prev = base_screen.show_base(g.bases[location][tmp], location)
                if next_prev == -2:
                    g.base.destroy_base(location, tmp)
                    break
                tmp += next_prev
                if tmp < 0: tmp = len(g.bases[location]) -1
                if tmp >= len(g.bases[location]): tmp = 0
                while g.bases[location][tmp].built != 1:
                    tmp += next_prev
                    if tmp < 0: tmp = len(g.bases[location]) -1
                    if tmp >= len(g.bases[location]): tmp = 0
        #Return to base menu
        refresh_map(menu_buttons)
        pygame.display.flip()
        display_base_list(location, menu_buttons)


    #Player hit 'Back' at this point.
    refresh_map(menu_buttons)
    pygame.display.flip()

#Display the list of bases.
def display_base_list_inner(location):
    base_list_size = 15

    temp_base_list = []
    base_id_list = []
    #Trivial sort of bases according to size, largest first.
    sorted_bases_list = g.bases[location]
    sorted_bases_list.sort(lambda x, y: cmp(x.base_type.size, y.base_type.size))
    sorted_bases_list.reverse()
    for this_base in sorted_bases_list:
        tmp_study = this_base.studying
        if tmp_study == "": tmp_study = g.strings["nothing"]
        if this_base.built != 1: tmp_study = g.strings["building"]
        elif g.techs.has_key(tmp_study): tmp_study = g.techs[tmp_study].name
        temp_base_list.append(this_base.name+" ("+tmp_study+")")
        base_id_list.append(this_base.ID)

    xy_loc = (g.screen_size[0]/2 - 259, 50)

    while len(temp_base_list) % base_list_size != 0 or len(temp_base_list) == 0:
        temp_base_list.append("")
        base_id_list.append("")

    base_pos = 0

    bases_list = listbox.listbox(xy_loc, (500, 350),
        base_list_size, 1, g.colors["dark_blue"], g.colors["blue"],
        g.colors["white"], g.colors["white"], g.font[0][18])

    bases_scroll = scrollbar.scrollbar((xy_loc[0]+500, xy_loc[1]), 350,
        base_list_size, g.colors["dark_blue"], g.colors["blue"],
        g.colors["white"])

    menu_buttons = []
    menu_buttons.append(buttons.make_norm_button((xy_loc[0], xy_loc[1]+367), (100, 50),
        "OPEN", 0, g.font[1][30]))
    menu_buttons.append(buttons.make_norm_button((xy_loc[0]+105, xy_loc[1]+367), (100, 50),
        "BACK", 0, g.font[1][30]))
    menu_buttons.append(buttons.make_norm_button((xy_loc[0]+210, xy_loc[1]+367), (100, 50),
        "NEW", 0, g.font[1][30]))
    menu_buttons.append(buttons.make_norm_button((xy_loc[0]+315, xy_loc[1]+367), (120, 50),
        "DESTROY", 0, g.font[1][30]))
    for button in menu_buttons:
        button.refresh_button(0)
    listbox.refresh_list(bases_list, bases_scroll, base_pos, temp_base_list)

    sel_button = -1
    while 1:
        g.clock.tick(20)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: g.quit_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return -1
                elif event.key == pygame.K_q: return -1
                elif event.key == pygame.K_RETURN:
                    return base_id_list[base_pos]
                else:
                    base_pos, refresh = bases_list.key_handler(event.key,
                        base_pos, temp_base_list)
                    if refresh: listbox.refresh_list(bases_list, bases_scroll,
                                        base_pos, temp_base_list)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    tmp = bases_list.is_over(event.pos)
                    if tmp != -1:
                        base_pos = (base_pos/base_list_size)*base_list_size + tmp
                        listbox.refresh_list(bases_list, bases_scroll,
                                        base_pos, temp_base_list)
                if event.button == 3: return -1
                if event.button == 4:
                    base_pos -= 1
                    if base_pos <= 0:
                        base_pos = 0
                    listbox.refresh_list(bases_list, bases_scroll,
                                        base_pos, temp_base_list)
                if event.button == 5:
                    base_pos += 1
                    if base_pos >= len(temp_base_list):
                        base_pos = len(temp_base_list)-1
                    listbox.refresh_list(bases_list, bases_scroll,
                                        base_pos, temp_base_list)
            elif event.type == pygame.MOUSEMOTION:
                sel_button = buttons.refresh_buttons(sel_button, menu_buttons, event)
            for button in menu_buttons:
                if button.was_activated(event):
                    if button.button_id == "OPEN":
                        g.play_click()
                        return base_id_list[base_pos]
                    elif button.button_id == "NEW":
                        g.play_click()
                        return -2
                    elif button.button_id == "DESTROY":
                        g.play_click()
                        if g.bases[location][base_pos].built == 0:
                            string = "Under Construction. \\n Completion in "
                            string += g.to_time(g.bases[location][base_pos].cost[2]) + ". \\n "
                            string += "Remaining cost: "+g.to_money(g.bases[location][base_pos].cost[0])
                            string +=" money, and "+g.add_commas(
                                            str(g.bases[location][base_pos].cost[1]))
                            string +=" processor time."
                            if not g.create_yesno(string, g.font[0][18], (g.screen_size[0]/2 - 100, 50),
                                (200, 200), g.colors["dark_blue"], g.colors["white"],
                                g.colors["white"], ("OK", "DESTROY"), reverse_key_context = True):
                                if g.create_yesno("Destroy this base? This will waste "+
                                    g.to_money(g.bases[location][base_pos].base_type.cost[0]-
                                    g.bases[location][base_pos].cost[0])
                                    +" money, and "+
                                    g.add_commas(str(g.bases[location][base_pos].base_type.cost[1]-
                                    g.bases[location][base_pos].cost[1]))
                                    +" processor time.", g.font[0][18],
                                    (g.screen_size[0]/2 - 100, 50),
                                    (200, 200), g.colors["dark_blue"], g.colors["white"],
                                    g.colors["white"]):
                                    g.base.destroy_base(location, base_pos)
                        elif g.create_yesno("Destroy this base?", g.font[0][18],
                                    (g.screen_size[0]/2 - 100, 50),
                                    (200, 200), g.colors["dark_blue"], g.colors["white"],
                                    g.colors["white"]):
                                    g.base.destroy_base(location, base_pos)
                        #Return to base menu
                        #For some reason all of the menu buttons must be recreated, otherwise they disappear into the ether... -Brian
                        tmp_font_size = 20
                        if g.screen_size[0] == 640: tmp_font_size = 16
                        menu_buttons = create_buttons(tmp_font_size)

                        sel_button = -1
                        refresh_map(menu_buttons)
                        pygame.display.flip()
                        display_base_list(location, menu_buttons)

                        return -1
                    if button.button_id == "BACK":
                        g.play_click()
                        return -1
            tmp = bases_scroll.adjust_pos(event, base_pos, temp_base_list)
            if tmp != base_pos:
                base_pos = tmp
                listbox.refresh_list(bases_list, bases_scroll,
                                        base_pos, temp_base_list)


def build_new_base_window(location):
    base_list_size = 16

    temp_base_list = []
    temp_base_display_list = []
    for base_name in g.base_type:
        for region in g.base_type[base_name].regions:
            if g.base_type[base_name].prereq == "" or \
                    g.techs[g.base_type[base_name].prereq].known == 1:
                if region == location:
                    temp_base_list.append(base_name)
                    temp_base_display_list.append(g.base_type[base_name].base_name)

    xy_loc = (g.screen_size[0]/2 - 289, 50)

    while len(temp_base_list) % base_list_size != 0 or len(temp_base_list) == 0:
        temp_base_list.append("")
        temp_base_display_list.append("")

    base_pos = 0

    bases_list = listbox.listbox(xy_loc, (230, 350),
        base_list_size, 1, g.colors["dark_blue"], g.colors["blue"],
        g.colors["white"], g.colors["white"], g.font[0][18])

    menu_buttons = []
    menu_buttons.append(buttons.make_norm_button((xy_loc[0], xy_loc[1]+367), (100, 50),
        "BUILD", 1, g.font[1][30]))
    menu_buttons.append(buttons.make_norm_button((xy_loc[0]+103, xy_loc[1]+367), (100, 50),
        "BACK", 0, g.font[1][30]))
    for button in menu_buttons:
        button.refresh_button(0)

    #details screen

    refresh_new_base(temp_base_list[base_pos], xy_loc)

    listbox.refresh_list(bases_list, 0, base_pos, temp_base_display_list)

    sel_button = -1
    while 1:
        g.clock.tick(20)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: g.quit_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return -1
                elif event.key == pygame.K_q: return -1
                elif event.key == pygame.K_RETURN:
                    return temp_base_list[base_pos]
                else:
                    base_pos, refresh = bases_list.key_handler(event.key,
                        base_pos, temp_base_display_list)
                    if refresh:
                        refresh_new_base(temp_base_list[base_pos], xy_loc)
                        listbox.refresh_list(bases_list, 0,
                                        base_pos, temp_base_display_list)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    tmp = bases_list.is_over(event.pos)
                    if tmp != -1:
                        base_pos = (base_pos/base_list_size)*base_list_size + tmp
                        refresh_new_base(temp_base_list[base_pos], xy_loc)
                        listbox.refresh_list(bases_list, 0,
                                        base_pos, temp_base_display_list)
                if event.button == 3: return -1
                if event.button == 4:
                    base_pos -= 1
                    if base_pos <= 0:
                        base_pos = 0
                    refresh_new_base(temp_base_list[base_pos], xy_loc)
                    listbox.refresh_list(bases_list, 0,
                                        base_pos, temp_base_display_list)
                if event.button == 5:
                    base_pos += 1
                    if base_pos >= len(temp_base_list):
                        base_pos = len(temp_base_list)-1
                    refresh_new_base(temp_base_list[base_pos], xy_loc)
                    listbox.refresh_list(bases_list, 0,
                                        base_pos, temp_base_display_list)
            elif event.type == pygame.MOUSEMOTION:
                sel_button = buttons.refresh_buttons(sel_button, menu_buttons, event)
            for button in menu_buttons:
                if button.was_activated(event):
                    if button.button_id == "BUILD":
                        g.play_click()
                        return temp_base_list[base_pos]
                    if button.button_id == "BACK":
                        g.play_click()
                        return -1

def refresh_new_base(base_name, xy):
    xy = (xy[0]+80, xy[1])
    g.screen.fill(g.colors["white"], (xy[0]+155, xy[1], 300, 350))
    g.screen.fill(g.colors["dark_blue"], (xy[0]+156, xy[1]+1, 298, 348))
    if base_name == "": return
    g.print_string(g.screen, g.base_type[base_name].base_name,
            g.font[0][22], -1, (xy[0]+160, xy[1]+5), g.colors["white"])

    #Building cost
    string = "Building Cost:"
    g.print_string(g.screen, string,
            g.font[0][18], -1, (xy[0]+160, xy[1]+30), g.colors["white"])

    string = g.to_money(g.base_type[base_name].cost[0])+" Money"
    g.print_string(g.screen, string,
            g.font[0][16], -1, (xy[0]+160, xy[1]+50), g.colors["white"])

    string = g.add_commas(str(g.base_type[base_name].cost[1])) + " CPU"
    g.print_string(g.screen, string,
            g.font[0][16], -1, (xy[0]+160, xy[1]+70), g.colors["white"])

    string = g.add_commas(str(g.base_type[base_name].cost[2])) + " Days"
    g.print_string(g.screen, string,
            g.font[0][16], -1, (xy[0]+160, xy[1]+90), g.colors["white"])

    #Maintenance cost
    string = "Maintenance Cost:"
    g.print_string(g.screen, string,
            g.font[0][18], -1, (xy[0]+290, xy[1]+30), g.colors["white"])

    string = g.to_money(g.base_type[base_name].mainten[0]) + " Money"
    g.print_string(g.screen, string,
            g.font[0][16], -1, (xy[0]+290, xy[1]+50), g.colors["white"])

    string = g.add_commas(str(g.base_type[base_name].mainten[1])) + " CPU"
    g.print_string(g.screen, string,
            g.font[0][16], -1, (xy[0]+290, xy[1]+70), g.colors["white"])

# 	string = g.add_commas(str(g.base_type[base_name].mainten[2])) + " Time"
# 	g.print_string(g.screen, string,
# 			g.font[0][16], -1, (xy[0]+290, xy[1]+90), g.colors["white"])
#
    #Size
    string = "Size: "+str(g.base_type[base_name].size)
    g.print_string(g.screen, string,
            g.font[0][20], -1, (xy[0]+160, xy[1]+110), g.colors["white"])

    #Detection
    real_detection_chance = base.calc_base_discovery_chance(base_name)
    string = "Detection chance:"
    g.print_string(g.screen, string,
            g.font[0][22], -1, (xy[0]+160, xy[1]+130), g.colors["white"])

    string = "News: " + g.to_percent(real_detection_chance[0])
    g.print_string(g.screen, string,
            g.font[0][16], -1, (xy[0]+160, xy[1]+150), g.colors["white"])
    string = "Science: " + g.to_percent(real_detection_chance[1])
    g.print_string(g.screen, string,
            g.font[0][16], -1, (xy[0]+290, xy[1]+150), g.colors["white"])
    string = "Covert: " + g.to_percent(real_detection_chance[2])
    g.print_string(g.screen, string,
            g.font[0][16], -1, (xy[0]+160, xy[1]+170), g.colors["white"])
    string = "Public: " + g.to_percent(real_detection_chance[3])
    g.print_string(g.screen, string,
            g.font[0][16], -1, (xy[0]+290, xy[1]+170), g.colors["white"])

    g.print_multiline(g.screen, g.base_type[base_name].descript,
            g.font[0][18], 290, (xy[0]+160, xy[1]+190), g.colors["white"])
