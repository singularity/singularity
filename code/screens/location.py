#file: location.py
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

#This file is used to display the base list at a given location

import random

from code import g, base
from code.graphics import text, button, dialog, constants, listbox, g as gg

import base as basescreen

state_colors = basescreen.state_colors
state_list = base.power_states[:2]
state_list.reverse()

class LocationScreen(dialog.Dialog):
    def __init__(self, *args, **kwargs):
        super(LocationScreen, self).__init__(*args, **kwargs)
        self.pos = (-.5, -.5)
        self.anchor = constants.MID_CENTER
        self.size = (-.75, -.5)
        self.name_display = text.Text(self, (0,0), (-1, -.08),
                                      background_color="clear")
        self.listbox = listbox.CustomListbox(self, (0,-.08), (-1, -.70),
                                             remake_func=self.make_item,
                                             rebuild_func=self.update_item)

        self.open_button = \
            button.FunctionButton(self, (0, -.8), (-.3, -.09),
                                  anchor=constants.TOP_LEFT,
                                  autohotkey=True,
                                  function=self.open_base)

        self.rename_button = \
            button.FunctionButton(self, (-.50, -.8), (-.3, -.09),
                                  anchor=constants.TOP_CENTER,
                                  autohotkey=True,
                                  function=self.rename_base)

        self.power_button = \
            button.FunctionButton(self, (-1, -.8), (-.3, -.09),
                                  anchor=constants.TOP_RIGHT,
                                  autohotkey=True,
                                  function=self.power_state)

        self.new_button = \
            button.FunctionButton(self, (0, -.91), (-.3, -.09),
                                  autohotkey=True,
                                  function=self.new_base)
        self.destroy_button = \
            button.FunctionButton(self, (-.50, -.91), (-.3, -.09),
                                  anchor=constants.TOP_CENTER,
                                  autohotkey=True,
                                  function=self.destroy_base)
        self.back_button = button.ExitDialogButton(self, (-1, -.9), (-.3, -.09),
                                                   anchor=constants.TOP_RIGHT,
                                                   autohotkey=True)

        self.confirm_destroy = \
            dialog.YesNoDialog(self, (-.5,0), (-.35, -.7),
                            text=_("Are you sure you want to destroy this base?"),
                            shrink_factor=.5)

        self.new_base_dialog = NewBaseDialog(self)
        self.location = None

        self.name_dialog = \
            dialog.TextEntryDialog(self, text=g.strings["name_base_text"])

        self.base_dialog = basescreen.BaseScreen(self, (0,0),
                                                 anchor=constants.TOP_LEFT)

    def make_item(self, canvas):
        canvas.name_display   = text.Text(canvas, (-.01,-.05), (-.45, -.99),
                                          align=constants.LEFT,
                                          background_color="clear")
        canvas.status_display = text.Text(canvas, (-.46,-.05), (-.44, -.99),
                                          align=constants.LEFT,
                                          background_color="clear")
        canvas.power_display  = text.Text(canvas, (-.90,-.05), (-.10, -.99),
                                          background_color="clear")


    def update_item(self, canvas, name, base):
        if base is None:
            elements = [canvas.name_display, canvas.status_display,
                        canvas.power_display]
            for element in elements:
                element.text = ""
        else:
            canvas.name_display.text = name
            canvas.power_display.text = base.power_state_name
            canvas.power_display.color = state_colors[base.power_state]

            if not base.done:
                canvas.status_display.text = \
                    "%s: % 2s%%. %s" % (
                    _("Building Base"),
                    int(base.percent_complete() * 100),
                    _("Completion in %s.") % g.to_time(base.cost_left[2]),)

            elif base.type.force_cpu:
                canvas.status_display.text = ""
            elif base.is_empty():
                canvas.status_display.text = _("Empty")
            elif base.cpus is None:
                canvas.status_display.text = _("Incomplete")
            elif not base.cpus.done:
                canvas.status_display.text = \
                    "%s: % 2s%%. %s" % (
                    _("Building CPU"),
                    int(base.cpus.percent_complete() * 100),
                    _("Completion in %s.") % g.to_time(base.cpus.cost_left[2]),)
            elif base.is_building_extra():
                canvas.status_display.text = _("Building Item")
            else:
                canvas.status_display.text = _("Complete")

    def show(self):
        self.needs_rebuild = True
        return super(LocationScreen, self).show()

    def rebuild(self):
        # Update base location
        if self.location is not None:
            self.location.bases.sort()

            self.listbox.list = [base.name for base in self.location.bases]
            self.listbox.key_list = self.location.bases

            self.name_display.text = self.location.name

            self.listbox.needs_rebuild = True

        # Rebuild dialogs
        self.confirm_destroy.needs_rebuild = True
        self.name_dialog.needs_rebuild = True
        self.base_dialog.needs_rebuild = True

        # Update buttons translations
        self.open_button.text = _("&OPEN BASE")
        self.rename_button.text = _("&RENAME BASE")
        self.power_button.text = _("&POWER STATE")
        self.new_button.text = _("&NEW BASE")
        self.destroy_button.text = _("&DESTROY BASE")
        self.back_button.text = _("&BACK")

        super(LocationScreen, self).rebuild()

    def power_state(self):
        if 0 <= self.listbox.list_pos < len(self.listbox.key_list):
            base = self.listbox.key_list[self.listbox.list_pos]
            old_index = state_list.index(base.power_state)
            base.power_state = state_list[old_index-1]
            base.check_power()
            self.needs_rebuild = True
            self.parent.needs_rebuild = True

    def destroy_base(self):
        if 0 <= self.listbox.list_pos < len(self.listbox.key_list):
            if dialog.call_dialog(self.confirm_destroy, self):
                base = self.listbox.key_list[self.listbox.list_pos]
                base.destroy()
                self.listbox.list = [base.name for base in self.location.bases]
                self.listbox.key_list = self.location.bases
                self.needs_rebuild = True
                self.parent.needs_rebuild = True

    def open_base(self):
        if 0 <= self.listbox.list_pos < len(self.listbox.key_list):
            base = self.listbox.key_list[self.listbox.list_pos]
            if not base.done:
                return
            self.base_dialog.base = base
            dialog.call_dialog(self.base_dialog, self)
            self.needs_rebuild = True
            self.parent.needs_rebuild = True

    def new_base(self):
        result = dialog.call_dialog(self.new_base_dialog, self)
        if result:
            base_type, base_name = result
            new_base = g.base.Base(base_type, base_name)
            self.location.add_base(new_base)
            self.needs_rebuild = True
            self.parent.needs_rebuild = True

    def rename_base(self):
        if 0 <= self.listbox.list_pos < len(self.listbox.key_list):
            base = self.listbox.key_list[self.listbox.list_pos]
            self.name_dialog.default_text = base.name
            name = dialog.call_dialog(self.name_dialog, self)
            if name:
                base.name = name
                self.needs_rebuild = True

