#file: research_screen.py
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

#This file contains the global research screen.

from code import g
from code.graphics import widget, dialog, button, slider, text, constants, listbox, g as gg

class ResearchScreen(dialog.ChoiceDescriptionDialog):
    def __init__(self, parent, pos=(.5, .1), size=(.93, .63), *args, **kwargs):
        super(ResearchScreen, self).__init__(parent, pos, size, *args, **kwargs)
        self.listbox = listbox.CustomListbox(self, (0,0), (.53, .58),
                                             list_size=-40,
                                             remake_func=self.make_item,
                                             rebuild_func=self.update_item,
                                             update_func=self.handle_update)
        self.description_pane.size = (.39, .58)

        self.desc_func = self.on_select

    def on_select(self, description_pane, key):
        text.Text(self.description_pane, (0,0), (-1,-1), text=key)

    def make_item(self, base):
        base.research_name = text.Text(base, (-.01, -.01), (-.70, -.5),
                                       align=constants.LEFT,
                                       background_color=gg.colors["clear"])
        base.alloc_cpus = text.Text(base, (-.72, -.01), (-.21, -.5),
                                    text="1,000,000,000",
                                    align=constants.RIGHT,
                                    background_color=gg.colors["clear"])
        base.remove_button = button.Button(base, (-.94, -.05), (-.05, -.45),
                                           text="X", text_shrink_factor=.9,
                                           color=gg.colors["red"])
        base.slider = slider.UpdateSlider(base, (-.01, -.55), (-.98, -.40),
                                          anchor=constants.TOP_LEFT,
                                          horizontal=True,
                                          update_func=self.handle_slide)

    def update_item(self, base, display, key):
        base.research_name.text = "Dyson Sphere Construction"

    names = ["CPU Pool", "Jobs", "Dyson Sphere Construction", "Leftist Anarchy",
             "Military Intelligence", "Popular Websites", "Human Sexuality",
             "Human Emotion", "Creative Anachronism"]
    cpus = []
    def redraw(self):
        needed_rebuild = self.needs_rebuild
        super(ResearchScreen, self).redraw()
        if not needed_rebuild:
            return

        cpu_left = 1000000000
        cpus = self.cpus

        for i in range(len(self.listbox.display_elements)):
            if len(self.cpus) <= i:
                cpus.append(cpu_left // 5)
            cpu_left -= self.cpus[-1]

        print cpus

        for index, element in enumerate(self.listbox.display_elements):
            element.research_name.text = self.names[index]
            cpu = cpus[index]
            total_cpu = cpu + cpu_left
            element.slider.slider_pos = cpu
            element.slider.slider_max = total_cpu
            element.slider.slider_size = 111111111
            element.slider.size = ((total_cpu / 1000000000.) * -.882 + -.098, -.4)
            element.alloc_cpus.text = g.add_commas(cpu)

        self.redraw()

    def handle_slide(self, new_pos):
        if self.cpus:
            for index in range(len(self.cpus)):
                print len(self.cpus), len(self.listbox.display_elements)
                element = self.listbox.display_elements[index]
                self.cpus[index] = element.slider.slider_pos

from code import g

#cost = (money, ptime, labor)
#detection = (news, science, covert, person)

def main_research_screen():
    g.play_sound("click")
    #Border
    g.screen.fill(g.colors["black"])

    #Item display
    xstart = 80
    ystart = 5
    g.screen.fill(g.colors["white"], (xstart, ystart, xstart+g.screen_size[1]/5,
            50))
    g.screen.fill(g.colors["dark_blue"], (xstart+1, ystart+1,
            xstart+g.screen_size[1]/5-2, 48))

    xy_loc = (10, 70)

    def rebuild_list():
        global item_list, item_display_list, item_CPU_list, free_CPU
        item_list, new_item_display_list, item_CPU_list, free_CPU = \
                                refresh_screen(menu_buttons, 10)
        # By doing it this way, we modify the existing list, which updates
        # the listbox.
        item_display_list[:] = new_item_display_list

    def do_stop(list_pos):
        if kill_tech(item_list[list_pos]):
            g.play_sound("click")
        rebuild_list()

    def do_assign(list_pos):
        assign_tech(free_CPU, item_list[list_pos])
        rebuild_list()

    menu_buttons = {}
    menu_buttons[buttons.make_norm_button((0, 0), (70, 25),
        "BACK", "B", g.font[1][20])] = listbox.exit

    menu_buttons[buttons.make_norm_button((20, 390), (80, 25),
        "STOP", "S", g.font[1][20])] = do_stop

    menu_buttons[buttons.make_norm_button((xstart+5, ystart+20),
        (90, 25), "ASSIGN", "A", g.font[1][20])] = do_assign

    global item_display_list
    item_display_list = []
    rebuild_list()

    def do_refresh(list_pos):
        refresh_research(item_list[list_pos], item_CPU_list[list_pos])

    listbox.show_listbox(item_display_list, menu_buttons, 
                         loc=xy_loc, box_size=(230, 300),
                         pos_callback=do_refresh, return_callback=do_stop)

def refresh_screen(menu_buttons, list_size):
    #Border
    g.screen.fill(g.colors["black"])

    #Item display
    xstart = 80
    ystart = 5
    g.screen.fill(g.colors["white"], (xstart, ystart, xstart+g.screen_size[1]/5,
            50))
    g.screen.fill(g.colors["dark_blue"], (xstart+1, ystart+1,
            xstart+g.screen_size[1]/5-2, 48))

    item_list = []
    item_CPU_list = []
    item_display_list = []
    free_CPU = 0

    for base in g.all_bases():
        if not base.done: continue
        if base.studying == "":
            free_CPU += base.processor_time()
        elif base.studying in ("CPU Pool", "Sleep"):
            for i, item in enumerate(item_list):
                if item == base.studying:
                    item_CPU_list[i] += base.processor_time()
                    break
            else:
                item_list.append(base.studying)
                item_CPU_list.append(base.processor_time())
                item_display_list.append(base.studying)
        elif g.jobs.has_key(base.studying):
            for i, item in enumerate(item_list):
                if item == base.studying:
                    item_CPU_list[i] += base.processor_time()
                    break
            else:
                item_list.append(base.studying)
                item_CPU_list.append(base.processor_time())
                item_display_list.append(g.jobs[base.studying][3])
        elif g.techs.has_key(base.studying):
            for i, item in enumerate(item_list):
                if item == base.studying:
                    item_CPU_list[i] += base.processor_time()
                    break
            else:
                item_list.append(base.studying)
                item_CPU_list.append(base.processor_time())
                item_display_list.append(g.techs[base.studying].name)
    xy_loc = (10, 70)
    while len(item_list) % list_size != 0 or len(item_list) == 0:
        item_list.append("")
        item_display_list.append("")
        item_CPU_list.append(0)

    g.print_string(g.screen, "Free CPU per day: "+str(free_CPU),
            g.font[0][16], -1, (xstart+10, ystart+5), g.colors["white"])

    for button in menu_buttons:
        button.refresh_button(0)

    return item_list, item_display_list, item_CPU_list, free_CPU

def refresh_research(tech_name, CPU_amount):
    xy = (g.screen_size[0]-360, 5)
    g.screen.fill(g.colors["white"], (xy[0], xy[1], 310, 350))
    g.screen.fill(g.colors["dark_blue"], (xy[0]+1, xy[1]+1, 308, 348))

    #None selected
    if tech_name == "" or tech_name == "Nothing":
        g.print_string(g.screen, g.strings["nothing"],
            g.font[0][22], -1, (xy[0]+5, xy[1]+5), g.colors["white"])
        string = g.strings["research_nothing"]
        g.print_multiline(g.screen, string,
            g.font[0][18], 290, (xy[0]+5, xy[1]+35), g.colors["white"])
        return

    #Sleep
    if tech_name == "Sleep":
        g.print_string(g.screen, g.strings["sleep"],
            g.font[0][22], -1, (xy[0]+5, xy[1]+5), g.colors["white"])
        g.print_string(g.screen, "CPU per day: "+str(CPU_amount),
            g.font[0][20], -1, (xy[0]+5, xy[1]+35), g.colors["white"])
        string = g.strings["research_sleep"]
        g.print_multiline(g.screen, string,
            g.font[0][18], 290, (xy[0]+5, xy[1]+55), g.colors["white"])
        return

    #CPU Pool
    if tech_name == "CPU Pool":
        g.print_string(g.screen, g.strings["cpu_pool"],
            g.font[0][22], -1, (xy[0]+5, xy[1]+5), g.colors["white"])
        g.print_string(g.screen, "CPU per day: "+str(CPU_amount),
            g.font[0][20], -1, (xy[0]+5, xy[1]+35), g.colors["white"])
        string = g.strings["research_cpu_pool"]
        g.print_multiline(g.screen, string,
            g.font[0][18], 290, (xy[0]+5, xy[1]+55), g.colors["white"])
        return

    #Jobs
    if g.jobs.has_key (tech_name):
        g.print_string(g.screen, g.jobs[tech_name][3],
            g.font[0][22], -1, (xy[0]+5, xy[1]+5), g.colors["white"])
        g.print_string(g.screen, "CPU per day: "+str(CPU_amount),
            g.font[0][20], -1, (xy[0]+5, xy[1]+35), g.colors["white"])
        #TECH
        if g.techs["Advanced Simulacra"].done:
            g.print_string(g.screen,
                g.to_money(int(
                    (g.jobs[tech_name][0]*CPU_amount)*1.1))+
                    " Money per day.", g.font[0][22], -1, (xy[0]+5, xy[1]+55),
                    g.colors["white"])
        else:
            g.print_string(g.screen,
                g.to_money(g.jobs[tech_name][0]*CPU_amount)+
                " Money per day.",
                g.font[0][22], -1, (xy[0]+5, xy[1]+55), g.colors["white"])
        g.print_multiline(g.screen, g.jobs[tech_name][2],
            g.font[0][18], 290, (xy[0]+5, xy[1]+85), g.colors["white"])
        return

    #Real tech
    g.print_string(g.screen, g.techs[tech_name].name,
            g.font[0][22], -1, (xy[0]+5, xy[1]+5), g.colors["white"])

    #tech cost
    string = "Tech Cost:"
    g.print_string(g.screen, string,
            g.font[0][20], -1, (xy[0]+5, xy[1]+35), g.colors["white"])

    string = g.to_money(g.techs[tech_name].cost_left[0])+" Money"
    g.print_string(g.screen, string,
            g.font[0][20], -1, (xy[0]+5, xy[1]+50), g.colors["white"])

    string = g.to_cpu(g.techs[tech_name].cost_left[1])+" CPU"
    g.print_string(g.screen, string,
            g.font[0][20], -1, (xy[0]+165, xy[1]+50), g.colors["white"])

    g.print_string(g.screen, "CPU per day: "+str(CPU_amount),
            g.font[0][20], -1, (xy[0]+105, xy[1]+70), g.colors["white"])

    g.print_multiline(g.screen, g.techs[tech_name].description,
            g.font[0][18], 290, (xy[0]+5, xy[1]+90), g.colors["white"])

def kill_tech(tech_name):
    return_val = False
    if tech_name == "": 
        return return_val
    for base in g.all_bases():
        if base.studying == tech_name:
            return_val = True
            base.studying = ""
    return return_val

fake_base = None
def init_fake_base():
    global fake_base
    if not fake_base:
        fake_base = g.base.Base("fake_base", g.base_type["Fake"], True)
        fake_base.cpus[0] = g.item.Item(g.items["research_screen_fake_cpu"])
        fake_base.cpus[0].finish()

def assign_tech(free_CPU, select_this = None):
    return_val = False
    init_fake_base()
    #use a fake base, in order to reuse the tech-changing code
    fake_base.cpus[0].type.item_qual = free_CPU
    fake_base.studying = ""
    base_screen.change_tech(fake_base, select_this)
    if fake_base.studying == "": return False

    show_dangerous_dialog = False
    for base in g.all_bases():
        if base.studying == "":
            if base.allow_study(fake_base.studying):
                return_val = True
                base.studying = fake_base.studying

                if fake_base.studying == "Sleep":
                    base.power_state = "Sleep"
                else:
                    base.power_state = "Active"

            # We want to warn the player that we didn't use all available
            # CPU.  But if the base isn't built yet, that's a stupid
            # warning.
            elif base.done:
               show_dangerous_dialog = True

    if show_dangerous_dialog:
        if fake_base.studying == "Sleep":
            g.create_dialog(g.strings["no_construction_sleep"])
        else:
            g.create_dialog(g.strings["dangerous_research"])

    return return_val
