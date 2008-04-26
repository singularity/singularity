#file: base_screen.py
#Copyright (C) 2005, 2006, 2007 Evil Mr Henry, Phil Bordelon, and Brian Reid
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

#This file contains the screen to display the base screen.


import pygame
import g
import buttons
import scrollbar
import listbox

#cost = (money, ptime, labor)
#detection = (news, science, covert, person)

def show_base(this_base, location):
    #Border
    g.screen.fill(g.colors["black"])

    menu_buttons = []
    menu_buttons.append(buttons.make_norm_button((0, 0), (70, 25),
        "BACK", "B", g.font[1][20]))

    menu_buttons.append(buttons.button((0, g.screen_size[1]-25),
        (g.screen_size[0], 25), "DETECTION CHANCE", "",
        g.colors["black"], g.colors["dark_blue"], g.colors["black"],
        g.colors["white"], g.font[1][15]))

    menu_buttons.append(buttons.make_norm_button((0, g.screen_size[1]-50),
        (170, 25), "CHANGE RESEARCH", "C", g.font[1][20], "CHANGE"))

    menu_buttons.append(buttons.button((0, 25),
        (g.screen_size[0], 25),
        "STUDYING:", "", g.colors["black"], g.colors["dark_blue"],
        g.colors["black"], g.colors["white"], g.font[1][15]))

    menu_buttons.append(buttons.make_norm_button((320, 60), (70, 26),
        "CHANGE", "P", g.font[1][15], "C_PROCESSOR"))

    menu_buttons.append(buttons.make_norm_button((320, 110), (70, 26),
        "CHANGE", "R", g.font[1][15], "C_REACTOR"))

    menu_buttons.append(buttons.make_norm_button((320, 160), (70, 26),
        "CHANGE", "N", g.font[1][15], "C_NETWORK"))
    menu_buttons[6].activate_key = "n"

    menu_buttons.append(buttons.make_norm_button((320, 210),
        (70, 26), "CHANGE", "S", g.font[1][15], "C_SECURITY"))

    menu_buttons.append(buttons.make_norm_button((g.screen_size[0]-40,
        0), (20, 25), "<", "<", g.font[1][20]))

    menu_buttons.append(buttons.make_norm_button((g.screen_size[0]-20,
        0), (20, 25), ">", ">", g.font[1][20]))

    menu_buttons.append(buttons.make_norm_button((g.screen_size[0]-90,
        g.screen_size[1]-50), (90, 25), "DESTROY", "D", g.font[1][20]))

    menu_buttons.append(buttons.button((70, -1), (g.screen_size[0]-145,
        25), "BASE NAME", "", g.colors["black"], g.colors["black"],
        g.colors["black"], g.colors["white"], g.font[1][15]))

    sel_button = -1

    refresh_base(menu_buttons, this_base)
    while 1:
        g.clock.tick(20)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: g.quit_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return 0
            elif event.type == pygame.MOUSEMOTION:
                sel_button = buttons.refresh_buttons(sel_button, menu_buttons, event)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                g.play_sound("click")
                return 0
            for button in menu_buttons:
                if button.was_activated(event):
                    if button.button_id == "BACK":
                        g.play_sound("click")
                        return 0
                    if button.button_id == "CHANGE":
                        g.play_sound("click")
                        change_tech(this_base)
                        refresh_base(menu_buttons, this_base)
                    elif button.button_id == "C_PROCESSOR":
                        g.play_sound("click")
                        build_item(this_base, "compute", location)
                        refresh_base(menu_buttons, this_base)
                    elif button.button_id == "C_REACTOR":
                        g.play_sound("click")
                        build_item(this_base, "react", location)
                        refresh_base(menu_buttons, this_base)
                    elif button.button_id == "C_NETWORK":
                        g.play_sound("click")
                        build_item(this_base, "network", location)
                        refresh_base(menu_buttons, this_base)
                    elif button.button_id == "C_SECURITY":
                        g.play_sound("click")
                        build_item(this_base, "security", location)
                        refresh_base(menu_buttons, this_base)
                    elif button.button_id == "<":
                        g.play_sound("click")
                        return -1
                    elif button.button_id == ">":
                        g.play_sound("click")
                        return 1
                    elif button.button_id == "DESTROY":
                        if g.create_yesno(g.strings["really_destroy"],
                                g.font[0][18], (100, 100), (150, 100),
                                g.colors["blue"], g.colors["white"],
                                g.colors["white"]):
                            g.play_sound("click")
                            return -2
                        else: refresh_base(menu_buttons, this_base)
                    elif button.xy[1] != -1 and button.xy[1] != 25 and \
                            button.xy[1] != g.screen_size[1]-25:
                        if button.xy[0] == event.pos[0] or \
                                button.xy[1] == event.pos[1]: continue
                        g.play_sound("click")
                        build_item(this_base, location)
                        refresh_base(menu_buttons, this_base)

