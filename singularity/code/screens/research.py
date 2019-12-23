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

from __future__ import absolute_import

from numpy import array, int64
import pygame

from singularity.code import g, task
from singularity.code.graphics import dialog, button, slider, text, constants, listbox


class ResearchScreen(dialog.ChoiceDescriptionDialog):
    def __init__(self, parent, pos=(.5, .1), size=(.93, .63), *args, **kwargs):
        self.dirty_count = True
        super(ResearchScreen, self).__init__(parent, pos, size, *args, **kwargs)
        self.listbox.parent = None
        self.listbox = listbox.CustomListbox(self, (0,0), (.53, .55),
                                             list_item_height=0.06,
                                             remake_func=self.make_item,
                                             rebuild_func=self.update_item,
                                             update_func=self.handle_update)
        self.description_pane.size = (.39, .55)

        self.desc_func = self.on_select

        self.help_dialog = dialog.MessageDialog(self)

        self.yes_button.parent = None
        self.no_button.pos = (-.5,-.99)
        self.no_button.anchor = constants.BOTTOM_CENTER

        self.add_handler(constants.KEY, self._got_key, priority=5)

    def _got_key(self, event):
        if event.type != pygame.KEYDOWN:
            return
        # If a valid slider is selected, we let it move first.
        if 0 <= self.listbox.list_pos < len(self.listbox.list):
            index = self.listbox.list_pos - self.listbox.scrollbar.scroll_pos
            canvas = self.listbox.display_elements[index]
            # Raises Handled for us if the key was relevant to the slider
            canvas.slider.handle_key(event)

        # Let the list box get the rest of the keys if it wants them
        self.listbox.got_key(event, require_focus=False)

    def on_select(self, description_pane, key):
        if key in g.pl.techs:
            description = g.pl.techs[key].get_info()
        elif key == "cpu_pool":
            template = "%s\n---\n%s"
            cpu_pool = task.get_current("cpu_pool")
            description = template % (cpu_pool.name, cpu_pool.description)
        elif key == "jobs":
            template = "%s\n" + _("%s money per CPU per day.") + "\n---\n%s"
            job = task.get_current("jobs")
            profit = job.get_profit()
            description = template % (job.name, profit, job.description)
        else:
            description = ""

        text.Text(self.description_pane, (0,0), (-1,-1), text=description,
                  background_color="pane_background", text_size=18,
                  align=constants.LEFT, valign=constants.TOP,
                  borders=constants.ALL)

    def make_item(self, canvas):
        # Dirty, underhanded trick to make the canvas into a progress bar.
        canvas.__class__ = text.ProgressText
        canvas.progress = 0
        canvas.progress_color = "progress_background_progress"

        canvas.research_name = text.Text(canvas, (-.01, -.01), (-.70, -.5),
                                         align=constants.LEFT,
                                         background_color="clear")
        canvas.research_name.visible = False
        canvas.alloc_cpus = text.Text(canvas, (-.99, -.01), (-.21, -.5),
                                      anchor=constants.TOP_RIGHT,
                                      text="1,000,000,000",
                                      align=constants.RIGHT,
                                      background_color="clear")
        canvas.alloc_cpus.visible = False
        canvas.slider = slider.UpdateSlider(canvas, (-.01, -.55), (-.98, -.40),
                                            anchor=constants.TOP_LEFT,
                                            horizontal=True, priority=150)
        canvas.slider.visible = False

        canvas.help_button = button.FunctionButton(canvas, (-.11, -.55),
                                                   (0, -.40), text=" ??? ",
                                                   text_shrink_factor=1,
                                                   base_font="normal",
                                                   function=self.show_help)

    def cpu_for(self, key):
        return g.pl.get_allocated_cpu_for(key, 0)

    def update_item(self, canvas, name, key):
        visible = (key is not None)
        canvas.research_name.visible = visible
        canvas.alloc_cpus.visible = visible
        canvas.slider.visible = visible

        canvas.help_button.visible = False
        canvas.progress = 0

        if not visible:
            return

        danger = task.danger_for(key)
        if danger > 0 and g.pl.available_cpus[danger] == 0:
            canvas.help_button.visible = True
            canvas.help_button.args = (danger,)

        if key in g.pl.techs:
            canvas.progress = g.pl.techs[key].percent_complete().min()

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
        cpu_count = array(g.pl.available_cpus, int64)
        for task_id, cpu in g.pl.get_cpu_allocations():
            danger = task.danger_for(task_id)
            cpu_count[:danger+1] -= cpu

        for i in range(1, 4):
            cpu_count[i] = min(cpu_count[i-1:i+1])

        return [int(c) for c in cpu_count]

    def handle_slide(self, key, new_pos):
        g.pl.set_allocated_cpu_for(key, new_pos)
        self.dirty_count = True
        self.needs_rebuild = True
        self.parent.needs_rebuild = True

    def show_help(self, danger_level):
        self.help_dialog.text = _("This technology is too dangerous to research on any of the computers I have. {TEXT}",
                                  TEXT=g.dangers[danger_level].research_desc)
        dialog.call_dialog(self.help_dialog, self)

    def show(self):
        techs = [tech for tech in g.pl.techs.values() if tech.available()
                                                      and not tech.done]
        techs.sort()
        self.list = [_("CPU Pool"), task.get_current("jobs").name] + \
                    [_("Research %s") % tech.name for tech in techs]
        self.key_list = ["cpu_pool", "jobs"] + [tech.id for tech in techs]
        self.listbox.key_list = self.key_list

        self.dirty_count = True
        return super(ResearchScreen, self).show()
