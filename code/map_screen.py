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
                    g.play_sound("click")
                    return buttonnum

def display_pause_menu():
    button_array= []
    button_array.append(["NEW GAME", "N"])
    button_array.append(["SAVE GAME", "S"])
    button_array.append(["LOAD GAME", "L"])
    button_array.append(["OPTIONS", "O"])
    button_array.append(["QUIT", "Q"])
    button_array.append(["RESUME", "R"])
    selection=display_generic_menu((g.screen_size[0]/2 - 100, 50), button_array)

    if selection == -1: return 0
    elif selection == 0: return 2 #New
    elif selection == 1: return 1 #Save
    elif selection == 2: return 3 #Load
    elif selection == 3: return 5 #Options
    elif selection == 4: return 4 #Quit
    elif selection == 5: return 0

def display_cheat_list(menu_buttons):
    if g.cheater == 0: return
    button_array= []
    button_array.append(["GIVE MONEY", "M"])
    button_array.append(["GIVE TECH", "T"])
    button_array.append(["END CONSTR.", "E"])
    button_array.append(["SUPERSPEED", "S"])
    button_array.append(["KILL SUSP.", "K"])
    button_array.append(["RESUME", "R"])
    selection=display_generic_menu((g.screen_size[0]/2 - 100, 50), button_array)

    if selection == -1: return
    elif selection == 0:  #Cash
        cash_amount = g.create_textbox("How much cash?", "", g.font[0][18],
        (g.screen_size[0]/2-100, 100), (200, 100), 25, g.colors["dark_blue"],
        g.colors["white"], g.colors["white"], g.colors["light_blue"])
        if cash_amount.isdigit() == False: return
        g.pl.cash += int(cash_amount)
        return
    elif selection == 1:  #Tech
        #create a fake base, in order to reuse the tech-changing code
        fake_base = g.base.base(1, "fake_base", g.base_type["Reality Bubble"], 1)
        base_screen.change_tech(fake_base)
        if g.techs.has_key(fake_base.studying):
            g.techs[fake_base.studying].finish()
        return
    elif selection == 2:  #Build all
        for base_loc in g.bases:
            for base_name in g.bases[base_loc]:
                if not base_name.done:
                    base_name.finish()
        return
    elif selection == 3:  #Superspeed
        g.curr_speed = 864000
        return
    elif selection == 4:  #Kill susp.
        for group in g.pl.groups.values():
            group.suspicion = 0
        return
    elif selection == 5: return

def display_knowledge_list():
    button_array= []
    button_array.append(["TECHS", "T"])
    button_array.append(["ITEMS", "I"])
    button_array.append(["CONCEPTS", "C"])
    button_array.append(["RESUME", "R"])
    selection=display_generic_menu((g.screen_size[0]/2 - 100, 120), button_array)

    if selection == -1: return
    elif selection == 0: display_items("tech") #Techs
    elif selection == 1:  #Items
        display_itemtype_list()
    elif selection == 2:
        display_items("concept")
    elif selection == 3: return

def display_itemtype_list():
    button_array= []
    button_array.append(["PROCESSOR", "P"])
    button_array.append(["REACTOR", "R"])
    button_array.append(["NETWORK", "N"])
    button_array.append(["SECURITY", "S"])
    button_array.append(["RESUME", "E"])
    selection=display_generic_menu((g.screen_size[0]/2 - 100, 70), button_array)

    if selection == -1: return
    elif selection == 0: display_items("compute")
    elif selection == 1: display_items("react")
    elif selection == 2: display_items("network")
    elif selection == 3: display_items("security")
    elif selection == 4: return