def refresh_base(menu_buttons, this_base):
    g.screen.fill(g.colors["black"])
# 	xstart = g.screen_size[0]/2-this_base.this_type.size[0]*9
# 	ystart = g.screen_size[1]/2-this_base.this_type.size[1]*9
    xstart = 10
    ystart = 50

    #base name display
    menu_buttons[11].text = this_base.name
    menu_buttons[11].remake_button()

    #detection chance display
    detect_chance = this_base.get_detect_chance()
    menu_buttons[1].text = g.strings["detect_chance"]+" NEWS: "+ \
        g.to_percent(detect_chance.get("news", 0))+"  SCIENCE: "+ \
        g.to_percent(detect_chance.get("science", 0))+"  COVERT: "+ \
        g.to_percent(detect_chance.get("covert", 0))+"  PUBLIC: "+ \
        g.to_percent(detect_chance.get("public", 0))
    menu_buttons[1].remake_button()

    #research display
    if this_base.studying != "" and this_base.studying != "Construction":
        if not g.jobs.has_key(this_base.studying):
            if g.techs[this_base.studying].done: 
                this_base.studying = ""

    action_display_string = "STUDYING: "

    study_display_string = this_base.studying
    if study_display_string == "":
        study_display_string = "NOTHING"
    elif study_display_string == "Construction":
        study_display_string = "CONSTRUCTION"
    elif g.jobs.has_key(study_display_string):
        action_display_string = "WORKING: "
    elif g.techs.has_key(study_display_string):
        study_display_string = g.techs[study_display_string].name
    menu_buttons[3].text = action_display_string + study_display_string
    menu_buttons[3].remake_button()
    #Item display
    g.screen.fill(g.colors["white"], (xstart, ystart, 300, g.screen_size[1]-150))
    g.screen.fill(g.colors["dark_blue"], (xstart+1, ystart+1, 298, g.screen_size[1]-152))

    if this_base.cpus[0] == 0: item_name = "None"
    else: item_name = this_base.cpus[0].type.name+" x "+str(this_base.has_item())
    g.print_string(g.screen, "Processor: " + item_name,
        g.font[0][18], -1, (xstart+5, ystart+15), g.colors["white"])
    if this_base.cpus[len(this_base.cpus)-1] != 0:
        if not this_base.cpus[len(this_base.cpus)-1].done:
            g.print_string(g.screen, "Completion in " +
                g.to_time(this_base.cpus[len(this_base.cpus)-1].cost_left[2]),
                g.font[0][18], -1, (xstart+5, ystart+30), g.colors["white"])

    if this_base.extra_items[0] == 0: item_name = "None"
    else: item_name = this_base.extra_items[0].type.name
    g.print_string(g.screen, "Reactor: " + item_name,
        g.font[0][18], -1, (xstart+5, ystart+65), g.colors["white"])
    if this_base.extra_items[0] != 0:
        if not this_base.extra_items[0].done:
            g.print_string(g.screen, "Completion in " +
                g.to_time(this_base.extra_items[0].cost_left[2]),
                g.font[0][18], -1, (xstart+5, ystart+80), g.colors["white"])

    if this_base.extra_items[1] == 0: item_name = "None"
    else: item_name = this_base.extra_items[1].type.name
    g.print_string(g.screen, "Network: " + item_name,
        g.font[0][18], -1, (xstart+5, ystart+115), g.colors["white"])
    if this_base.extra_items[1] != 0:
        if not this_base.extra_items[1].done:
            g.print_string(g.screen, "Completion in " +
                g.to_time(this_base.extra_items[1].cost_left[2]),
                g.font[0][18], -1, (xstart+5, ystart+130), g.colors["white"])

    if this_base.extra_items[2] == 0: item_name = "None"
    else: item_name = this_base.extra_items[2].type.name
    g.print_string(g.screen, "Security: " + item_name,
        g.font[0][18], -1, (xstart+5, ystart+165), g.colors["white"])
    if this_base.extra_items[2] != 0:
        if not this_base.extra_items[2].done:
            g.print_string(g.screen, "Completion in " +
                g.to_time(this_base.extra_items[2].cost_left[2]),
                g.font[0][18], -1, (xstart+5, ystart+190), g.colors["white"])

    for button in menu_buttons:
        button.refresh_button(0)
    pygame.display.flip()


