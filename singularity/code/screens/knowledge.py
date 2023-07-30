# file: knowledge.py
# Copyright (C) 2005,2006,2008 Evil Mr Henry, Phil Bordelon, and FunnyMan3595
# This file is part of Endgame: Singularity.

# Endgame: Singularity is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# Endgame: Singularity is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Endgame: Singularity; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

# This file is used to display the knowledge lists.

from __future__ import absolute_import

import collections

from singularity.code import i18n, g
from singularity.code.graphics import text, button, dialog, widget, constants, listbox


class KnowledgeScreen(dialog.FocusDialog):
    def __init__(self, *args, **kwargs):
        super(KnowledgeScreen, self).__init__(*args, **kwargs)

        self.knowledge_types = collections.OrderedDict()
        self.knowledge_type_index = collections.defaultdict(int)
        self.cur_knowledge_type = ""
        self.cur_knowledge = None
        self.knowledge_inner_list = ()
        self.knowledge_inner_list_key = ()

        self.knowledge_choice_title = button.HotkeyText(
            self,
            (0.08, 0.04),
            (0.42, 0.05),
            autotranslate=True,
            text=N_("&Sections:"),
            align=constants.LEFT,
            background_color="clear",
        )
        self.knowledge_choice = listbox.UpdateListbox(
            self, (0.08, 0.09), (0.42, 0.22), update_func=self.set_knowledge_type
        )
        self.knowledge_choice_title.hotkey_func = lambda e: self.took_focus(
            self.knowledge_choice
        )

        self.knowledge_inner_title = button.HotkeyText(
            self,
            (0.08, 0.35),
            (0.42, 0.05),
            autotranslate=True,
            text=N_("&Entries:"),
            align=constants.LEFT,
            background_color="clear",
        )
        self.knowledge_inner = listbox.UpdateListbox(
            self, (0.08, 0.40), (0.42, 0.22), update_func=self.set_knowledge
        )
        self.knowledge_inner_title.hotkey_func = lambda e: self.took_focus(
            self.knowledge_inner
        )

        self.description_pane = widget.BorderedWidget(
            self, (0.54, 0.04), (0.38, 0.70), anchor=constants.TOP_LEFT
        )

        self.back_button = button.ExitDialogButton(
            self,
            (0.18, 0.68),
            (0.22, 0.06),
            autotranslate=True,
            text=N_("&BACK"),
            anchor=constants.TOP_LEFT,
            autohotkey=True,
        )

        self.took_focus(self.knowledge_choice)

    def rebuild(self):
        # Update knowledge lists
        self.knowledge_types = collections.OrderedDict()
        self.knowledge_types.update(
            [(_("Techs"), "techs"), (_("Bases"), "bases"), (_("Items"), "items")]
        )
        self.knowledge_types.update(
            (knowledge.name, knowledge_id)
            for knowledge_id, knowledge in g.knowledge.items()
        )

        self.knowledge_choice.list = list(self.knowledge_types)
        self.knowledge_choice.needs_rebuild = True

        super(KnowledgeScreen, self).rebuild()

    # fill the right-hand listbox
    def set_inner_list(self, item_type):
        item_type = self.knowledge_types.get(item_type)

        if item_type == "techs":
            items = [
                [tech.name, tech.id] for tech in g.pl.techs.values() if tech.available()
            ]
        elif item_type == "bases":
            items = [
                [base.name, base.id]
                for base in g.base_type.values()
                if base.available()
            ]
        elif item_type == "items":
            items = [
                [item.name, item.id] for item in g.items.values() if item.available()
            ]
        elif item_type is not None:
            items = [
                [item.name, id]
                for id, item in g.knowledge[item_type].help_entries.items()
            ]

        else:
            items = []

        items.sort(key=lambda item: i18n.lex_sorting_form(item[0]))

        return_list1 = []
        return_list2 = []
        for name, id in items:
            return_list1.append(id)
            return_list2.append(name)
        return return_list1, return_list2

    # Make sure the left listbox is correct after moving around.
    def set_knowledge_type(self, list_pos):
        if getattr(self, "knowledge_choice", None) is None:
            return  # Not yet initialized.
        prev_know = self.cur_knowledge_type
        if list_pos == -1:
            prev_know = ""
            list_pos = 0
        if 0 <= list_pos < len(self.knowledge_choice.list):
            self.cur_knowledge_type = self.knowledge_choice.list[list_pos]
        if prev_know != self.cur_knowledge_type:
            self.knowledge_type_index[prev_know] = self.knowledge_inner.list_pos
            index = self.knowledge_type_index[self.cur_knowledge_type]
            (
                self.knowledge_inner_list_key,
                self.knowledge_inner.list,
            ) = self.set_inner_list(self.cur_knowledge_type)
            self.knowledge_inner.list_pos = index
            self.set_knowledge(0)

    # Make sure the right-hand listbox is correct.
    def set_knowledge(self, list_pos):
        if getattr(self, "knowledge_inner", None) is None:
            return  # Not yet initialized.
        prev_know = self.cur_knowledge
        if 0 <= list_pos < len(self.knowledge_inner.list):
            self.cur_knowledge = self.knowledge_inner.list[list_pos]
        if prev_know != self.cur_knowledge:
            self.show_info(
                self.cur_knowledge_type, self.knowledge_inner_list_key[list_pos]
            )

    # print information to the right.
    def show_info(self, knowledge_type, knowledge_key):
        knowledge_type = self.knowledge_types.get(knowledge_type)
        desc_text = ""

        if knowledge_type == "techs":
            desc_text = g.pl.techs[knowledge_key].name + "\n\n"

            # Cost
            desc_text += _("Research Cost:") + "\n"
            desc_text += self._desc_cost(
                g.pl.techs[knowledge_key].total_cost
            )  # Research cost
            desc_text += "\n"

            danger_level = g.pl.techs[knowledge_key].danger
            desc_text += g.dangers[danger_level].knowledge_desc

            if g.pl.techs[knowledge_key].done:
                desc_text += " " + _("Research complete.")

            desc_text += "\n\n" + g.techs[knowledge_key].description

            if g.pl.techs[knowledge_key].done:
                desc_text += "\n\n" + g.techs[knowledge_key].result

        elif knowledge_type == "bases":
            base = g.base_type[knowledge_key]

            desc_text = base.name + "\n\n"
            desc_text += _("Building Cost:") + "\n"
            desc_text += self._desc_cost(base.cost)  # Building cost
            desc_text += "\n"
            desc_text += _("Maintenance Cost:") + "\n"
            desc_text += self._desc_maint(base.maintenance)  # Maintenance cost
            desc_text += "\n"
            if base.size > 1:
                desc_text += _("Size: %d") % base.size + "\n"

            desc_text += base.get_detect_info()

            desc_text += "\n" + base.description

        elif knowledge_type == "items":
            item = g.items[knowledge_key]

            desc_text = item.name + "\n\n"
            desc_text += _("Building Cost:") + "\n"
            desc_text += self._desc_cost(item.cost)  # Building cost
            desc_text += "\n"
            desc_text += g.items[knowledge_key].get_quality_info()
            desc_text += "\n" + item.description

        elif knowledge_type is not None:
            help_entry = g.knowledge[knowledge_type].help_entries[knowledge_key]
            desc_text = help_entry.name + "\n\n" + help_entry.description

        text.Text(
            self.description_pane,
            (0, 0),
            (-1, -1),
            text=desc_text,
            background_color="pane_background",
            text_size=20,
            align=constants.LEFT,
            valign=constants.TOP,
            borders=constants.ALL,
        )

    def _desc_maint(self, maintenance):
        maint = maintenance[:]
        # describe_cost() expects CPU-seconds, not CPU-days
        maint[1] *= g.seconds_per_day
        return self._desc_cost(maint)

    def _desc_cost(self, cost):
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
