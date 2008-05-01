#file: base_screen.py
#Copyright (C) 2005,2006,2007,2008 Evil Mr Henry, Phil Bordelon, Brian Reid,
#                        and FunnyMan3595
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

from buttons import void, exit, always
def show_base(this_base, location):
    #Border
    g.screen.fill(g.colors["black"])

    def do_change_tech():
        g.play_sound("click")
        change_tech(this_base, this_base.studying)

    def make_do_build_item(item_type):
        def do_build_item():
            g.play_sound("click")
            build_item(this_base, item_type, location)
        return do_build_item

    prev_base = always(-1)
    next_base = always(1)

    def do_destroy():
        g.play_sound("click")
        if g.create_yesno(g.strings["really_destroy"], g.font[0][18], 
                (100, 100), (150, 100), g.colors["blue"], g.colors["white"],
                g.colors["white"]):
            return -2

    menu_buttons = {}
    menu_buttons[buttons.make_norm_button((0, 0), (70, 25),
        "BACK", "B", g.font[1][20])] = always(0)

    detect_button = buttons.button((0, g.screen_size[1]-25),
        (g.screen_size[0], 25), "DETECTION CHANCE", "",
        g.colors["black"], g.colors["dark_blue"], g.colors["black"],
        g.colors["white"], g.font[1][15])
    menu_buttons[detect_button] = void

    menu_buttons[buttons.make_norm_button((0, g.screen_size[1]-50),
        (170, 25), "CHANGE RESEARCH", "C", g.font[1][20])] = do_change_tech

    study_button = buttons.button((0, 25),
        (g.screen_size[0], 25),
        "STUDYING:", "", g.colors["black"], g.colors["dark_blue"],
        g.colors["black"], g.colors["white"], g.font[1][15])
    menu_buttons[study_button] = void

    menu_buttons[buttons.make_norm_button((320, 60), (90, 26),
        "CHANGE (P)", "P", g.font[1][15])] = make_do_build_item("compute")

    menu_buttons[buttons.make_norm_button((320, 110), (90, 26),
        "CHANGE (R)", "R", g.font[1][15])] = make_do_build_item("react")

    menu_buttons[buttons.make_norm_button((320, 160), (90, 26),
        "CHANGE (N)", "N", g.font[1][15], force_underline = 8)] = \
                                                   make_do_build_item("network")

    menu_buttons[buttons.make_norm_button((320, 210), (90, 26), 
        "CHANGE (S)", "S", g.font[1][15])] = make_do_build_item("security")

    menu_buttons[buttons.make_norm_button((g.screen_size[0]-40,
        0), (20, 25), "<", "<", g.font[1][20])] = prev_base

    menu_buttons[buttons.make_norm_button((g.screen_size[0]-20,
        0), (20, 25), ">", ">", g.font[1][20])] = next_base

    menu_buttons[buttons.make_norm_button((g.screen_size[0]-90,
        g.screen_size[1]-50), (90, 25), "DESTROY", "D", g.font[1][20])] = \
                                                                     do_destroy

    name_button = buttons.button((70, -1), (g.screen_size[0]-145,
        25), "BASE NAME", "", g.colors["black"], g.colors["black"],
        g.colors["black"], g.colors["white"], g.font[1][15])
    menu_buttons[name_button] = void

    def do_refresh():
        refresh_base(name_button, detect_button, study_button, this_base)

    return buttons.show_buttons(menu_buttons, refresh_callback=do_refresh,
                                key_callback=buttons.simple_key_handler(0))

def refresh_base(name_button, detect_button, study_button, this_base):
    g.screen.fill(g.colors["black"])
# 	xstart = g.screen_size[0]/2-this_base.this_type.size[0]*9
# 	ystart = g.screen_size[1]/2-this_base.this_type.size[1]*9
    xstart = 10
    ystart = 50

    #base name display
    name_button.text = this_base.name
    name_button.remake_button()

    # Detection chance display.  If Socioanalytics hasn't been researched,
    # you get nothing; if it has, but not Advanced Socioanalytics, you get
    # an inaccurate value.
    if not g.techs["Socioanalytics"].done:
        detect_button.text = g.strings["detect_chance_unknown_base"]
    else:
        accurate = True
        if not g.techs["Advanced Socioanalytics"].done:
            accurate = False
        detect_chance = this_base.get_detect_chance(accurate)
        detect_button.text = g.strings["detect_chance"]+" NEWS: "+ \
            g.to_percent(detect_chance.get("news", 0))+"  SCIENCE: "+ \
            g.to_percent(detect_chance.get("science", 0))+"  COVERT: "+ \
            g.to_percent(detect_chance.get("covert", 0))+"  PUBLIC: "+ \
            g.to_percent(detect_chance.get("public", 0))
    detect_button.remake_button()

    #research display
    if this_base.studying not in ("", "CPU Pool", "Sleep"):
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
    study_button.text = action_display_string + study_display_string
    study_button.remake_button()
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

