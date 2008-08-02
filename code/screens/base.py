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

import code.g as g
import code.graphics.g as gg
from code.graphics import constants, widget, dialog, text, button, listbox

class BuildDialog(dialog.ChoiceDescriptionDialog):
    type = widget.causes_rebuild("_type")
    def __init__(self, parent, pos = (0, 0), size = (-1, -1),
                 anchor = constants.TOP_LEFT, *args, **kwargs):
        super(BuildDialog, self).__init__(parent, pos, size, anchor, *args, 
                                          **kwargs)

        self.type = None
        self.desc_func = self.on_change

    def show(self):
        self.list = []
        self.key_list = []

        item_list = g.items.values()
        item_list.sort()
        item_list.reverse()
        for item in item_list:
            if item.item_type == self.type:
                self.list.append(item.name)
                self.key_list.append(item.id)

        self.default = self.parent.get_current(self.type).type.id

        super(BuildDialog, self).show()

    def on_change(self, description_pane, key):
        text.Text(description_pane, (0, 0), (-1, -1), text = key)

# XXX Replace with the real data.
type_names = dict(cpu = "Processor", reactor = "Reactor",
                  network = "Network", security = "Security")

class ItemPane(widget.BorderedWidget):
    type = widget.causes_rebuild("_type")
    def __init__(self, parent, pos, size = (.48, .06), 
                 anchor = constants.TOP_LEFT,
                 type = "cpu", **kwargs):

        kwargs.setdefault("background_color", gg.colors["dark_blue"])

        super(ItemPane, self).__init__(parent, pos, size, anchor = anchor,
                                       **kwargs)

        self.type = type

        self.name_panel = text.Text(self, (0,0), (.35, .03),
                                    anchor=constants.TOP_LEFT,
                                    align=constants.LEFT,
                                    background_color=self.background_color,
                                    bold=True)

        self.build_panel = text.Text(self, (0,.03), (.35, .03),
                                     anchor=constants.TOP_LEFT,
                                     align=constants.LEFT,
                                     background_color=self.background_color,
                                     text="Completion in 15 hours.", bold=True)

        #TODO: Use information out of gg.buttons
        change_text = "CHANGE"
        hotkey_dict = dict(cpu = "p", reactor = "r", network = "n",
                           security = "s")
        hotkey = hotkey_dict[self.type]
        button_text = "%s (%s)" % (change_text, hotkey.upper())

        self.change_button = button.FunctionButton(self, (.36,.01), (.12, .04),
                                                   anchor = constants.TOP_LEFT,
                                                   text = button_text, 
                                                   hotkey = hotkey,
                                                   function =
                                                self.parent.parent.build_item,
                                                   kwargs = {"type": self.type})

        if hotkey.upper() in change_text:
            hotkey_pos = len(change_text) + 2
            self.change_button.force_underline = hotkey_pos

state_colors = dict(
    active = gg.colors["green"],
    sleep = gg.colors["yellow"],
    stasis = gg.colors["gray"],
    overclocked = gg.colors["orange"],
    suicide = gg.colors["red"],
    entering_stasis = gg.colors["gray"],
    leaving_stasis = gg.colors["gray"],
)

class BaseScreen(dialog.Dialog):
    base = widget.causes_rebuild("_base")
    def __init__(self, *args, **kwargs):
        if len(args) < 3:
            kwargs.setdefault("size", (.75, .5))
        base = kwargs.pop("base", None)
        super(BaseScreen, self).__init__(*args, **kwargs)

        self.base = base

        self.build_dialog = BuildDialog(self)

        self.header = widget.Widget(self, (0,0), (-1, .08), 
                                    anchor = constants.TOP_LEFT)

        self.name_display = text.Text(self.header, (-.5,0), (-1, -.5),
                                      anchor = constants.TOP_CENTER,
                                      borders = constants.ALL,
                                      border_color = gg.colors["dark_blue"],
                                      background_color = gg.colors["black"],
                                      shrink_factor = .85, bold = True)

        self.next_base_button = \
            button.FunctionButton(self.name_display, (-1, 0), (.03, -1),
                                  anchor = constants.TOP_RIGHT,
                                  text = ">", hotkey = ">",
                                  function = self.switch_base,
                                  kwargs = {"forwards": True})
        self.add_key_handler(pygame.K_RIGHT, self.next_base_button.activate_with_sound)

        self.prev_base_button = \
            button.FunctionButton(self.name_display, (0, 0), (.03, -1),
                                  anchor = constants.TOP_LEFT,
                                  text = "<", hotkey = "<",
                                  function = self.switch_base,
                                  kwargs = {"forwards": False})
        self.add_key_handler(pygame.K_LEFT, self.prev_base_button.activate_with_sound)

        self.state_display = text.Text(self.header, (-.5,-.5), (-1, -.5),
                                       anchor = constants.TOP_CENTER,
                                       borders =(constants.LEFT,constants.RIGHT,
                                                 constants.BOTTOM),
                                       border_color = gg.colors["dark_blue"],
                                       background_color = gg.colors["black"],
                                       shrink_factor = .8, bold = True)

        self.back_button = \
            button.ExitDialogButton(self, (-.5,-1),
                                    anchor = constants.BOTTOM_CENTER,
                                    text = "back", hotkey = "b")

        self.detect_frame = text.Text(self, (-1, .09), (.21, .33),
                                      anchor = constants.TOP_RIGHT,
                                      background_color = gg.colors["dark_blue"],
                                      borders = constants.ALL,
                                      wrap = False, bold = True,
                                      align = constants.LEFT, 
                                      valign = constants.TOP)

        self.contents_frame = \
            widget.BorderedWidget(self, (0, .09), (.50, .33),
                                  anchor = constants.TOP_LEFT,
                                  background_color = gg.colors["dark_blue"],
                                  borders = range(6))

        self.cpu_pane      = ItemPane(self.contents_frame, (.01, .01),
                                      type = "cpu")
        self.reactor_pane  = ItemPane(self.contents_frame, (.01, .09),
                                      type = "reactor")
        self.network_pane  = ItemPane(self.contents_frame, (.01, .17),
                                      type = "network")
        self.security_pane = ItemPane(self.contents_frame, (.01, .25),
                                      type = "security")

    def get_current(self, type):
        if type == "cpu":
            target = self.base.cpus
        else:
            index = ["reactor", "network", "security"].index(type)
            target = self.base.extra_items[index]
        if target is not None:
            return target

    def build_item(self, type):
        self.build_dialog.type = type
        result = dialog.call_dialog(self.build_dialog, self)
        if result:
            self.do_build_item(type, result)

    def switch_base(self, forwards):
        self.base = self.base.next_base(forwards)
        self.needs_rebuild = True

    def rebuild(self):
        self.name_display.text="%s (%s)" % (self.base.name, self.base.type.name)
        discovery_template = \