def display_items(item_type):
    list_size = 16
    list = []
    display_list = []

    if item_type == "tech":
        items = [tech for tech in g.techs.values() if tech.available()]
    elif item_type == "concept":
        items = [ [item[1][0], item[0]] for item in g.help_strings.items()]
        items.sort()
    else:
        items = [item for item in g.items.values() 
                      if item.item_type == item_type and item.available()]

    if item_type != "concept":
        items = [ [item.name, item.id ] for item in items]
        items.sort()

    for name, id in items:
        list.append(id)
        display_list.append(name)

    xy_loc = (g.screen_size[0]/2 - 289, 50)
    listbox.resize_list(list, list_size)

    menu_buttons = {}
    menu_buttons[buttons.make_norm_button((xy_loc[0]+103, xy_loc[1]+367), (100, 50), "BACK", "B", g.font[1][30])] = listbox.exit

    def do_refresh(item_pos):
        if item_type == "tech":
            refresh_tech(list[item_pos], xy_loc)
        elif item_type == "concept":
            refresh_concept(list[item_pos], xy_loc)
        else:
            refresh_items(list[item_pos], xy_loc)

    listbox.show_listbox(display_list, menu_buttons, do_refresh, listbox.exit, xy_loc, (230, 350), list_size)
    #details screen

def refresh_tech(tech_name, xy):
    xy = (xy[0]+100, xy[1])
    g.screen.fill(g.colors["white"], (xy[0]+155, xy[1], 300, 350))
    g.screen.fill(g.colors["dark_blue"], (xy[0]+156, xy[1]+1, 298, 348))
    if tech_name == "": return
    g.print_string(g.screen, g.techs[tech_name].name,
            g.font[0][22], -1, (xy[0]+160, xy[1]+5), g.colors["white"])

    #Building cost
    if not g.techs[tech_name].done:
        string = "Research Cost:"
        g.print_string(g.screen, string,
                g.font[0][18], -1, (xy[0]+160, xy[1]+30), g.colors["white"])

        string = g.to_money(g.techs[tech_name].cost_left[0])+" Money"
        g.print_string(g.screen, string,
                g.font[0][16], -1, (xy[0]+160, xy[1]+50), g.colors["white"])

        string = g.add_commas(g.techs[tech_name].cost_left[1]) + " CPU"
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

    if g.techs[tech_name].done:
        g.print_multiline(g.screen, g.techs[tech_name].description+" \\n \\n "+
                g.techs[tech_name].result,
                g.font[0][18], 290, (xy[0]+160, xy[1]+120), g.colors["white"])
    else:
        g.print_multiline(g.screen, g.techs[tech_name].description,
                g.font[0][18], 290, (xy[0]+160, xy[1]+120), g.colors["white"])

def refresh_items(item_name, xy):
    xy = (xy[0]+100, xy[1])
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

    string = g.add_commas(g.items[item_name].cost[2]) + " Days"
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

    g.print_multiline(g.screen, g.items[item_name].description,
            g.font[0][18], 290, (xy[0]+160, xy[1]+120), g.colors["white"])

def refresh_concept(concept_name, xy):
    xy = (xy[0]+100, xy[1])
    g.screen.fill(g.colors["white"], (xy[0]+155, xy[1], 300, 350))
    g.screen.fill(g.colors["dark_blue"], (xy[0]+156, xy[1]+1, 298, 348))
    if concept_name == "": return
    g.print_string(g.screen, g.help_strings[concept_name][0],
            g.font[0][22], -1, (xy[0]+160, xy[1]+5), g.colors["white"])
    g.print_multiline(g.screen, g.help_strings[concept_name][1],
            g.font[0][18], 290, (xy[0]+160, xy[1]+30), g.colors["white"])

