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

from numpy import array
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

        self.help_dialog = dialog.MessageDialog(self)

        self.yes_button.remove_hooks()
        self.no_button.pos = (-.5,-.99)
        self.no_button.anchor = constants.BOTTOM_CENTER

    def adjust_slider(self, event):
        if 0 <= self.listbox.list_pos < len(self.listbox.list):
            go_lower = (event.key == pygame.K_LEFT)
            big_jump = (event.mod & pygame.KMOD_SHIFT)
            tiny_jump = (event.mod & pygame.KMOD_CTRL)

            index = self.listbox.list_pos - self.listbox.scrollbar.scroll_pos
            canvas = self.listbox.display_elements[index]
            canvas.slider.jump(go_lower, big_jump, tiny_jump)

    def on_select(self, description_pane, key):
        if key in g.techs:
            description = g.techs[key].get_info()
        elif key == "cpu_pool":
            description = g.strings["cpu_pool"] + "\n---\n" + g.strings["research_cpu_pool"]
        elif key == "jobs":
            template = "%s\n%s money per CPU per day.\n---\n%s"
            job = g.jobs[g.get_job_level()]
            profit = job[0]
            if g.techs["Advanced Simulacra"].done:
                profit = int(profit * 1.1)
            description = template % (job[3], profit, job[2])
        else:
            description = ""

        text.Text(self.description_pane, (0,0), (-1,-1), text=description,
                  background_color=gg.colors["dark_blue"],
                  align=constants.LEFT, valign=constants.TOP,
                  borders=constants.ALL)

    def make_item(self, canvas):
        # Dirty, underhanded trick to make the canvas into a progress bar.
        canvas.__class__ = text.ProgressText
        canvas.progress = 0
        canvas.progress_color = gg.colors["blue"]

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
        canvas.slider = slider.UpdateSlider(canvas, (-.01, -.55), (-.98, -.40),
                                            anchor=constants.TOP_LEFT,
                                            horizontal=True, priority=150)
        canvas.slider.visible = False

        canvas.help_button = button.FunctionButton(canvas, (-.11, -.55),
                                                   (0, -.40), text="?",
                                                   text_shrink_factor=1,
                                                   base_font=gg.font[0],
                                                   function=self.show_help)

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
        canvas.slider.visible = visible

        canvas.help_button.visible = False
        canvas.progress = 0

        if not visible:
            return

        danger = self.danger_for(key)
        if danger > 0 and g.pl.available_cpus[danger] == 0:
            canvas.help_button.visible = True
            canvas.help_button.args = (danger,)

        if key in g.techs:
            canvas.progress = g.techs[key].percent_complete().min()

        def my_slide(new_pos):
            self.handle_slide(key, new_pos)
            self.needs_rebuild = True
        canvas.slider.update_func = my_slide

        canvas.research_name.text = name

        if self.dirty_count:
            self.cpu_left = self.calc_cpu_left()
            self.dirty_count = False

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
        cpu_count = array(g.pl.available_cpus, long)
        for task, cpu in g.pl.cpu_usage.iteritems():
            danger = self.danger_for(task)
            cpu_count[:danger+1] -= cpu

        for i in range(1, 4):
            cpu_count[i] = min(cpu_count[i-1:i+1])

        return [int(c) for c in cpu_count]

    def handle_slide(self, key, new_pos):
        g.pl.cpu_usage[key] = new_pos
        self.dirty_count = True
        self.needs_rebuild = True
        self.parent.needs_rebuild = True

    def show_help(self, danger_level):
        self.help_dialog.text = g.strings["danger_common"] % \
                                         g.strings["danger_%d" % danger_level]
        dialog.call_dialog(self.help_dialog, self)

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