"""DISCOVERY CHANCE:
News: %s
Science: %s
Covert: %s
Public: %s"""
        self.state_display.color = state_colors[self.base.power_state]
        self.state_display.text = self.base.power_state.capitalize()

        mutable = not self.base.type.force_cpu
        for item in ["cpu", "reactor", "network", "security"]:
            pane = getattr(self, item + "_pane")
            pane.change_button.visible = mutable
            current = self.get_current(item)
            if current is None:
                current_name = "None"
                current_build = ""
            else:
                current_name = current.name
                if current.done:
                    current_build = ""
                else:
                    current_build = "Completion in %s." % \
                        g.to_time(current.cost_left[2])
            pane.name_panel.text = "%s: %s" % (type_names[item], current_name)
            pane.build_panel.text = current_build

        # Detection chance display.  If Socioanalytics hasn't been researched,
        # you get nothing; if it has, but not Advanced Socioanalytics, you get
        # an inaccurate value.
        if not g.techs["Socioanalytics"].done:
            self.detect_frame.text = \
                g.strings["detect_chance_unknown_base"].replace(" ", "\n")
        else: 
            accurate = g.techs["Advanced Socioanalytics"].done
            chance = self.base.get_detect_chance(accurate)
            def get_chance(group):
                return g.to_percent(chance.get(group, 0))
            self.detect_frame.text = discovery_template % \
                (get_chance("news"), get_chance("science"),
                 get_chance("covert"), get_chance("public"))
        super(BaseScreen, self).rebuild()

def old_detection_chance():
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

def old_build_item(this_base, item_type, location):
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
            try: 
                g.items[item_name].buildable.index(location)
            except ValueError: 
                continue
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
    if item_name == "": 
        return
    if item_type == "compute":
        for i, cpu in enumerate(this_base.cpus):
            if cpu != 0 and cpu.type.id == g.items[item_name].id:
                continue
            this_base.cpus[i] = g.item.Item(g.items[item_name], this_base)
    elif item_type == "react":
        if this_base.extra_items[0] != 0:
            if this_base.extra_items[0].type.id == g.items[item_name].id:
                return
        this_base.extra_items[0] = g.item.Item(g.items[item_name], this_base)
    elif item_type == "network":
        if this_base.extra_items[1] != 0:
            if this_base.extra_items[1].type.id == g.items[item_name].id:
                return
        this_base.extra_items[1] = g.item.Item(g.items[item_name], this_base)
    elif item_type == "security":
        if this_base.extra_items[2] != 0:
            if this_base.extra_items[2].type.id == g.items[item_name].id:
                return
        this_base.extra_items[2] = g.item.Item(g.items[item_name], this_base)


def old_change_tech(this_base, select_this = None):
    item_list = []
    item_list2 = []
    #TECH
    for tech_name in g.techs:
        if not g.techs[tech_name].done and this_base.allow_study(tech_name):
            if g.techs[tech_name].available():
                item_list.append(g.techs[tech_name].name)
                item_list2.append(tech_name)
    #SPECIALS
    item_list.append("---")
    item_list2.append("")
    if this_base.location:
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
    if select_this and select_this in item_list2:
        list_pos = item_list2.index(select_this)

    return listbox.show_listbox(item_list, menu_buttons, list_pos=list_pos, 
                                pos_callback=do_refresh, 
                                return_callback=change_study)



def old_refresh_tech(this_base, tech_name, xy):
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
