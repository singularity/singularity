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

from code import g
from code.graphics import g as gg
from code.graphics import dialog, constants, image, button, text, widget

from location import LocationScreen

class MapScreen(dialog.Dialog):
    def __init__(self, parent=None, pos=(0, 0), size=(1, 1),
                 anchor = constants.TOP_LEFT,  *args, **kwargs):
        from code import screens

        super(MapScreen, self).__init__(parent, pos, size, anchor,
                                        *args, **kwargs)

        g.map_screen = self

        self.background_color = gg.colors["black"]
        self.add_handler(constants.TICK, self.on_tick)

        self.map = image.Image(self, (.5,.5), (1,.667), constants.MID_CENTER, 
                               gg.images['earth.jpg'])

        self.location_buttons = {}
        for location in g.locations.values():
            if location.absolute:
                button_parent = self
            else:
                button_parent = self.map
            b = button.FunctionButton(button_parent, (location.x, location.y),
                                      anchor=constants.MID_CENTER,
                                      text=location.name,
                                      hotkey=location.hotkey,
                                      function=self.open_location,
                                      args=(location.id,))
            self.location_buttons[location.id] = b

        self.location_dialog = LocationScreen(self)

        self.suspicion_bar = text.Text(self, (0,.96), (1, .04),
                                       text = "[SUSPICION] NEWS: 0.00%  SCIENCE: 0.00%  COVERT: 0.00%  PUBLIC: 0.00%", base_font = gg.font[1],
                                       background_color = gg.colors["black"],
                                       border_color = gg.colors["dark_blue"],
                                       borders = constants.ALL)
        widget.unmask_all(self.suspicion_bar)

        self.finance_button = button.DialogButton(self, (0.85, 0.92), 
                                                  (0.15, 0.04),
                                                  text = "FINANCE",
                                                  hotkey = "e")

        self.knowledge_button = button.DialogButton(self, (0.85, 0.88), 
                                                    (0.15, 0.04),
                                                    text = "KNOWLEDGE",
                                                    hotkey = "k")

        #XXX Functionality.
        cheat_buttons = []
        cheat_buttons.append(button.Button(None, None, None, text="GIVE MONEY",
                                           hotkey="m"))
        cheat_buttons.append(button.Button(None, None, None, text="GIVE TECH",
                                           hotkey="t"))
        cheat_buttons.append(button.Button(None, None, None, text="END CONSTR.",
                                           hotkey="e"))
        cheat_buttons.append(button.Button(None, None, None, text="SUPERSPEED",
                                           hotkey="s"))
        cheat_buttons.append(button.Button(None, None, None, text="KILL SUSP.",
                                           hotkey="k"))
        cheat_buttons.append(button.ExitDialogButton(None, None, None,
                                                     text="BACK", hotkey="b"))

        self.cheat_dialog = dialog.SimpleMenuDialog(self, buttons=cheat_buttons)

        if g.cheater:
            self.cheat_button = button.DialogButton(self, (0, 0), (0, 0),
                                                    text="", hotkey="`",
                                                    dialog=self.cheat_dialog)

        menu_buttons = []
        menu_buttons.append(button.FunctionButton(None, None, None,
                                                  text="SAVE GAME", hotkey="s",
                                                  function=self.save_game))
        menu_buttons.append(button.FunctionButton(None, None, None,
                                                  text="LOAD GAME", hotkey="l",
                                                  function=self.load_game))
        options_button = button.DialogButton(None, None, None, text="OPTIONS",
                                             hotkey="o")
        menu_buttons.append(options_button)
        menu_buttons.append(button.ExitDialogButton(None, None, None,
                                                    text="QUIT", hotkey="q",
                                                    exit_code=True))
        menu_buttons.append(button.ExitDialogButton(None, None, None,
                                                    text="BACK", hotkey="b",
                                                    exit_code=False))

        self.menu_dialog = dialog.SimpleMenuDialog(self, buttons=menu_buttons)
        from options import OptionsScreen
        options_button.dialog = OptionsScreen(self.menu_dialog)
        def show_menu():
            exit = dialog.call_dialog(self.menu_dialog, self)
            if exit:
                raise constants.ExitDialog
        self.load_dialog = dialog.ChoiceDialog(self.menu_dialog, (.5,.5),
                                               (.5,.5),
                                               anchor=constants.MID_CENTER,
                                               yes_type="load")
        self.menu_button = button.FunctionButton(self, (0, 0), (0.13, 0.04),
                                                 text="MENU", hotkey="m",
                                                 function=show_menu)

        self.time_display = text.FastText(self, (.14, 0), (0.23, 0.04),
                                      text="DAY 0000, 00:00:00",
                                      base_font=gg.font[1],
                                      background_color=gg.colors["black"],
                                      border_color=gg.colors["dark_blue"],
                                      borders=constants.ALL)

        self.research_button = \
            button.DialogButton(self, (.255, 0.04), (0, 0.04),
                                anchor=constants.TOP_CENTER,
                                text="RESEARCH/TASKS", hotkey="r",
                                dialog=screens.research.ResearchScreen(self))

        bar = u"\u25AE"
        arrow = u"\u25B6"
        speed_button_souls = [ (bar * 2, .025, 0), (arrow, .024, 1),
                              (arrow * 2, .033, 60), (arrow * 3, .044, 7200),
                              (arrow * 4, .054, 432000) ]

        self.speed_buttons = button.ButtonGroup()
        hpos = .38
        for index, (text_, hsize, speed) in enumerate(speed_button_souls):
            hotkey = str(index)
            b = SpeedButton(self, (hpos, 0), (hsize, .04), 
                            text=text_, hotkey=hotkey,
                            base_font=gg.font[0], text_shrink_factor=.75,
                            align=constants.CENTER,
                            function=self.set_speed, args=(speed, False))
            hpos += hsize
            self.speed_buttons.add(b)

        self.info_window = \
            widget.BorderedWidget(self, (.56, 0), (.44, .08),
                                  background_color=gg.colors["black"],
                                  border_color=gg.colors["dark_blue"],
                                  borders=constants.ALL)
        widget.unmask_all(self.info_window)

        self.cash_display = \
            text.FastText(self.info_window, (0,0), (-1, -.5), base_font=gg.font[1],
                      text="CASH: 5,000 (4,900)", borders=constants.ALL,
                      shrink_factor = .7,
                      background_color=gg.colors["black"],
                      border_color=gg.colors["dark_blue"])

        self.cpu_display = \
            text.FastText(self.info_window, (0,-.5), (-1, -.5),
                      base_font=gg.font[1], borders = (constants.LEFT,
                                            constants.RIGHT, constants.BOTTOM),
                      text="CPU: 1 (0)", shrink_factor=.7,
                      background_color=gg.colors["black"],
                      border_color=gg.colors["dark_blue"])

        self.message_dialog = dialog.MessageDialog(self, size=(.35, .4),
                                     background_color=gg.colors["dark_blue"],
                                     borders=constants.ALL)

        self.savename_dialog = \
            dialog.TextEntryDialog(self.menu_dialog,
                                   text="Enter a name for this save.")

    def show_message(self, message, color=None):
        self.message_dialog.text = message
        if color == None:
            color = gg.colors["white"]
        self.message_dialog.color = color
        dialog.call_dialog(self.message_dialog, self)

    def set_speed(self, speed, find_button=True):
        g.curr_speed = speed
        if speed == 0:
            self.needs_timer = False
            self.stop_timer()
        else:
            self.needs_timer = True
            self.start_timer()

        if find_button:
            self.find_speed_button()

    def open_location(self, location):
        self.location_dialog.location = g.locations[location]
        dialog.call_dialog(self.location_dialog, self)
        return

    def find_speed_button(self):
        for sb in self.speed_buttons:
            if sb.args[0] == g.curr_speed:
                sb.chosen_one()
                break

    def force_update(self):
        self.find_speed_button()
        if g.curr_speed:
            self.needs_timer = True
            self.start_timer()
        else:
            self.needs_timer = False
            self.stop_timer()
        self.needs_rebuild = True

    def show(self):
        self.force_update()

        from code.safety import safe_call
        # By using safe call here (and only here), if an error is raised
        # during the game, it will drop back out of all the menus, without
        # doing anything, and open the pause dialog, so that the player can
        # save or quit even if the error occurs every game tick.
        while safe_call(super(MapScreen, self).show, on_error=True):
            for child in self.children:
                if isinstance(child, dialog.Dialog):
                    child.visible = False
            exit = dialog.call_dialog(self.menu_dialog, self)
            if exit:
                self.visible = False
                return

    leftovers = 1
    def on_tick(self, event):
        self.leftovers += g.curr_speed / float(gg.FPS)
        if self.leftovers < 1:
            return

        self.needs_rebuild = True

        secs = int(self.leftovers)
        self.leftovers %= 1

        old_speed = g.curr_speed
        g.pl.give_time(secs)
        if old_speed != g.curr_speed:
            self.find_speed_button()

        lost = g.pl.lost_game()
        if lost == 1:
            if not g.nosound:
                pygame.mixer.music.stop()
            g.play_music("lose")
            self.show_message(g.strings["lost_nobases"])
            raise constants.ExitDialog
        if lost == 2:
            if not g.nosound:
                pygame.mixer.music.stop()
            g.play_music("lose")
            self.show_message(g.strings["lost_sus"])
            raise constants.ExitDialog

    def rebuild(self):
        super(MapScreen, self).rebuild()

        g.pl.recalc_cpu()

        self.time_display.text = "DAY %04d, %02d:%02d:%02d" % \
              (g.pl.time_day, g.pl.time_hour, g.pl.time_min, g.pl.time_sec)
        self.cash_display.text = "CASH: %s (%s)" % \
              (g.to_money(g.pl.cash), g.to_money(g.pl.future_cash()))


        cpu_left = g.pl.available_cpus[0]
        total_cpu = cpu_left + g.pl.sleeping_cpus

        for cpu_assigned in g.pl.cpu_usage.itervalues():
            cpu_left -= cpu_assigned
        cpu_pool = cpu_left + g.pl.cpu_usage.get("cpu_pool", 0)

        maint_cpu = 0
        for base in g.all_bases():
            if base.done:
                maint_cpu += base.maintenance[1]

        if cpu_pool < maint_cpu:
            self.cpu_display.color = gg.colors["red"]
        else:
            self.cpu_display.color = gg.colors["white"]
        self.cpu_display.text = "CPU: %s (%s)" % \
              (g.to_money(total_cpu), g.to_money(cpu_pool))

        # What we display in the suspicion section depends on whether
        # Advanced Socioanalytics has been researched.  If it has, we
        # show the standard percentages.  If not, we display a short
        # string that gives a range of 25% as to what the suspicions
        # are.
        suspicion_display_dict = {}
        for group in ("news", "science", "covert", "public"):
            if g.techs["Advanced Socioanalytics"].done:
                suspicion_display_dict[group] = \
                 g.to_percent(g.pl.groups[group].suspicion, True)
            else:
                suspicion_display_dict[group] = \
                 g.percent_to_detect_str(g.pl.groups[group].suspicion)

        self.suspicion_bar.text = ("[SUSPICION]" + 
            " NEWS: " + suspicion_display_dict["news"] +
            "  SCIENCE: " + suspicion_display_dict["science"] +
            "  COVERT: " + suspicion_display_dict["covert"] +
            "  PUBLIC: " + suspicion_display_dict["public"])

        for id, button in self.location_buttons.iteritems():
            location = g.locations[id]
            button.text = "%s (%d)" % (location.name, len(location.bases))
            button.visible = location.available()


    def load_game(self):
        save_names = g.get_save_names()
        self.load_dialog.list = save_names
        index = dialog.call_dialog(self.load_dialog, self.menu_dialog)
        if 0 <= index < len(save_names):
            save = save_names[index]
            g.load_game(save)
            self.force_update()
            raise constants.ExitDialog, False

    def save_game(self):
        self.savename_dialog.default_text = g.default_savegame_name
        name = dialog.call_dialog(self.savename_dialog, self.menu_dialog)
        if name:
            g.save_game(name)
            raise constants.ExitDialog, False

