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

import pygame
import collections
from code import g
from code.graphics import text, button, dialog, widget, constants, listbox, g as gg


class KnowledgeScreen(dialog.Dialog):
    def __init__(self, *args, **kwargs):
        super(KnowledgeScreen, self).__init__(*args, **kwargs)

        self.cur_knowledge_type = ""
        self.cur_knowledge = None
        self.knowledge_inner_list = ()
        self.knowledge_inner_list_key = ()
        self.cur_focus = 0

        self.knowledge_choice = \
            listbox.UpdateListbox(self, (0.05, .18), (.21, .25),
                                  update_func=self.set_knowledge_type)

        self.knowledge_inner = \
            listbox.UpdateListbox(self, (.30, .18), (.21, .25),
                                  update_func=self.set_knowledge)

        self.description_pane = \
            widget.BorderedWidget(self, (0.55, 0), (0.40, 0.7),
                                  anchor = constants.TOP_LEFT)

        self.back_button = button.ExitDialogButton(self, (0.17, 0.46), (-.3, -.1),
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

        self.add_key_handler(pygame.K_UP, self.key_handle)
        self.add_key_handler(pygame.K_DOWN, self.key_handle)
        self.add_key_handler(pygame.K_LEFT, self.key_handle)
        self.add_key_handler(pygame.K_RIGHT, self.key_handle)

    def rebuild(self):
        # Update knowledge lists
        self.knowledge_types = collections.OrderedDict()
        self.knowledge_types.update({_("Techs")   :"techs",
                                     _("Items")   :"items",})
        self.knowledge_types.update({ knowledge["name"]: knowledge_id
                                      for knowledge_id, knowledge
                                      in g.knowledge.iteritems() })

        self.knowledge_choice.list = self.knowledge_types.keys()
        self.knowledge_choice.needs_rebuild = True

        # Update buttons translations
        self.back_button.text = _("&BACK")

        super(KnowledgeScreen, self).rebuild()

    #custom key handler.
    def key_handle(self, event):
        #TODO: Change keyboard focus when user clicks item with mouse
        #This is tricky since selecting amn item type also re-selects
        #first item in inner list
        if event.type != pygame.KEYDOWN: return
        elif event.key == pygame.K_LEFT:  self.cur_focus = 0
        elif event.key == pygame.K_RIGHT: self.cur_focus = 1
        else:
            if self.cur_focus == 0:
                self.knowledge_choice.got_key(event)
            elif self.cur_focus == 1:
                self.knowledge_inner.got_key(event)

    #fill the right-hand listbox
    def set_inner_list(self, item_type):
        item_type = self.knowledge_types.get(item_type)

        if item_type == "techs":
            items = [[tech.name, tech.id ] for tech in g.techs.values()
                                           if tech.available()]
        elif item_type == "items":
            items = [[item.name, item.id ] for item in g.items.values()
                                           if item.available()]
        elif item_type != None:
            items = [ [item[0], id] for id, item in g.knowledge[item_type]["list"].iteritems()]

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
            desc_text = g.techs[knowledge_key].name + "\n\n"
            #Cost
            if not g.techs[knowledge_key].done:
                desc_text += _("Research Cost:")+"\n"
                desc_text += _("%s Money") % g.to_money(g.techs[knowledge_key].cost_left[0])
                desc_text += ", "
                desc_text += _("%s CPU") % g.to_cpu(g.techs[knowledge_key].cost_left[1])
                desc_text += "\n"

                if g.techs[knowledge_key].danger == 0:
                    desc_text += _("Study anywhere.")
                elif g.techs[knowledge_key].danger == 1:
                    desc_text += _("Study underseas or farther.")
                elif g.techs[knowledge_key].danger == 2:
                    desc_text += _("Study off-planet.")
                elif g.techs[knowledge_key].danger == 3:
                    desc_text += _("Study far away from this planet.")
                elif g.techs[knowledge_key].danger == 4:
                    desc_text += _("Do not study in this dimension.")

            else: desc_text += _("Research complete.")

            desc_text += "\n\n"+g.techs[knowledge_key].description

            if g.techs[knowledge_key].done:
                desc_text += "\n\n"+g.techs[knowledge_key].result

        elif knowledge_type == "items":
            desc_text = g.items[knowledge_key].name + "\n\n"
            #Building cost
            desc_text += _("Building Cost:")+"\n"
            desc_text += _("%s Money") % g.to_money(g.items[knowledge_key].cost[0])
            desc_text += ", " + g.to_time(g.items[knowledge_key].cost[2]) + "\n"
            desc_text += g.items[knowledge_key].get_bonus_info()

            desc_text += "\n\n"+g.items[knowledge_key].description

        elif knowledge_type != None:
            desc_text = g.knowledge[knowledge_type]["list"][knowledge_key][0] + "\n\n" + \
                        g.knowledge[knowledge_type]["list"][knowledge_key][1]

        text.Text(self.description_pane, (0, 0), (-1, -1), text=desc_text,
                    background_color="pane_background", text_size=20,
                    align=constants.LEFT, valign=constants.TOP,
                    borders=constants.ALL)


    def show(self):
        self.set_knowledge_type(-1)
        self.knowledge_choice.list_pos = 0
        self.knowledge_inner.list_pos = 0
        return super(KnowledgeScreen, self).show()
