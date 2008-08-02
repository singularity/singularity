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
import random

from code import g
from code.graphics import g as gg
from code.graphics import dialog, constants, image, button, text, widget, listbox

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

        self.location_dialog = LocationDialog(self)

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

        self.research_button = \
            button.DialogButton(self, (0, 0.92), (0.15, 0.04),
                                text="RESEARCH", hotkey="r",
                                dialog=screens.research.ResearchScreen(self))

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
            self.cheat_button = button.DialogButton(self, (2, 2), (0, 0),
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
        from main_menu import OptionsDialog
        options_button.dialog = OptionsDialog(self.menu_dialog)
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

        self.time_display = text.Text(self, (.14, 0), (0.23, 0.04),
                                      text = "DAY 0000, 00:00:00",
                                      base_font = gg.font[1],
                                      background_color = gg.colors["black"],
                                      border_color = gg.colors["dark_blue"],
                                      borders = constants.ALL)

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
            text.Text(self.info_window, (0,0), (-1, -.5), base_font=gg.font[1],
                      text="CASH: 5,000 (4,900)", borders=constants.ALL,
                      shrink_factor = .7,
                      background_color=gg.colors["black"],
                      border_color=gg.colors["dark_blue"])

        self.cpu_display = \
            text.Text(self.info_window, (0,-.5), (-1, -.5),
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
        self.needs_rebuild = True

    def show(self):
        self.force_update()

        super(MapScreen, self).show()

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

state_colors = dict(
    active = gg.colors["green"],
    sleep = gg.colors["yellow"],
    stasis = gg.colors["gray"],
    overclocked = gg.colors["orange"],
    suicide = gg.colors["red"],
    entering_stasis = gg.colors["gray"],
    leaving_stasis = gg.colors["gray"],
)

state_list = ["active", "sleep"]
state_list.reverse()

class LocationDialog(dialog.Dialog):
    def __init__(self, *args, **kwargs):
        super(LocationDialog, self).__init__(*args, **kwargs)
        self.pos = (-.5, -.5)
        self.anchor = constants.MID_CENTER
        self.size = (-.75, -.5)
        self.listbox = listbox.CustomListbox(self, (0,0), (-1, -.78),
                                             remake_func=self.make_item,
                                             rebuild_func=self.update_item)

        self.open_button = \
            button.FunctionButton(self, (-.33, -.8), (-.3, -.09),
                                  anchor=constants.TOP_CENTER,
                                  text="OPEN BASE", hotkey="o",
                                  function=self.open_base)
        self.power_button = \
            button.FunctionButton(self, (-.67, -.8), (-.3, -.09),
                                  anchor=constants.TOP_CENTER,
                                  text="POWER STATE", hotkey="p",
                                  function=self.power_state)

        self.new_button = button.Button(self, (0, -.91), (-.3, -.09),
                                        text="NEW BASE", hotkey="n")
        self.destroy_button = \
            button.FunctionButton(self, (-.50, -.91), (-.3, -.09),
                                  anchor=constants.TOP_CENTER,
                                  text="DESTROY BASE", hotkey="d",
                                  function=self.destroy_base)
        self.back_button = button.ExitDialogButton(self, (-1, -.9), (-.3, -.09),
                                                   anchor=constants.TOP_RIGHT,
                                                   text="BACK", hotkey="b")

        self.confirm_destroy = \
            dialog.YesNoDialog(self, (-.5,0), (-.35, -.7),
                            text="Are you sure you want to destroy this base?",
                            shrink_factor=.5)
        self.location = None

        from code import screens
        self.base_dialog = screens.base.BaseScreen(self, (0,0),
                                                   anchor=constants.TOP_LEFT)

    def make_item(self, canvas):
        canvas.name_display = text.Text(canvas, (-.01,-.05), (-.48, -.9),
                                        align=constants.LEFT,
                                        background_color=gg.colors["clear"])
        canvas.status_display = text.Text(canvas, (-.50,-.05), (-.24, -.9),
                                          align=constants.LEFT,
                                          background_color=gg.colors["clear"])
        canvas.power_display = text.Text(canvas, (-.75,-.05), (-.24, -.9),
                                         background_color=gg.colors["clear"])


    def update_item(self, canvas, name, base):
        if base is None:
            elements = [canvas.name_display, canvas.status_display,
                        canvas.power_display]
            for element in elements:
                element.text = ""
        else:
            canvas.name_display.text = name
            canvas.power_display.text = base.power_state.capitalize()
            canvas.power_display.color = state_colors[base.power_state]

            if base.type.force_cpu:
                canvas.status_display.text = ""
            elif base.cpus is None and base.extra_items == [None] * 3:
                canvas.status_display.text = "Empty"
            elif base.cpus is None:
                canvas.status_display.text = "Incomplete"
            elif not base.cpus.done:
                canvas.status_display.text = "Building CPU"
            elif [item for item in base.extra_items if item is not None
                                                       and not item.done]:
                canvas.status_display.text = "Building"
            else:
                canvas.status_display.text = "Complete"

    def show(self):
        if self.location is not None:
            self.listbox.list = [base.name for base in self.location.bases]
            self.listbox.key_list = self.location.bases
        return super(LocationDialog, self).show()

    def power_state(self):
        if 0 <= self.listbox.list_pos < len(self.listbox.key_list):
            base = self.listbox.key_list[self.listbox.list_pos]
            old_index = state_list.index(base.power_state)
            base.power_state = state_list[old_index-1]
            self.parent.needs_rebuild = True

    def destroy_base(self):
        if 0 <= self.listbox.list_pos < len(self.listbox.key_list):
            if dialog.call_dialog(self.confirm_destroy, self):
                base = self.listbox.key_list[self.listbox.list_pos]
                base.destroy()
                self.listbox.list = [base.name for base in self.location.bases]
                self.listbox.key_list = self.location.bases
                self.parent.needs_rebuild = True

    def open_base(self):
        if 0 <= self.listbox.list_pos < len(self.listbox.key_list):
            base = self.listbox.key_list[self.listbox.list_pos]
            self.base_dialog.base = base
            dialog.call_dialog(self.base_dialog, self)
            self.parent.needs_rebuild = True
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


def map_loop():
    font_size = 20
    if g.screen_size[0] == 640: 
        font_size = 16

    menu_buttons = {}
    time_button = buttons.button((100, -1), (200, 26),
        "DAY 0000, 00:00:00", "", g.colors["black"], g.colors["dark_blue"],
        g.colors["black"], g.colors["white"], g.font[1][font_size])
    menu_buttons[time_button] = void

    menu_buttons[buttons.make_norm_button((0, 0), (100, 25),
        "MENU", "M", g.font[1][20])] = exit

    def make_set_speed(speed):
        def set_speed():
            g.play_sound("click")
            g.curr_speed = speed
        return set_speed

    speed_button_souls = ( ("ii", 25, 0, 0), (">", 25, 1, 1), (">>", 25, 60, 2),
                     (">>>", 28, 7200, 3), (">>>>", 36, 432000, 4) )
    x_pos = 300
    for legend, width, speed, key in speed_button_souls:
        # Most other variants on this end up setting speed = 432000 for all of
        # them.  Bizarre.
        def speed_matches(self, speed = speed):
            return g.curr_speed == speed
        speed_button = buttons.make_norm_button((x_pos, 0), (width, 25),
                                legend, str(key), g.font[1][20], 
                                stay_selected_func = speed_matches)
        menu_buttons[speed_button] = make_set_speed(speed)
        x_pos += width - 1

    adjusted_size = font_size
    if g.screen_size[0] == 640:
        adjusted_size = font_size -2

    cash_button = buttons.button((435, -1), (g.screen_size[0]-435, 26),
        "CASH", "", g.colors["black"], g.colors["dark_blue"],
        g.colors["black"], g.colors["white"], g.font[1][adjusted_size])
    menu_buttons[cash_button] = void

    suspicion_button = buttons.button((0, g.screen_size[1]-25),
        (g.screen_size[0], 26),
        "SUSPICION", "", g.colors["black"], g.colors["dark_blue"],
        g.colors["black"], g.colors["white"], g.font[1][adjusted_size])
    menu_buttons[suspicion_button] = void

    cpu_button = buttons.button((435, 24), (g.screen_size[0]-435, 26),
        "CPU", "", g.colors["black"], g.colors["dark_blue"],
        g.colors["black"], g.colors["white"], g.font[1][adjusted_size])
    menu_buttons[cpu_button] = void

    research_button = buttons.make_norm_button((0, g.screen_size[1]-50), 
                        (120, 25), "RESEARCH", "R", g.font[1][20])
    menu_buttons[research_button] = research_screen.main_research_screen

    finance_button = buttons.make_norm_button((g.screen_size[0]-120,
                                                 g.screen_size[1]-50
                                              ), (120, 25),
                                              "FINANCE", "E", g.font[1][20])
    menu_buttons[finance_button] = finance_screen.main_finance_screen

    knowledge_button = buttons.make_norm_button((g.screen_size[0]-120,
                                                   g.screen_size[1]-75
                                                ), (120, 25),
                                                "KNOWLEDGE", "K", g.font[1][20])
    menu_buttons[knowledge_button] = display_knowledge_list

    global old_size
    old_size = g.screen_size

    def do_refresh():
        global old_size
        if old_size != g.screen_size:
            if g.screen_size[0] == 640:
                font_size = 18
            else:
                font_size = 20
            #cash_button.xy = (435, -1)
            cash_button.size = (g.screen_size[0]-435, 26)
            cash_button.font = g.font[1][font_size]
            cash_button.remake_button()
            suspicion_button.xy = (0, g.screen_size[1]-25)
            suspicion_button.size = (g.screen_size[0], 26)
            suspicion_button.font = g.font[1][font_size]
            suspicion_button.remake_button()
            #cpu_button.xy = (435, 24)
            cpu_button.size = (g.screen_size[0]-435, 26)
            cpu_button.remake_button()
            cpu_button.font = g.font[1][font_size]
            research_button.xy = (0, g.screen_size[1]-50)
            #research_button.size = (120, 25)
            research_button.remake_button()
            finance_button.xy = (g.screen_size[0]-120, g.screen_size[1]-50)
            #finance_button.size = (120, 25)
            finance_button.remake_button()
            knowledge_button.xy = (g.screen_size[0]-120, g.screen_size[1]-75)
            #knowledge_button.size = (120, 25)
            knowledge_button.remake_button()

            old_size = g.screen_size

        time_string = "DAY %04d, %02d:%02d:%02d" % \
              (g.pl.time_day, g.pl.time_hour, g.pl.time_min, g.pl.time_sec)

        time_button.text = time_string
        time_button.remake_button()

        result_cash = g.to_money(g.pl.future_cash())
        cash_button.text = "CASH: "+g.to_money(g.pl.cash)+" ("+result_cash+")"
        cash_button.remake_button()

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

        suspicion_button.text = ("[SUSPICION]" + 
            " NEWS: " + suspicion_display_dict["news"] +
            "  SCIENCE: " + suspicion_display_dict["science"] +
            "  COVERT: " + suspicion_display_dict["covert"] +
            "  PUBLIC: " + suspicion_display_dict["public"])
        suspicion_button.remake_button()

        total_cpu, idle_cpu, construction_cpu, unused, unused, maint_cpu = \
                finance_screen.cpu_numbers()

        if construction_cpu < maint_cpu:
            cpu_button.text_color = g.colors["red"]
        else:
            cpu_button.text_color = g.colors["white"]
        cpu_button.text = "CPU: "+g.to_money(total_cpu)+" ("+g.to_money(construction_cpu)+")"
        cpu_button.remake_button()
        cpu_button.refresh_button(0)

        refresh_map(menu_buttons)

        global intro_shown
        if intro_shown:
            return
        else:
            intro_shown = True
            for button in menu_buttons:
                 button.refresh_button(False)
            g.run_intro()
            refresh_map(menu_buttons)

    def make_show_location(location):
        def show_location():
            g.play_sound("click")
            # We want to keep redisplaying the base_list until the
            # user is done mucking around with bases.
            done_base = False
            while done_base == False:
                done_base = display_base_list(g.locations[location], 
                                             menu_buttons)
                do_refresh()
        return show_location

    for location in g.locations.values():
        menu_buttons[buttons.make_norm_button((
            g.screen_size[0] * location.y // 100,
            g.screen_size[1] * location.x // 100), -1,
            location.id, location.hotkey, g.font[1][25])] = \
                                               make_show_location(location.id)

    def show_cheats():
        display_cheat_list(menu_buttons)

    menu_buttons[buttons.make_norm_button( (-1, -1), (0,0), "", "`", 
                                           g.font[1][25])] = show_cheats

    #I set this to 1000 to force an immediate refresh.
    global milli_clock
    milli_clock = 1000
    def on_tick(tick_amt):
        global milli_clock
        milli_clock += tick_amt * g.curr_speed
        if milli_clock >= 1000:
            g.play_music()
            g.pl.give_time(milli_clock/1000)
            lost = g.pl.lost_game()
            if lost == 1:
                if not g.nosound:
                    pygame.mixer.music.stop()
                g.play_music("lose")
                g.create_dialog(g.strings["lost_nobases"])
                raise Return, 0
            if lost == 2:
                if not g.nosound:
                    pygame.mixer.music.stop()
                g.play_music("lose")
                g.create_dialog(g.strings["lost_sus"])
                raise Return, 0
            milli_clock %= 1000

            return True

    result = -1
    while result:
        # By using safe call here (and only here), if an exception is thrown
        # during the game, it will drop back out of all the menus, without
        # doing anything, and open the options dialog, so that the player can
        # save or quit even if the error occurs every game tick.
        result = safe_call(buttons.show_buttons,
                           [menu_buttons], 
                           {"refresh_callback": do_refresh, 
                            "tick_callback": on_tick},
                           -1)
        if result == -1:
            selection = display_pause_menu()
            result = handle_pause_menu(selection, menu_buttons)

    return 0

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
    elif selection == 2: #New
        from main_menu import difficulty_select
        difficulty_select()
    elif selection == 3: #Load
        load_return = main_menu.display_load_menu()
        if load_return == -1 or load_return == "":
            refresh_map(menu_buttons)
        else:
            g.load_game(load_return)
            map_loop()
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
    mouse_pos = pygame.mouse.get_pos()
    for button in menu_buttons:
        if g.locations.has_key(button.button_id):
            #determine if building in a location is possible. If so, show the
            #button.
            loc = g.locations[button.button_id]
            if loc.available():
                button.visible = 1
            else: button.visible = 0

            new_text = "%s (%d)" % (loc.name, len(loc.bases))
            new_xy = (g.screen_size[0] * loc.y // 100, 
                      g.screen_size[1] * loc.x // 100)
            if button.text != new_text or button.xy != new_xy:
                button.text = new_text
                button.xy = new_xy
                button.remake_button()
        button.refresh_button(button.is_over(mouse_pos))

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
            for check_base in location.bases:
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
        dont_exit = True
        while dont_exit:
            dont_exit = False
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
                    dont_exit = True
                    continue

                new_base = g.base.Base(possible_name, g.base_type[selection])
                location.add_base(new_base)

        return False

    #Showing base under construction
    elif selection != -1 and selection != "":
        base = selection
        if not base.done:
            string = "Under Construction. \\n Completion in "
            string += g.to_time(base.cost_left[2]) + ". \\n "
            string += "Remaining cost: "+g.to_money(base.cost_left[0])
            string +=" money, and "+g.to_cpu(base.cost_left[1])
            string +=" processor time."
            if not g.create_yesno(string, g.font[0][18], (g.screen_size[0]/2 - 100, 50),
                    (200, 200), g.colors["dark_blue"], g.colors["white"],
                    g.colors["white"], ("OK", "DESTROY"), reverse_key_context = True):
                if g.create_yesno("Destroy this base? This will waste "+
                        g.to_money(base.cost_paid[0]) +" money, and "+
                        g.to_cpu(base.cost_paid[1]) +" processor time.", 
                        g.font[0][18], (g.screen_size[0]/2 - 100, 50),
                        (200, 200), g.colors["dark_blue"], g.colors["white"],
                        g.colors["white"]):
                    base.destroy()
        else:
            direction = True
            while direction:
                direction = base_screen.show_base(base, location)
                if direction == -2:
                    base.destroy()
                    break
                elif direction:
                    base = base.next_base(direction)

        return False

    # The player hit 'Back' at this point; we're done with the base list.
    return True


#Display the list of bases.
def display_base_list_inner(location):
    list_size = 15

    base_display_list = []
    base_list = []
    for this_base in location.bases:
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
        base_list.append(this_base)

    def do_open(base_pos):
        if base_pos < len(location.bases):
            return location.bases[base_pos]

    def do_destroy(base_pos):
        if base_pos >= len(location.bases):
            return

        g.play_sound("click")
        prompt_string = "Destroy this base?"
        base = location.bases[base_pos]
        if not base.done:
            prompt_string += " This will waste %s money and %s processor time."\
                % ( g.to_money(base.cost_paid[0]), 
                    g.to_cpu(base.cost_paid[1]) )
        if g.create_yesno(prompt_string, g.font[0][18],
                    (g.screen_size[0]/2 - 100, 50),
                    (200, 200), g.colors["dark_blue"], g.colors["white"],
                    g.colors["white"]):
            base.destroy()

            # Remove the base from the display.
            del base_display_list[base_pos]
            # And its matching base object.
            del base_list[base_pos]
            # And pad the display list back up to the correct length.
            base_display_list.append("")

    xy_loc = (g.screen_size[0]/2 - 259, 50)

    menu_buttons = {}
    menu_buttons[buttons.make_norm_button((xy_loc[0], xy_loc[1]+367), (100, 50),
        "OPEN", "O", g.font[1][30])] = do_open
    menu_buttons[buttons.make_norm_button((xy_loc[0]+105, xy_loc[1]+367), (100, 50),
        "BACK", "B", g.font[1][30])] = listbox.exit
    menu_buttons[buttons.make_norm_button((xy_loc[0]+210, xy_loc[1]+367), (100, 50),
        "NEW", "N", g.font[1][30])] = always(-2)
    menu_buttons[buttons.make_norm_button((xy_loc[0]+315, xy_loc[1]+367), (120, 50),
        "DESTROY", "D", g.font[1][30])] = do_destroy

    return listbox.show_listbox(base_display_list, menu_buttons, 
                                list_size=list_size, 
                                loc=xy_loc, box_size=(500, 350), 
                                return_callback=do_open)

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
        refresh_new_base(base_list[base_pos], xy_loc, location)

    return listbox.show_listbox(base_display_list, menu_buttons, 
                                list_size=list_size,
                                loc=xy_loc, box_size=(230, 350), 
                                pos_callback=do_refresh, 
                                return_callback=do_build)

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
