#file: knowledge.py
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

#This file is used to display the knowledge lists.

from __future__ import absolute_import

import pygame
import collections

from singularity.code import g
from singularity.code.graphics import text, button, dialog, widget, constants, listbox


class KnowledgeScreen(dialog.Dialog):
    def __init__(self, *args, **kwargs):
        super(KnowledgeScreen, self).__init__(*args, **kwargs)

        self.cur_knowledge_type = ""
        self.cur_knowledge = None
        self.knowledge_inner_list = ()
        self.knowledge_inner_list_key = ()
        self.cur_focus = 0

        self.knowledge_choice = \
            listbox.UpdateListbox(self, (0.05, .18), (.15, .25),
                                  update_func=self.set_knowledge_type)

        # Tech names are typically a lot longer than knowledge concepts.
        # Therefore, we make knowledge_inner a lot wider than
        # knowledge_choice.
        self.knowledge_inner = \
            listbox.UpdateListbox(self, (.24, .18), (.27, .25),
                                  update_func=self.set_knowledge)

        self.description_pane = \
            widget.BorderedWidget(self, (0.55, 0), (0.40, 0.7),
                                  anchor = constants.TOP_LEFT)

        self.back_button = button.ExitDialogButton(self, (0.17, 0.46), (-.3, -.1),
                                                   autotranslate=True,
                                                   text=N_("&BACK"),
                                                   anchor=constants.TOP_LEFT,
                                                   autohotkey=True)

        #Set up the key handling.
        #This is likely not the best way to do it.

        self.remove_key_handler(pygame.K_UP, self.knowledge_choice.got_key)
        self.remove_key_handler(pygame.K_DOWN, self.knowledge_choice.got_key)
        self.remove_key_handler(pygame.K_PAGEUP, self.knowledge_choice.got_key)
        self.remove_key_handler(pygame.K_PAGEDOWN, self.knowledge_choice.got_key)

        self.remove_key_handler(pygame.K_UP, self.knowledge_inner.got_key)
        self.remove_key_handler(pygame.K_DOWN, self.knowledge_inner.got_key)
        self.remove_key_handler(pygame.K_PAGEUP, self.knowledge_inner.got_key)
        self.remove_key_handler(pygame.K_PAGEDOWN, self.knowledge_inner.got_key)

        self.add_key_handler(pygame.K_UP, self.key_handle, only_on_event_type=pygame.KEYDOWN)
        self.add_key_handler(pygame.K_DOWN, self.key_handle, only_on_event_type=pygame.KEYDOWN)
        self.add_key_handler(pygame.K_LEFT, self.key_handle, only_on_event_type=pygame.KEYDOWN)
        self.add_key_handler(pygame.K_RIGHT, self.key_handle, only_on_event_type=pygame.KEYDOWN)

    def rebuild(self):
        # Update knowledge lists
        self.knowledge_types = collections.OrderedDict()
        self.knowledge_types.update([(_("Techs"), "techs"),
                                     (_("Bases"), "bases"),
                                     (_("Items"), "items")])
        self.knowledge_types.update(
            (knowledge.name, knowledge_id)
            for knowledge_id, knowledge in g.knowledge.items()
        )

        self.knowledge_choice.list = list(self.knowledge_types)
        self.knowledge_choice.needs_rebuild = True

        super(KnowledgeScreen, self).rebuild()

    #custom key handler.
    def key_handle(self, event):
        #TODO: Change keyboard focus when user clicks item with mouse
        #This is tricky since selecting amn item type also re-selects
        #first item in inner list
        if event.key == pygame.K_LEFT:
            self.cur_focus = 0
        elif event.key == pygame.K_RIGHT:
            self.cur_focus = 1
        else:
            if self.cur_focus == 0:
                self.knowledge_choice.got_key(event)
            elif self.cur_focus == 1:
                self.knowledge_inner.got_key(event)

    #fill the right-hand listbox
    def set_inner_list(self, item_type):
        item_type = self.knowledge_types.get(item_type)

        if item_type == "techs":
            items = [[tech.name, tech.id ] for tech in g.pl.techs.values()
                                           if tech.available()]
        elif item_type == "bases":
            items = [[base.name, base.id ] for base in g.base_type.values()
                                           if base.available()]
        elif item_type == "items":
            items = [[item.name, item.id ] for item in g.items.values()
                                           if item.available()]
        elif item_type is not None:
            items = [
                [item.name, id]
                for id, item in g.knowledge[item_type].help_entries.items()
            ]

        else:
            items = []

        items.sort()

        return_list1 = []
        return_list2 = []
        for name, id in items:
            return_list1.append(id)
            return_list2.append(name)
        return return_list1, return_list2

    #Make sure the left listbox is correct after moving around.
    def set_knowledge_type(self, list_pos):
        self.cur_focus = 0
        if getattr(self, "knowledge_choice", None) is None:
            return # Not yet initialized.
        prev_know = self.cur_knowledge_type
        if list_pos == -1:
            prev_know = ""
            list_pos = 0
        if 0 <= list_pos < len(self.knowledge_choice.list):
            self.cur_knowledge_type = self.knowledge_choice.list[list_pos]
        if prev_know != self.cur_knowledge_type:
            self.knowledge_inner_list_key, self.knowledge_inner.list = \
                        self.set_inner_list(self.cur_knowledge_type)
            self.knowledge_inner.list_pos = 0
            self.set_knowledge(0, set_focus=False)

    #Make sure the right-hand listbox is correct.
    def set_knowledge(self, list_pos, set_focus=True):
        if set_focus: self.cur_focus = 1
        if getattr(self, "knowledge_inner", None) is None:
            return # Not yet initialized.
        prev_know = self.cur_knowledge
        if 0 <= list_pos < len(self.knowledge_inner.list):
            self.cur_knowledge = self.knowledge_inner.list[list_pos]
        if prev_know != self.cur_knowledge:
            self.show_info(self.cur_knowledge_type,
                    self.knowledge_inner_list_key[list_pos])

    #print information to the right.
    def show_info(self, knowledge_type, knowledge_key):
        knowledge_type = self.knowledge_types.get(knowledge_type)
        desc_text = ""

        if knowledge_type == "techs":
            desc_text = g.pl.techs[knowledge_key].name + "\n\n"

            # Cost
            desc_text += _("Research Cost:")+"\n"
            desc_text += self._desc_cost(g.pl.techs[knowledge_key].total_cost)  # Research cost
            desc_text += "\n"

            danger_level = g.pl.techs[knowledge_key].danger
            desc_text += g.dangers[danger_level].knowledge_desc

            if g.pl.techs[knowledge_key].done:
                desc_text += " " + _("Research complete.")

            desc_text += "\n\n"+g.techs[knowledge_key].description

            if g.pl.techs[knowledge_key].done:
                desc_text += "\n\n"+g.techs[knowledge_key].result

        elif knowledge_type == "bases":
            base = g.base_type[knowledge_key]
            
            desc_text = base.name + "\n\n"
            desc_text += _("Building Cost:")+"\n"
            desc_text += self._desc_cost(base.cost) #Building cost
            desc_text += "\n"
            desc_text += _("Maintenance Cost:")+"\n"
            desc_text += self._desc_cost(base.maintenance) #Maintenance cost
            desc_text += "\n"
            if base.size > 1:
                desc_text +=  _("Size: %d") % base.size + "\n"

            desc_text += base.get_detect_info()

            desc_text += "\n" + base.description

        elif knowledge_type == "items":
            item = g.items[knowledge_key]
            
            desc_text = item.name + "\n\n"
            desc_text += _("Building Cost:")+"\n"
            desc_text += self._desc_cost(item.cost)  # Building cost
            desc_text += "\n"
            desc_text += g.items[knowledge_key].get_quality_info()
            desc_text += "\n" + item.description

        elif knowledge_type is not None:
            help_entry = g.knowledge[knowledge_type].help_entries[knowledge_key]
            desc_text = help_entry.name + "\n\n" + help_entry.description

        text.Text(self.description_pane, (0, 0), (-1, -1), text=desc_text,
                    background_color="pane_background", text_size=20,
                    align=constants.LEFT, valign=constants.TOP,
                    borders=constants.ALL)

    @staticmethod
    def _desc_cost(cost):
        desc_text = _("%s Money") % g.to_money(cost[0])
        if cost[1] > 0:
            desc_text += ", "
            desc_text += _("%s CPU") % g.to_cpu(cost[1])
        if cost[2] > 0: 
            desc_text += ", "
            desc_text += g.to_time(cost[2])
        
        return desc_text

    def show(self):
        self.set_knowledge_type(-1)
        self.knowledge_choice.list_pos = 0
        self.knowledge_inner.list_pos = 0
        return super(KnowledgeScreen, self).show()