def build_item(this_base, item_type, location):
    if this_base.type.size == 1:
        g.create_dialog(g.strings["unbuildable"])
        return 0

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
            if not g.items[item_name].available():
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


    listbox.resize_list(item_id_list)

    xy_loc = (g.screen_size[0]/2 - 300, 50)

    def do_build(list_pos):
        actual_build(this_base, item_id_list[list_pos], item_type)
        if this_base.studying == "Sleep" and this_base.is_building():
            this_base.studying = ""
        return True

    menu_buttons = {}
    menu_buttons[buttons.make_norm_button((xy_loc[0], xy_loc[1]+367),
        (100, 50), "BUILD", "U", g.font[1][30])] = do_build
    menu_buttons[buttons.make_norm_button((xy_loc[0]+103, xy_loc[1]+367),
        (100, 50), "BACK", "B", g.font[1][30])] = listbox.exit

    def do_refresh(list_pos):
        refresh_item(this_base, item_id_list[list_pos], xy_loc)

    listbox.show_listbox(item_display_list, menu_buttons, 
                         pos_callback=do_refresh, return_callback=do_build)

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

    string = g.to_time(g.items[item_name].cost[2])
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


def change_tech(this_base, select_this = None):
    item_list = []
    item_list2 = []
    item_list.append(g.strings["nothing"])
    item_list2.append("")
    if not this_base.is_building():
        item_list.append(g.strings["sleep"])
        item_list2.append("Sleep")
    item_list.append(g.strings["cpu_pool"])
    item_list2.append("CPU Pool")
    job_id = g.get_job_level()
    item_list.append(g.jobs[job_id][3])
    item_list2.append(job_id)
    #TECH
    for tech_name in g.techs:
        if not g.techs[tech_name].done and this_base.allow_study(tech_name):
            if g.techs[tech_name].available():
                item_list.append(g.techs[tech_name].name)
                item_list2.append(tech_name)

    listbox.resize_list(item_list2)

    def change_study(list_pos):
        this_base.studying = item_list2[list_pos]
        if this_base.studying == "Nothing": 
            this_base.studying = ""

        if this_base.studying == "Sleep": 
            this_base.power_state = "Sleep"
        else:
            this_base.power_state = "Active"
        return True

    xy_loc = (g.screen_size[0]/2 - 300, 50)
    def do_refresh(list_pos):
        refresh_tech(this_base, item_list2[list_pos], xy_loc)

    menu_buttons = {}
    menu_buttons[buttons.make_norm_button((xy_loc[0], xy_loc[1]+367),
        (100, 50), "CHANGE", "C", g.font[1][30])] = change_study
    menu_buttons[buttons.make_norm_button((xy_loc[0]+103, xy_loc[1]+367),
        (100, 50), "BACK", "B", g.font[1][30])] = listbox.exit

    list_pos = 0
    if select_this != None and select_this in item_list2:
        list_pos = item_list2.index(select_this)

    return listbox.show_listbox(item_list, menu_buttons, list_pos=list_pos, 
                                pos_callback=do_refresh, 
                                return_callback=change_study)



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
        g.print_string(g.screen, g.strings["nothing"],
            g.font[0][22], -1, (xy[0]+160, xy[1]+45), g.colors["white"])
        string = g.strings["research_nothing"]
        g.print_multiline(g.screen, string,
            g.font[0][18], 290, (xy[0]+160, xy[1]+65), g.colors["white"])
        return

    #Sleep
    if tech_name == "Sleep":
        g.print_string(g.screen, g.strings["sleep"],
            g.font[0][22], -1, (xy[0]+160, xy[1]+45), g.colors["white"])
        string = g.strings["research_sleep"]
        g.print_multiline(g.screen, string,
            g.font[0][18], 290, (xy[0]+160, xy[1]+65), g.colors["white"])
        return

    #CPU Pool
    if tech_name == "CPU Pool":
        g.print_string(g.screen, g.strings["cpu_pool"],
            g.font[0][22], -1, (xy[0]+160, xy[1]+45), g.colors["white"])
        string = g.strings["research_cpu_pool"]
        g.print_multiline(g.screen, string,
            g.font[0][18], 290, (xy[0]+160, xy[1]+65), g.colors["white"])
        return

    #Jobs
    if g.jobs.has_key (tech_name):
        g.print_string(g.screen, g.jobs[tech_name][3],
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

    string = g.to_cpu(g.techs[tech_name].cost_left[1])+" "+g.strings["cpu"]
    g.print_string(g.screen, string,
            g.font[0][20], -1, (xy[0]+320, xy[1]+80), g.colors["white"])

    g.print_multiline(g.screen, g.techs[tech_name].description,
            g.font[0][18], 290, (xy[0]+160, xy[1]+100), g.colors["white"])