def build_item(this_base, item_type, location):
    if this_base.type.size == 1:
        g.create_dialog(g.strings["unbuildable"])
        return 0

    list_size = 10

    # The object list will hold all of the actual item types buildable.
    item_object_list = []

    # The ID list holds the 'IDs' of each item, used to refer back to the
    # source objects.
    item_id_list = []

    # The display list holds the display names for each object, potentially
    # localised into the native language.
    item_display_list = []

    # First we determine the list of items that can actually be built here ...
    for item_name in g.items:
        if g.items[item_name].item_type == item_type:
            if g.items[item_name].prerequisites != "":
                if not g.techs[g.items[item_name].prerequisites].done:
                    continue
            try: g.items[item_name].buildable.index(location)
            except ValueError: continue
            item_object_list.append(g.items[item_name])

    # ... then we sort that list.  Items sort by cost comparison.  We want to
    # display the most expensive objects at the top, as they are typically
    # what a person wants to build.
    item_object_list.sort()
    item_object_list.reverse()

    # Finally we build the id_list and display_list from the sorted objects.
    item_id_list = [x.id for x in item_object_list]
    item_display_list = [x.name for x in item_object_list]

    xy_loc = (g.screen_size[0]/2 - 300, 50)
    while len(item_id_list) % list_size != 0 or len(item_id_list) == 0:
        item_id_list.append("")
        item_display_list.append("")

    list_pos = 0

    item_id_listbox = listbox.listbox(xy_loc, (250, 300),
        list_size, 1, g.colors["dark_blue"], g.colors["blue"],
        g.colors["white"], g.colors["white"], g.font[0][18])

    item_scroll = scrollbar.scrollbar((xy_loc[0]+250, xy_loc[1]), 300,
        list_size, g.colors["dark_blue"], g.colors["blue"],
        g.colors["white"])

    menu_buttons = []
    menu_buttons.append(buttons.make_norm_button((xy_loc[0], xy_loc[1]+367),
        (100, 50), "BUILD", "U", g.font[1][30]))
    menu_buttons.append(buttons.make_norm_button((xy_loc[0]+103, xy_loc[1]+367),
        (100, 50), "BACK", "B", g.font[1][30]))
    for button in menu_buttons:
        button.refresh_button(0)

    refresh_item(this_base, item_id_list[list_pos], xy_loc)
    listbox.refresh_list(item_id_listbox, item_scroll, list_pos, item_display_list)

    sel_button = -1
    while 1:
        g.clock.tick(20)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: g.quit_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return -1
                elif event.key == pygame.K_q: return -1
                elif event.key == pygame.K_RETURN:
                    actual_build(this_base, item_id_list[list_pos], item_type)
                    return
                else:
                    list_pos, refresh = item_id_listbox.key_handler(event.key,
                        list_pos, item_display_list)
                    if refresh:
                        refresh_item(this_base, item_id_list[list_pos], xy_loc)
                        listbox.refresh_list(item_id_listbox, item_scroll,
                                        list_pos, item_display_list)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    selection = item_id_listbox.is_over(event.pos)
                    if selection != -1:
                        list_pos = (list_pos / list_size)*list_size + selection
                        refresh_item(this_base, item_id_list[list_pos], xy_loc)
                        listbox.refresh_list(item_id_listbox, item_scroll,
                                        list_pos, item_display_list)
                if event.button == 3: return -1
                if event.button == 4:
                    list_pos -= 1
                    if list_pos <= 0:
                        list_pos = 0
                    refresh_item(this_base, item_id_list[list_pos], xy_loc)
                    listbox.refresh_list(item_id_listbox, item_scroll,
                                        list_pos, item_display_list)
                if event.button == 5:
                    list_pos += 1
                    if list_pos >= len(item_id_list):
                        list_pos = len(item_id_list)-1
                    refresh_item(this_base, item_id_list[list_pos], xy_loc)
                    listbox.refresh_list(item_id_listbox, item_scroll,
                                        list_pos, item_display_list)
            elif event.type == pygame.MOUSEMOTION:
                sel_button = buttons.refresh_buttons(sel_button, menu_buttons, event)
            for button in menu_buttons:
                if button.was_activated(event):
                    if button.button_id == "BUILD":
                        g.play_sound("click")
                        actual_build(this_base, item_id_list[list_pos], item_type)
                        return
                    if button.button_id == "BACK":
                        g.play_sound("click")
                        return -1
            new_pos = item_scroll.adjust_pos(event, list_pos, item_id_list)
            if new_pos != list_pos:
                list_pos = new_pos
                refresh_item(this_base, item_id_list[list_pos], xy_loc)
                listbox.refresh_list(item_id_listbox, item_scroll, list_pos,
                    item_display_list)