class NewBaseDialog(dialog.ChoiceDescriptionDialog):
    def __init__(self, parent, pos=(0, 0), size = (-1, -1),
                 anchor=constants.TOP_LEFT, *args, **kwargs):
        kwargs["yes_type"] = "ok"
        kwargs["no_type"] = "back"
        super(NewBaseDialog, self).__init__(parent, pos, size, anchor, *args,
                                            **kwargs)
        self.listbox.size = (-.53, -.75)
        self.description_pane.size = (-.45, -.75)

        self.text_label = text.Text(self, (.01, -.87), (-.25, -.1),
                                          anchor=constants.BOTTOM_LEFT,
                                          borders=(constants.TOP, constants.BOTTOM, constants.LEFT),
                                          shrink_factor=.88,
                                          background_color="pane_background",
                                          text=g.strings["name_base_text"])

        self.text_field = text.EditableText(self, (-.26, -.87), (-.73, -.1),
                                            anchor=constants.BOTTOM_LEFT,
                                            borders=constants.ALL,
                                            base_font="normal")

        self.desc_func = self.on_change

        self.yes_button.function = self.finish

    def on_change(self, description_pane, base_type):
        if base_type is not None:
            base_info = base_type.get_info(self.parent.location)
            text.Text(description_pane, (0, 0), (-1, -1), text=base_info,
                      background_color="pane_background",
                      align=constants.LEFT, valign=constants.TOP,
                      borders=constants.ALL)

            name = generate_base_name(self.parent.location, base_type)
            self.text_field.text = name
            self.text_field.cursor_pos = len(name)

    def show(self):
        self.list = []
        self.key_list = []

        base_type_list = g.base_type.values()
        base_type_list.sort()
        base_type_list.reverse()
        for base_type in base_type_list:
            if base_type.available() \
                    and base_type.buildable_in(self.parent.location):
                self.list.append(base_type.name)
                self.key_list.append(base_type)

        return super(NewBaseDialog, self).show()

    def finish(self):
        if 0 <= self.listbox.list_pos < len(self.key_list):
            type = self.key_list[self.listbox.list_pos]
            name = self.text_field.text
            if not name:
                name = generate_base_name(self.parent.location, type)

            raise constants.ExitDialog((name, type))

## Generates a name for a base, given a particular location.
def generate_base_name(location, base_type):

    attempts = 0
    name = None
    base_names = [name]+[base.name for base in location.bases]
    while name in base_names:

        # First, decide whether we're going to try significant values or just
        # choose one randomly.
        if random.random() < 0.3: # 30% chance.
            number = random.choice(g.significant_numbers)
        else:
            number = str(random.randint(0, 32767))

        city   = random.choice(location.cities) if location.cities else None
        flavor = random.choice(base_type.flavor) if base_type.flavor else base_type.name

        if city:
            #Translators: Format string for the name of a new base
            #Example: "${NUMBER} ${BASETYPE} in ${CITY}"
            name = _("{CITY} {BASETYPE} {NUMBER}",
                     CITY=city, BASETYPE=flavor, NUMBER=number)
        else:
            #Translators: Name of a new base when location has no cities
            name = _("{BASETYPE} {NUMBER}",
                     NUMBER=number, BASETYPE=flavor)

        # Damn translators omitting the ${NUMBER} in template string!
        if attempts > 100: name = city + " " + flavor + " " + number
        attempts += 1

    return name