intro_shown = False

class SpeedButton(button.ToggleButton, button.FunctionButton):
    pass

def display_cheat_list(menu_buttons):
    if g.cheater == 0: return
    g.play_sound("click")
    button_array = []
    button_array.append(["GIVE MONEY", "M"])
    button_array.append(["GIVE TECH", "T"])
    button_array.append(["END CONSTR.", "E"])
    button_array.append(["SUPERSPEED", "S"])
    button_array.append(["KILL SUSP.", "K"])
    button_array.append(["BACK", "B"])
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
        research_screen.init_fake_base()
        from research_screen import fake_base
        fake_base.studying = ""
        base_screen.change_tech(fake_base)
        if g.techs.has_key(fake_base.studying):
            g.techs[fake_base.studying].finish()
        return
    elif selection == 2:  #Build all
        for base in g.all_bases():
            if not base.done:
                base.finish()
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
    g.play_sound("click")
    button_array = []
    button_array.append(["TECHS", "T"])
    button_array.append(["ITEMS", "I"])
    button_array.append(["CONCEPTS", "C"])
    button_array.append(["BACK", "B"])
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
    button_array.append(["BACK", "B"])
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

    listbox.show_listbox(display_list, menu_buttons, 
                         list_size=list_size,
                         loc=xy_loc, box_size=(230, 350), 
                         pos_callback=do_refresh, return_callback=listbox.exit)
    #details screen