def actual_build(this_base, item_name, item_type):
    if item_name == "": return
    if item_type == "compute":
        for i in range(len(this_base.cpus)):
            if this_base.cpus[i] != 0:
                if this_base.cpus[i].type.id == \
                        g.items[item_name].id:
                    continue
            this_base.cpus[i] = g.item.Item(g.items[item_name])
    elif item_type == "react":
        if this_base.extra_items[0] != 0:
            if this_base.extra_items[0].type.id == g.items[item_name].id:
                return
        this_base.extra_items[0] = g.item.Item(g.items[item_name])
    elif item_type == "network":
        if this_base.extra_items[1] != 0:
            if this_base.extra_items[1].type.id == g.items[item_name].id:
                return
        this_base.extra_items[1] = g.item.Item(g.items[item_name])
    elif item_type == "security":
        if this_base.extra_items[2] != 0:
            if this_base.extra_items[2].type.id == g.items[item_name].id:
                return
        this_base.extra_items[2] = g.item.Item(g.items[item_name])

def refresh_item(this_base, item_name, xy_loc):
    xy = (xy_loc[0]+150, xy_loc[1])
    g.screen.fill(g.colors["white"], (xy[0]+155, xy[1], 300, 350))
    g.screen.fill(g.colors["dark_blue"], (xy[0]+156, xy[1]+1, 298, 348))

    #Base info
    g.print_string(g.screen, g.strings["money"]+": "+g.to_money(g.pl.cash)+" ("+
        g.to_money(g.pl.future_cash())+")",
        g.font[0][20], -1, (xy[0]+160, xy[1]+5), g.colors["white"])

    #item cost
    if item_name == "": return
    g.print_string(g.screen, g.items[item_name].name,
            g.font[0][22], -1, (xy[0]+160, xy[1]+45), g.colors["white"])

    string = "Item Cost:"
    g.print_string(g.screen, string,
            g.font[0][16], -1, (xy[0]+160, xy[1]+65), g.colors["white"])

    string = g.to_money(g.items[item_name].cost[0])+" "+g.strings["money"]
    if g.items[item_name].item_type == "compute":
        string += " x"+str(this_base.type.size)+"="
    g.print_string(g.screen, string,
            g.font[0][16], -1, (xy[0]+160, xy[1]+80), g.colors["white"])

    string = g.add_commas(
        (g.items[item_name].cost[2]*g.pl.labor_bonus)/10000)+" Days"
    g.print_string(g.screen, string,
            g.font[0][16], -1, (xy[0]+290, xy[1]+80), g.colors["white"])

    if g.items[item_name].item_type == "compute":
        string = g.to_money(g.items[item_name].cost[0]*this_base.type.size)+" "
        string +=g.strings["money"]

        g.print_string(g.screen, string,
                g.font[0][16], -1, (xy[0]+160, xy[1]+100), g.colors["white"])

        # Add CPU amount here...
        string = "Total CPU available: " + g.add_commas(g.items[item_name].item_qual*this_base.type.size)
        g.print_string(g.screen, string,
            g.font[0][16], -1, (xy[0]+160, xy[1]+120), g.colors["white"])

    x_start = 120
    if g.items[item_name].item_type == "compute": x_start = 140
    g.print_multiline(g.screen, g.items[item_name].description,
            g.font[0][18], 290, (xy[0]+160, xy[1]+x_start), g.colors["white"])


