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

import pygame

from code import g
from code.graphics import widget, dialog, button, slider, text, constants, listbox, g as gg
import finance

class ResearchScreen(dialog.ChoiceDescriptionDialog):
    def __init__(self, parent, pos=(.5, .1), size=(.93, .63), *args, **kwargs):
        self.dirty_count = True
        super(ResearchScreen, self).__init__(parent, pos, size, *args, **kwargs)
        self.listbox.remove_hooks()
        self.listbox = listbox.CustomListbox(self, (0,0), (.53, .55),
                                             list_size=-40,
                                             remake_func=self.make_item,
                                             rebuild_func=self.update_item,
                                             update_func=self.handle_update)
        self.description_pane.size = (.39, .55)

        self.desc_func = self.on_select

        self.add_key_handler(pygame.K_LEFT, self.adjust_slider)
        self.add_key_handler(pygame.K_RIGHT, self.adjust_slider)

    def adjust_slider(self, event):
        if 0 <= self.listbox.list_pos < len(self.listbox.list):
            go_lower = (event.key == pygame.K_LEFT)
            big_jump = (event.mod & pygame.KMOD_SHIFT)
            tiny_jump = (event.mod & pygame.KMOD_CTRL)

            canvas = self.listbox.display_elements[self.listbox.list_pos]
            canvas.slider.jump(go_lower, big_jump, tiny_jump)

    def on_select(self, description_pane, key):
        text.Text(self.description_pane, (0,0), (-1,-1), text=key)

    def make_item(self, canvas):
        canvas.research_name = text.Text(canvas, (-.01, -.01), (-.70, -.5),
                                         align=constants.LEFT,
                                         background_color=gg.colors["clear"])
        canvas.research_name.visible = False
        canvas.alloc_cpus = text.Text(canvas, (-.99, -.01), (-.21, -.5),
                                      anchor=constants.TOP_RIGHT,
                                      text="1,000,000,000",
                                      align=constants.RIGHT,
                                      background_color=gg.colors["clear"])
        canvas.alloc_cpus.visible = False
        #canvas.remove_button = button.Button(canvas, (-.94, -.05), (-.05, -.45),
        #                                   text="X", text_shrink_factor=.9,
        #                                   color=gg.colors["red"])
        #canvas.remove_button.visible = False
        canvas.slider = slider.UpdateSlider(canvas, (-.01, -.55), (-.98, -.40),
                                            anchor=constants.TOP_LEFT,
                                            horizontal=True)
        canvas.slider.visible = False

    def cpu_for(self, key):
        return g.pl.cpu_usage.get(key, 0)

    def danger_for(self, key):
        if key in ["jobs", "cpu_pool"]:
            return 0
        else:
            return g.techs[key].danger

    def update_item(self, canvas, name, key):
        visible = (key is not None)
        canvas.research_name.visible = visible
        canvas.alloc_cpus.visible = visible
        #canvas.remove_button.visible = visible
        canvas.slider.visible = visible

        if not visible:
            return

        def my_slide(new_pos):
            self.handle_slide(key, new_pos)
            self.needs_rebuild = True
        canvas.slider.update_func = my_slide

        canvas.research_name.text = name

        if self.dirty_count:
            self.cpu_left = self.calc_cpu_left()
            self.dirty_count = False

        danger = self.danger_for(key)
        cpu = self.cpu_for(key)
        cpu_left = self.cpu_left[danger]
        total_cpu = cpu + cpu_left
        canvas.slider.slider_pos = cpu
        canvas.slider.slider_max = total_cpu
        canvas.slider.slider_size = ss = g.pl.available_cpus[0] // 10 + 1
        full_size = -.98
        size_fraction = (total_cpu + ss) / float(g.pl.available_cpus[0] + ss)
        canvas.slider.size = (full_size * size_fraction, -.4)
        canvas.alloc_cpus.text = g.add_commas(cpu)

    def calc_cpu_left(self):
        from numpy import array
        cpu_count = array(g.pl.available_cpus)
        for task, cpu in g.pl.cpu_usage.iteritems():
            danger = self.danger_for(task)
            cpu_count[:danger+1] -= cpu

        for i in range(1, 4):
            cpu_count[i] = min(cpu_count[i-1:i+1])

        return cpu_count

    def handle_slide(self, key, new_pos):
        g.pl.cpu_usage[key] = new_pos
        self.dirty_count = True
        self.needs_rebuild = True
        self.parent.needs_rebuild = True

    def show(self):
        techs = [tech for tech in g.techs.values() if tech.available()
                                                      and not tech.done]
        techs.sort()
        self.list = ["CPU Pool", g.get_job_level()] + \
                    ["Research %s" % tech.name for tech in techs]
        self.key_list = ["cpu_pool", "jobs"] + [tech.id for tech in techs]
        self.listbox.key_list = self.key_list

        self.dirty_count = True
        return super(ResearchScreen, self).show()

#cost = (money, ptime, labor)

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