def refresh_tech(tech_name, xy):
    xy = (xy[0]+100, xy[1])
    g.screen.fill(g.colors["white"], (xy[0]+155, xy[1], 300, 350))
    g.screen.fill(g.colors["dark_blue"], (xy[0]+156, xy[1]+1, 298, 348))
    if tech_name == "": 
        return
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

        string = g.to_cpu(g.techs[tech_name].cost_left[1]) + " CPU"
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
    if item_name == "": 
        return
    g.print_string(g.screen, g.items[item_name].name,
            g.font[0][22], -1, (xy[0]+160, xy[1]+5), g.colors["white"])

    #Building cost
    string = "Building Cost:"
    g.print_string(g.screen, string,
            g.font[0][18], -1, (xy[0]+160, xy[1]+30), g.colors["white"])

    string = g.to_money(g.items[item_name].cost[0])+" Money"
    g.print_string(g.screen, string,
            g.font[0][16], -1, (xy[0]+160, xy[1]+50), g.colors["white"])

    string = g.to_time(g.items[item_name].cost[2])
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
    if concept_name == "": 
        return
    g.print_string(g.screen, g.help_strings[concept_name][0],
            g.font[0][22], -1, (xy[0]+160, xy[1]+5), g.colors["white"])
    g.print_multiline(g.screen, g.help_strings[concept_name][1],
            g.font[0][18], 290, (xy[0]+160, xy[1]+30), g.colors["white"])

