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

from code import g
from code.graphics import text, button, dialog, widget, constants, listbox, g as gg

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

class LocationScreen(dialog.Dialog):
    def __init__(self, *args, **kwargs):
        super(LocationScreen, self).__init__(*args, **kwargs)
        self.pos = (-.5, -.5)
        self.anchor = constants.MID_CENTER
        self.size = (-.75, -.5)
        self.name_display = text.Text(self, (0,0), (-1, -.08),
                                      background_color=gg.colors["clear"])
        self.listbox = listbox.CustomListbox(self, (0,-.08), (-1, -.70),
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

        self.new_button = \
            button.FunctionButton(self, (0, -.91), (-.3, -.09),
                                  text="NEW BASE", hotkey="n",
                                  function=self.new_base)
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

        self.new_base_dialog = NewBaseDialog(self)
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

            if not base.done:
                canvas.status_display.text = "Building Base"
            elif base.type.force_cpu:
                canvas.status_display.text = ""
            elif base.cpus is None and base.extra_items == [None] * 3:
                canvas.status_display.text = "Empty"
            elif base.cpus is None:
                canvas.status_display.text = "Incomplete"
            elif not base.cpus.done:
                canvas.status_display.text = "Building CPU"
            elif [item for item in base.extra_items if item is not None
                                                       and not item.done]:
                canvas.status_display.text = "Building Item"
            else:
                canvas.status_display.text = "Complete"

    def show(self):
        self.needs_rebuild = True
        return super(LocationScreen, self).show()

    def rebuild(self):
        if self.location is not None:
            self.listbox.list = [base.name for base in self.location.bases]
            self.listbox.key_list = self.location.bases
            self.listbox.needs_rebuild = True
            self.name_display.text = self.location.name
        super(LocationScreen, self).rebuild()

    def power_state(self):
        if 0 <= self.listbox.list_pos < len(self.listbox.key_list):
            base = self.listbox.key_list[self.listbox.list_pos]
            old_index = state_list.index(base.power_state)
            base.power_state = state_list[old_index-1]
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

class NewBaseDialog(dialog.ChoiceDescriptionDialog):
    def __init__(self, parent, pos = (0, 0), size = (-1, -1),
                 anchor = constants.TOP_LEFT, *args, **kwargs):
        kwargs["yes_type"] = "ok"
        kwargs["no_type"] = "back"
        super(NewBaseDialog, self).__init__(parent, pos, size, anchor, *args,
                                            **kwargs)

        self.desc_func = self.on_change

        self.yes_button.function = self.get_name
        self.name_dialog = \
            dialog.TextEntryDialog(self, text=g.strings["new_base_text"])

    def on_change(self, description_pane, base_type):
        base_info = base_type.get_info(self.parent.location)
        text.Text(description_pane, (0, 0), (-1, -1), text=base_info,
                  background_color=gg.colors["dark_blue"],
                  align=constants.LEFT, valign=constants.TOP,
                  borders=constants.ALL)

    def show(self):
        self.list = []
        self.key_list = []

        base_type_list = g.base_type.values()
        base_type_list.sort()
        base_type_list.reverse()
        for base_type in base_type_list:
            if base_type.available():
                self.list.append(base_type.name)
                self.key_list.append(base_type)

        return super(NewBaseDialog, self).show()

    def get_name(self):
        if 0 <= self.listbox.list_pos < len(self.key_list):
            type = self.key_list[self.listbox.list_pos]
            self.name_dialog.default_text = \
                generate_base_name(self.parent.location, type)
            name = dialog.call_dialog(self.name_dialog, self)
            if name:
                raise constants.ExitDialog((name, type))

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