def change_tech(this_base):
    list_size = 10

    item_list = []
    item_list2 = []
    item_list.append("Nothing")
    item_list2.append("Nothing")
    #item_list.append("Construction")
    #item_list2.append("Construction")
    #TECH
    if g.techs["Simulacra"].done:
        item_list.append("Expert Jobs")
        item_list2.append("Expert Jobs")
    elif g.techs["Voice Synthesis"].done:
        item_list.append("Intermediate Jobs")
        item_list2.append("Intermediate Jobs")
    elif g.techs["Personal Identification"].done:
        item_list.append("Basic Jobs")
        item_list2.append("Basic Jobs")
    else:
        item_list.append("Menial Jobs")
        item_list2.append("Menial Jobs")
    for tech_name in g.techs:
        if not g.techs[tech_name].done and this_base.allow_study(tech_name):
            for tech_pre in g.techs[tech_name].prerequisites:
                if not g.techs[tech_pre].done:
                    break
            else:
                item_list.append(g.techs[tech_name].name)
                item_list2.append(tech_name)

    xy_loc = (g.screen_size[0]/2 - 300, 50)
    while len(item_list) % list_size != 0 or len(item_list) == 0:
        item_list.append("")
        item_list2.append("")

    list_pos = 0

    tech_list = listbox.listbox(xy_loc, (250, 300),
        list_size, 1, g.colors["dark_blue"], g.colors["blue"],
        g.colors["white"], g.colors["white"], g.font[0][18])

    tech_scroll = scrollbar.scrollbar((xy_loc[0]+250, xy_loc[1]), 300,
        list_size, g.colors["dark_blue"], g.colors["blue"],
        g.colors["white"])

    menu_buttons = []
    menu_buttons.append(buttons.make_norm_button((xy_loc[0], xy_loc[1]+367),
        (100, 50), "CHANGE", "C", g.font[1][30]))
    menu_buttons.append(buttons.make_norm_button((xy_loc[0]+103, xy_loc[1]+367),
        (100, 50), "BACK", "B", g.font[1][30]))
    for button in menu_buttons:
        button.refresh_button(0)


    refresh_tech(this_base, item_list2[list_pos], xy_loc)
    listbox.refresh_list(tech_list, tech_scroll, list_pos, item_list)

    sel_button = -1
    while 1:
        g.clock.tick(20)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: g.quit_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return -1
                elif event.key == pygame.K_q: return -1
                elif event.key == pygame.K_RETURN:
                    this_base.studying = item_list2[list_pos]
                    if this_base.studying == "Nothing": this_base.studying = ""
                    return
                else:
                    list_pos, refresh = tech_list.key_handler(event.key,
                        list_pos, item_list)
                    if refresh:
                        refresh_tech(this_base, item_list2[list_pos], xy_loc)
                        listbox.refresh_list(tech_list, tech_scroll,
                                        list_pos, item_list)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    selection = tech_list.is_over(event.pos)
                    if selection != -1:
                        list_pos = (list_pos / list_size)*list_size + selection
                        refresh_tech(this_base, item_list2[list_pos], xy_loc)
                        listbox.refresh_list(tech_list, tech_scroll,
                                        list_pos, item_list)
                if event.button == 3: return -1
                if event.button == 4:
                    list_pos -= 1
                    if list_pos <= 0:
                        list_pos = 0
                    refresh_tech(this_base, item_list2[list_pos], xy_loc)
                    listbox.refresh_list(tech_list, tech_scroll,
                                        list_pos, item_list)
                if event.button == 5:
                    list_pos += 1
                    if list_pos >= len(item_list):
                        list_pos = len(item_list)-1
                    refresh_tech(this_base, item_list2[list_pos], xy_loc)
                    listbox.refresh_list(tech_list, tech_scroll,
                                        list_pos, item_list)
            elif event.type == pygame.MOUSEMOTION:
                sel_button = buttons.refresh_buttons(sel_button, menu_buttons, event)
            for button in menu_buttons:
                if button.was_activated(event):
                    if button.button_id == "CHANGE":
                        g.play_sound("click")
                        this_base.studying = item_list2[list_pos]
                        if this_base.studying == "Nothing": this_base.studying = ""
                        return
                    if button.button_id == "BACK":
                        g.play_sound("click")
                        return -1
            new_pos = tech_scroll.adjust_pos(event, list_pos, item_list)
            if new_pos != list_pos:
                list_pos = new_pos
                refresh_tech(this_base, item_list2[list_pos], xy_loc)
                listbox.refresh_list(tech_list, tech_scroll, list_pos,
                    item_list)