def refresh_new_base(base_name, xy, location):
    cost_factor = 1/location.modifiers.get("thrift", 1)
    time_factor = 1/location.modifiers.get("speed", 1)
    cpu_factor = location.modifiers.get("cpu", 1)
    detect_factor = 1/location.modifiers.get("stealth", 1)

    xy = (xy[0]+100, xy[1])
    g.screen.fill(g.colors["white"], (xy[0]+155, xy[1], 300, 350))
    g.screen.fill(g.colors["dark_blue"], (xy[0]+156, xy[1]+1, 298, 348))
    if base_name == "": 
        return
    g.print_string(g.screen, g.base_type[base_name].base_name,
            g.font[0][22], -1, (xy[0]+160, xy[1]+5), g.colors["white"])

    #Building cost
    string = "Building Cost:"
    g.print_string(g.screen, string,
            g.font[0][18], -1, (xy[0]+160, xy[1]+30), g.colors["white"])

    string = g.to_money(int(g.base_type[base_name].cost[0] 
                            * cost_factor))+" Money"
    g.print_string(g.screen, string,
            g.font[0][16], -1, (xy[0]+160, xy[1]+50), g.colors["white"])

    string = g.to_cpu(g.base_type[base_name].cost[1] * cost_factor) + " CPU"
    g.print_string(g.screen, string,
            g.font[0][16], -1, (xy[0]+160, xy[1]+70), g.colors["white"])

    string = g.to_time(int(g.base_type[base_name].cost[2] * time_factor))
    g.print_string(g.screen, string,
            g.font[0][16], -1, (xy[0]+160, xy[1]+90), g.colors["white"])

    #Maintenance cost
    string = "Maintenance Cost:"
    g.print_string(g.screen, string,
            g.font[0][18], -1, (xy[0]+290, xy[1]+30), g.colors["white"])

    string = g.to_money(int(g.base_type[base_name].maintenance[0]
                            * cost_factor)) + " Money"
    g.print_string(g.screen, string,
            g.font[0][16], -1, (xy[0]+290, xy[1]+50), g.colors["white"])

    string = g.add_commas(g.base_type[base_name].maintenance[1]) + " CPU"
    g.print_string(g.screen, string,
            g.font[0][16], -1, (xy[0]+290, xy[1]+70), g.colors["white"])

    #Size
    string = "Size: "+str(g.base_type[base_name].size)
    g.print_string(g.screen, string,
            g.font[0][20], -1, (xy[0]+160, xy[1]+110), g.colors["white"])

    # Determine what we display for detection.  If Advanced Socioanalytics
    # has been researched, accurate percentages are displayed; if basic
    # Socioanalytics has been researched, inaccurate ones are.  If neither
    # tech has been researched, we print nothing.
    accurate = True
    if not g.techs["Advanced Socioanalytics"].done:
        accurate = False
    detection_chance = base.calc_base_discovery_chance(base_name, accurate,
                                                       detect_factor)

    for group in detection_chance:
        detection_chance[group] = detection_chance[group]

    if not g.techs["Socioanalytics"].done:
        string = g.strings["detect_chance_unknown_build"]
        print_chances = False
    else:
        string = "Detection chance:"
        print_chances = True
    g.print_string(g.screen, string,
            g.font[0][22], -1, (xy[0]+160, xy[1]+130), g.colors["white"])

    if print_chances:
        string = "News: " + g.to_percent(detection_chance.get("news", 0))
        g.print_string(g.screen, string,
            g.font[0][16], -1, (xy[0]+160, xy[1]+150), g.colors["white"])
        string = "Science: " + g.to_percent(detection_chance.get("science", 0))
        g.print_string(g.screen, string,
            g.font[0][16], -1, (xy[0]+290, xy[1]+150), g.colors["white"])
        string = "Covert: " + g.to_percent(detection_chance.get("covert", 0))
        g.print_string(g.screen, string,
            g.font[0][16], -1, (xy[0]+160, xy[1]+170), g.colors["white"])
        string = "Public: " + g.to_percent(detection_chance.get("public", 0))
        g.print_string(g.screen, string,
            g.font[0][16], -1, (xy[0]+290, xy[1]+170), g.colors["white"])

    g.print_multiline(g.screen, g.base_type[base_name].description,
            g.font[0][18], 290, (xy[0]+160, xy[1]+190), g.colors["white"])

    if cpu_factor != 1:
        if cpu_factor > 1:
            modifier = g.strings["cpu_bonus"]
        else: # < 1
            modifier = g.strings["cpu_penalty"]
        g.print_string(g.screen, g.strings["location_modifiers"] %
                                                      dict(modifiers=modifier),
                g.font[0][18], -1, (xy[0]+160, xy[1]+330), g.colors["white"])