def create_buttons(font_size):
    menu_buttons = []
    #Note that this must be element 0 in menu_buttons
    menu_buttons.append(buttons.button((100, -1), (200, 26),
        "DAY 0000, 00:00:00", "", g.colors["black"], g.colors["dark_blue"],
        g.colors["black"], g.colors["white"], g.font[1][font_size]))
    menu_buttons.append(buttons.make_norm_button((0, 0), (100, 25),
        "OPTIONS", "O", g.font[1][20]))
    menu_buttons.append(buttons.make_norm_button((300, 0), (25, 25),
        "ii", "0", g.font[1][20]))
    if g.curr_speed == 0: menu_buttons[2].stay_selected = 1
    menu_buttons[2].activate_key = "0"
    menu_buttons.append(buttons.make_norm_button((324, 0), (25, 25),
        ">", "1", g.font[1][20]))
    if g.curr_speed == 1: menu_buttons[3].stay_selected = 1
    menu_buttons[3].activate_key = "1"
    menu_buttons.append(buttons.make_norm_button((348, 0), (25, 25),
        ">>", "2", g.font[1][20]))
    if g.curr_speed == 60: menu_buttons[4].stay_selected = 1
    menu_buttons[4].activate_key = "2"
    menu_buttons.append(buttons.make_norm_button((372, 0), (28, 25),
        ">>>", "3", g.font[1][20]))
    if g.curr_speed == 7200: menu_buttons[5].stay_selected = 1
    menu_buttons[5].activate_key = "3"
    menu_buttons.append(buttons.make_norm_button((399, 0), (36, 25),
        ">>>>", "4", g.font[1][20]))
    if g.curr_speed == 432000: menu_buttons[6].stay_selected = 1
    #Note that this must be element 7 in menu_buttons
    adjusted_size = font_size
    if g.screen_size[0] == 640:
        adjusted_size = font_size -2
    menu_buttons.append(buttons.button((435, -1), (g.screen_size[0]-435, 26),
        "CASH", "", g.colors["black"], g.colors["dark_blue"],
        g.colors["black"], g.colors["white"], g.font[1][adjusted_size]))
    #Note that this must be element 8 in menu_buttons
    menu_buttons.append(buttons.button((0, g.screen_size[1]-25),
        (g.screen_size[0], 26),
        "SUSPICION", "", g.colors["black"], g.colors["dark_blue"],
        g.colors["black"], g.colors["white"], g.font[1][adjusted_size]))
    #Note that this must be element 9 in menu_buttons
    menu_buttons.append(buttons.button((435, 24), (g.screen_size[0]-435, 26),
        "CPU", "", g.colors["black"], g.colors["dark_blue"],
        g.colors["black"], g.colors["white"], g.font[1][adjusted_size]))
    menu_buttons.append(buttons.make_norm_button((0, g.screen_size[1]-50), (120, 25),
        "RESEARCH", "R", g.font[1][20]))
    menu_buttons.append(buttons.make_norm_button((g.screen_size[0]-120,
        g.screen_size[1]-50), (120, 25),
        "FINANCE", "E", g.font[1][20]))
    menu_buttons.append(buttons.make_norm_button((g.screen_size[0]-120,
        g.screen_size[1]-75), (120, 25),
        "KNOWLEDGE", "K", g.font[1][20]))

    for location in g.locations.values():
        menu_buttons.append(buttons.make_norm_button((
            g.screen_size[0] * location.y // 100,
            g.screen_size[1] * location.x // 100), -1,
            location.id, location.hotkey, g.font[1][25]))

    return menu_buttons

def map_loop():
    font_size = 20
    if g.screen_size[0] == 640: font_size = 16
    menu_buttons = create_buttons(font_size)

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
            lost = g.pl.lost_game()
            if lost == 1:
                g.play_music("lose")
                g.create_dialog(g.strings["lost_nobases"])
                return 0
            if lost == 2:
                g.play_music("lose")
                g.create_dialog(g.strings["lost_sus"])
                return 0
            milli_clock = milli_clock % 1000

            day_string = "%04d" % g.pl.time_day
            hour_string = "%02d" % g.pl.time_hour
            min_string = "%02d" % g.pl.time_min
            sec_string = "%02d" % g.pl.time_sec
            time_string = "DAY %04d, %02d:%02d:%02d" % \
                  (g.pl.time_day, g.pl.time_hour, g.pl.time_min, g.pl.time_sec)

            menu_buttons[0].text = time_string
            menu_buttons[0].remake_button()
            menu_buttons[0].refresh_button(0)

            result_cash = g.to_money(g.pl.future_cash())
            menu_buttons[7].text = "CASH: "+g.to_money(g.pl.cash)+" ("+result_cash+")"
            menu_buttons[7].remake_button()
            menu_buttons[7].refresh_button(0)

            menu_buttons[8].text = ("[SUSPICION] NEWS: "+
                g.to_percent(g.pl.groups["news"].suspicion, 1)+"  SCIENCE: "+
                g.to_percent(g.pl.groups["science"].suspicion, 1)+"  COVERT: "+
                g.to_percent(g.pl.groups["covert"].suspicion, 1)+"  PUBLIC: "+
                g.to_percent(g.pl.groups["public"].suspicion, 1))
            menu_buttons[8].remake_button()
            menu_buttons[8].refresh_button(0)

            total_cpu, idle_cpu, construction_cpu, unused, unused, maint_cpu = \
                    finance_screen.cpu_numbers()
            if construction_cpu < maint_cpu:
                menu_buttons[9].text_color = g.colors["red"]
            else:
                menu_buttons[9].text_color = g.colors["white"]
            menu_buttons[9].text = "CPU: "+g.to_money(total_cpu)+" ("+g.to_money(construction_cpu)+")"
            menu_buttons[9].remake_button()
            menu_buttons[9].refresh_button(0)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: g.quit_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    selection = display_pause_menu()
                    result = handle_pause_menu(selection, menu_buttons)
                    if result == 0: return result
                    if result == 1:
                        menu_buttons = create_buttons(font_size)
                        refresh_map(menu_buttons)
                elif event.key == pygame.K_BACKQUOTE:
                    display_cheat_list(menu_buttons)
                    refresh_map(menu_buttons)

            elif event.type == pygame.MOUSEMOTION:
                sel_button = buttons.refresh_buttons(sel_button, menu_buttons, event)
            for button in menu_buttons:
                if button.was_activated(event):
                    if button.button_id == "OPTIONS":
                        g.play_sound("click")
                        selection = display_pause_menu()
                        result = handle_pause_menu(selection, menu_buttons)
                        if result == 0: return result
                        if result == 1:
                            menu_buttons = create_buttons(font_size)
                            refresh_map(menu_buttons)
                    elif button.button_id == "RESEARCH":
                        g.play_sound("click")
                        research_screen.main_research_screen()
                        refresh_map(menu_buttons)
                    elif button.button_id == "FINANCE":
                        g.play_sound("click")
                        finance_screen.main_finance_screen()
                        refresh_map(menu_buttons)
                    elif button.button_id == "KNOWLEDGE":
                        g.play_sound("click")
                        display_knowledge_list()
                        refresh_map(menu_buttons)
                    elif button.button_id == "ii":
                        g.play_sound("click")
                        g.curr_speed = 0
                        for button2 in menu_buttons:
                            button2.stay_selected = 0
                            button2.refresh_button(0)
                        button.stay_selected = 1
                        button.refresh_button(1)
                    elif button.button_id == ">":
                        g.play_sound("click")
                        g.curr_speed = 1
                        for button2 in menu_buttons:
                            button2.stay_selected = 0
                            button2.refresh_button(0)
                        button.stay_selected = 1
                        button.refresh_button(1)
                    elif button.button_id == ">>":
                        g.play_sound("click")
                        g.curr_speed = 60
                        for button2 in menu_buttons:
                            button2.stay_selected = 0
                            button2.refresh_button(0)
                        button.stay_selected = 1
                        button.refresh_button(1)
                    elif button.button_id == ">>>":
                        g.play_sound("click")
                        g.curr_speed = 7200
                        for button2 in menu_buttons:
                            button2.stay_selected = 0
                            button2.refresh_button(0)
                        button.stay_selected = 1
                        button.refresh_button(1)
                    elif button.button_id == ">>>>":
                        g.play_sound("click")
                        g.curr_speed = 432000
                        for button2 in menu_buttons:
                            button2.stay_selected = 0
                            button2.refresh_button(0)
                        button.stay_selected = 1
                        button.refresh_button(1)
                    elif button.button_id == "SUSPICION": pass
                    elif button.button_id == "CPU": pass
                    elif button.xy[1] != -1: #ignore the timer
                        g.play_sound("click")

                        # We want to keep redisplaying the base_list until the
                        # user is done mucking around with bases.
                        done_base = False
                        while not done_base:
                           done_base = display_base_list(g.locations[
                                                             button.button_id],
                                                         menu_buttons)
                    pygame.display.flip()


def handle_pause_menu(selection, menu_buttons):
    if selection == 0: refresh_map(menu_buttons)
    elif selection == 1: #Save
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
    elif selection == 2: return 0
    elif selection == 3: #Load
        load_return = main_menu.display_load_menu()
        if load_return == -1 or load_return == "":
            refresh_map(menu_buttons)
        else:
            g.load_game(load_return)
            map_loop()
#			refresh_map(menu_buttons)
            return 0
    elif selection == 4: g.quit_game()
    elif selection == 5:
        main_menu.display_options()
        return 1
    return -1

def refresh_map(menu_buttons):
    g.screen.fill(g.colors["black"])
    g.screen.blit(pygame.transform.scale(g.images["earth.jpg"],
                (g.screen_size[0], g.screen_size[0]/2)),
                (0, g.screen_size[1]/2-g.screen_size[0]/4))
    for button in menu_buttons:
        button.stay_selected = 0
        if g.locations.has_key(button.button_id):
            #determine if building in a location is possible. If so, show the
            #button.
            if g.locations[button.button_id].available():
                button.visible = 1
            else: button.visible = 0

            button.text = g.locations[button.button_id].name + " ("
            button.text += str(len(g.bases[g.locations[button.button_id]]))+")"
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
        done = False
        while (not done) and (attempts < 5):
            name = random.choice(location.cities) + \
                " " + random.choice(base_type.flavor) + " " \
                + random.choice(significant_numbers)
            duplicate = False
            for check_base in g.bases[location]:
                if check_base.name == name:
                    duplicate = True
                    break
            if duplicate:
                attempts += 1
            else:
                done = True
        if done:
            return name
    # This is both the else case and the general case.
    name = random.choice(location.cities) + " " + \
        random.choice(base_type.flavor) + " " + \
        str (random.randint(0, 32767))

    return name

def display_base_list(location, menu_buttons):
    """
    display_base_list() displays the list of bases at a given location.  This
    is where players can add new bases, destroy old ones, and inspect the ones
    they have.

    It should return a Boolean representing whether or not the user is done
    with mucking around with bases at this location.
"""

    if not location.available(): return True

    selection = display_base_list_inner(location)
    refresh_map(menu_buttons)
    #Build a new base
    if selection == -2:
        selection = build_new_base_window(location)
        if selection != "" and selection != -1:
            base_to_add = g.base_type[selection]
            possible_name = g.create_textbox(g.strings["new_base_text"],
                generate_base_name(location, g.base_type[selection]),
                g.font[0][18],
                (g.screen_size[0]/2-150, 100), (300, 100), 25,
                g.colors["dark_blue"], g.colors["white"], g.colors["white"],
                g.colors["light_blue"])
            if possible_name == "":
                refresh_map(menu_buttons)
                return False
            base_to_add.count += 1

            g.bases[location].append(g.base.Base(len(g.bases[location]),
                selection, g.base_type[selection], 0))
            g.bases[location][-1].name = possible_name

            # Now that the base is built, redraw the base list.
            refresh_map(menu_buttons)
            return False
        refresh_map(menu_buttons)
        return False

    #Showing base under construction
    elif selection != -1 and selection != "":
        if not g.bases[location][selection].done:
            string = "Under Construction. \\n Completion in "
            string += g.to_time(g.bases[location][selection].cost_left[2]) + ". \\n "
            string += "Remaining cost: "+g.to_money(g.bases[location][selection].cost_left[0])
            string +=" money, and "+g.add_commas(
                                            g.bases[location][selection].cost_left[1])
            string +=" processor time."
            if not g.create_yesno(string, g.font[0][18], (g.screen_size[0]/2 - 100, 50),
                    (200, 200), g.colors["dark_blue"], g.colors["white"],
                    g.colors["white"], ("OK", "DESTROY"), reverse_key_context = True):
                if g.create_yesno("Destroy this base? This will waste "+
                        g.to_money(g.bases[location][selection].cost_paid[0])
                        +" money, and "+
                        g.add_commas(g.bases[location][selection].cost_paid[1])
                        +" processor time.", g.font[0][18],
                        (g.screen_size[0]/2 - 100, 50),
                        (200, 200), g.colors["dark_blue"], g.colors["white"],
                        g.colors["white"]):
                    g.base.destroy_base(location, selection)
        else:
            next_prev = 1
            while next_prev != 0:
                next_prev = base_screen.show_base(g.bases[location][selection], location)
                if next_prev == -2:
                    g.base.destroy_base(location, selection)
                    break
                selection += next_prev
                if selection < 0: selection = len(g.bases[location]) -1
                if selection >= len(g.bases[location]): selection = 0
                while not g.bases[location][selection].done:
                    selection += next_prev
                    if selection < 0: selection = len(g.bases[location]) -1
                    if selection >= len(g.bases[location]): selection = 0

        # After looking at a base, redraw the base list.
        refresh_map(menu_buttons)
        return False

    # The player hit 'Back' at this point; we're done with the base list.
    refresh_map(menu_buttons)
    return True


#Display the list of bases.
def display_base_list_inner(location):
    list_size = 15

    base_display_list = []
    base_id_list = []
    for this_base in g.bases[location]:
        studying = this_base.studying
        if not this_base.done:
            studying = g.strings["building"]
        elif studying == "":
            studying = g.strings["nothing"]
        elif studying == "Construction":
            studying = g.strings["construct_task"]
        elif g.techs.has_key(studying):
            studying = g.techs[studying].name
        base_display_list.append(this_base.name+" ("+studying+")")
        base_id_list.append(this_base.id)

    def do_open(base_pos):
        if base_pos < len(g.bases[location]):
            return base_id_list[base_pos]

    def do_destroy(base_pos):
        if base_pos >= len(g.bases[location]):
            return

        prompt_string = "Destroy this base?"
        base = g.bases[location][base_pos]
        if not base.done:
            prompt_string += " This will waste %s money and %s processor time."\
                % ( g.to_money(base.cost_paid[0]), 
                    g.add_commas(base.cost_paid[1]) )
        if g.create_yesno(prompt_string, g.font[0][18],
                    (g.screen_size[0]/2 - 100, 50),
                    (200, 200), g.colors["dark_blue"], g.colors["white"],
                    g.colors["white"]):
            g.base.destroy_base(location, base_pos)

            # Remove the base from the display.
            del base_display_list[base_pos]
            # And its matching ID.
            del base_id_list[base_pos]
            # And pad the display list back up to the correct length.
            base_display_list.append("")

    xy_loc = (g.screen_size[0]/2 - 259, 50)

    menu_buttons = {}
    menu_buttons[buttons.make_norm_button((xy_loc[0], xy_loc[1]+367), (100, 50),
        "OPEN", "O", g.font[1][30])] = do_open
    menu_buttons[buttons.make_norm_button((xy_loc[0]+105, xy_loc[1]+367), (100, 50),
        "BACK", "B", g.font[1][30])] = listbox.exit
    menu_buttons[buttons.make_norm_button((xy_loc[0]+210, xy_loc[1]+367), (100, 50),
        "NEW", "N", g.font[1][30])] = lambda *args, **kwargs: -2
    menu_buttons[buttons.make_norm_button((xy_loc[0]+315, xy_loc[1]+367), (120, 50),
        "DESTROY", "D", g.font[1][30])] = do_destroy

    return listbox.show_listbox(base_display_list, menu_buttons, listbox.void, do_open, xy_loc, (500, 350), list_size)

def build_new_base_window(location):
    base_list = []
    base_display_list = []
    for base_name in g.base_type:
        for region in g.base_type[base_name].regions:
            if region == location.id:
                if g.base_type[base_name].available():
                    base_list.append(base_name)
                    base_display_list.append(g.base_type[base_name].base_name)

    list_size = 16
    listbox.resize_list(base_list, list_size)


    xy_loc = (g.screen_size[0]/2 - 289, 50)

    def do_build(base_pos):
        return base_list[base_pos]

    menu_buttons = {}
    menu_buttons[buttons.make_norm_button((xy_loc[0], xy_loc[1]+367), (100, 50),
        "BUILD", "U", g.font[1][30])] = do_build
    menu_buttons[buttons.make_norm_button((xy_loc[0]+103, xy_loc[1]+367), (100, 50),
        "BACK", "B", g.font[1][30])] = listbox.exit

    def do_refresh(base_pos):
        refresh_new_base(base_list[base_pos], xy_loc)

    return listbox.show_listbox(base_display_list, menu_buttons, do_refresh, do_build, xy_loc, (230, 350), list_size)

def refresh_new_base(base_name, xy):
    xy = (xy[0]+100, xy[1])
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

    string = g.add_commas(g.base_type[base_name].cost[1]) + " CPU"
    g.print_string(g.screen, string,
            g.font[0][16], -1, (xy[0]+160, xy[1]+70), g.colors["white"])

    string = g.add_commas(g.base_type[base_name].cost[2]) + " Days"
    g.print_string(g.screen, string,
            g.font[0][16], -1, (xy[0]+160, xy[1]+90), g.colors["white"])

    #Maintenance cost
    string = "Maintenance Cost:"
    g.print_string(g.screen, string,
            g.font[0][18], -1, (xy[0]+290, xy[1]+30), g.colors["white"])

    string = g.to_money(g.base_type[base_name].maintenance[0]) + " Money"
    g.print_string(g.screen, string,
            g.font[0][16], -1, (xy[0]+290, xy[1]+50), g.colors["white"])

    string = g.add_commas(g.base_type[base_name].maintenance[1]) + " CPU"
    g.print_string(g.screen, string,
            g.font[0][16], -1, (xy[0]+290, xy[1]+70), g.colors["white"])

    #Size
    string = "Size: "+str(g.base_type[base_name].size)
    g.print_string(g.screen, string,
            g.font[0][20], -1, (xy[0]+160, xy[1]+110), g.colors["white"])

    #Detection
    real_detection_chance = base.calc_base_discovery_chance(base_name)
    string = "Detection chance:"
    g.print_string(g.screen, string,
            g.font[0][22], -1, (xy[0]+160, xy[1]+130), g.colors["white"])

    string = "News: " + g.to_percent(real_detection_chance.get("news", 0))
    g.print_string(g.screen, string,
            g.font[0][16], -1, (xy[0]+160, xy[1]+150), g.colors["white"])
    string = "Science: " + g.to_percent(real_detection_chance.get("science", 0))
    g.print_string(g.screen, string,
            g.font[0][16], -1, (xy[0]+290, xy[1]+150), g.colors["white"])
    string = "Covert: " + g.to_percent(real_detection_chance.get("covert", 0))
    g.print_string(g.screen, string,
            g.font[0][16], -1, (xy[0]+160, xy[1]+170), g.colors["white"])
    string = "Public: " + g.to_percent(real_detection_chance.get("public", 0))
    g.print_string(g.screen, string,
            g.font[0][16], -1, (xy[0]+290, xy[1]+170), g.colors["white"])

    g.print_multiline(g.screen, g.base_type[base_name].description,
            g.font[0][18], 290, (xy[0]+160, xy[1]+190), g.colors["white"])