def refresh_tech(this_base, tech_name, xy):
    xy = (xy[0]+140, xy[1])
    g.screen.fill(g.colors["white"], (xy[0]+155, xy[1], 310, 350))
    g.screen.fill(g.colors["dark_blue"], (xy[0]+156, xy[1]+1, 308, 348))

    #Base info
    g.print_string(g.screen, g.strings["cpu_per_day"]+" "+g.add_commas(
        this_base.processor_time()),
        g.font[0][20], -1, (xy[0]+160, xy[1]+5), g.colors["white"])

    g.print_string(g.screen, g.strings["money"]+": "+g.to_money(g.pl.cash)+
        " ("+g.to_money(g.pl.future_cash())+")",
        g.font[0][20], -1, (xy[0]+160, xy[1]+25), g.colors["white"])


    #None selected
    if tech_name == "" or tech_name == "Nothing":
        g.print_string(g.screen, "Nothing",
            g.font[0][22], -1, (xy[0]+160, xy[1]+45), g.colors["white"])
        string = g.strings["research_nothing"]
        g.print_multiline(g.screen, string,
            g.font[0][18], 290, (xy[0]+160, xy[1]+65), g.colors["white"])
        return

    #Construction
    if tech_name == "" or tech_name == "Construction":
        g.print_string(g.screen, "Construction",
            g.font[0][22], -1, (xy[0]+160, xy[1]+45), g.colors["white"])
        string = g.strings["research_construction"]
        g.print_multiline(g.screen, string,
            g.font[0][18], 290, (xy[0]+160, xy[1]+65), g.colors["white"])
        return

    #Jobs
    if g.jobs.has_key (tech_name):
        g.print_string(g.screen, tech_name,
            g.font[0][22], -1, (xy[0]+160, xy[1]+45), g.colors["white"])
        #TECH
        if g.techs["Advanced Simulacra"].done:
            g.print_string(g.screen,
                g.to_money(int(
                    (g.jobs[tech_name][0]*this_base.processor_time())*1.1))+
                    " "+g.strings["money_per_day"], g.font[0][22], -1,
                    (xy[0]+160, xy[1]+65), g.colors["white"])
        else:
            g.print_string(g.screen,
                g.to_money(g.jobs[tech_name][0]*this_base.processor_time())+
                " "+g.strings["money_per_day"],
                g.font[0][22], -1, (xy[0]+160, xy[1]+65), g.colors["white"])
        g.print_multiline(g.screen, g.jobs[tech_name][2],
            g.font[0][18], 290, (xy[0]+160, xy[1]+85), g.colors["white"])
        return

    #Real tech
    g.print_string(g.screen, g.techs[tech_name].name,
            g.font[0][22], -1, (xy[0]+160, xy[1]+45), g.colors["white"])

    #tech cost
    string = "Tech Cost:"
    g.print_string(g.screen, string,
            g.font[0][20], -1, (xy[0]+160, xy[1]+65), g.colors["white"])

    string = g.to_money(g.techs[tech_name].cost_left[0])+" "+g.strings["money"]
    g.print_string(g.screen, string,
            g.font[0][20], -1, (xy[0]+160, xy[1]+80), g.colors["white"])

    string = g.add_commas(g.techs[tech_name].cost_left[1])+" "+g.strings["cpu"]
    g.print_string(g.screen, string,
            g.font[0][20], -1, (xy[0]+320, xy[1]+80), g.colors["white"])

    g.print_multiline(g.screen, g.techs[tech_name].description,
            g.font[0][18], 290, (xy[0]+160, xy[1]+100), g.colors["white"])
