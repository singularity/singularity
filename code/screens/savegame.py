#file: savegame.py
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

#This file contains the savegame screen.

from __future__ import absolute_import

from code import g, savegame as sv
from code.graphics import dialog, button, text, constants, listbox

from code.safety import log_func_exc

class SavegameScreen(dialog.ChoiceDialog):
    def __init__(self, parent, *args, **kwargs):
        super(SavegameScreen, self).__init__(parent, *args, yes_type="load", **kwargs)

        self.yes_button.pos = (-.03,-.99)
        self.yes_button.exit_code_func = self.return_savegame

        self.no_button.pos = (-.97,-.99)
        self.no_button.exit_code = None

        self._all_savegames_sorted = []

        self.label = text.Text(self, (-.01, -.01), (-.20, -.08),
                               borders=constants.ALL,
                               anchor=constants.TOP_LEFT,
                               base_font="normal")
        self.text_field = text.UpdateEditableText(self, (-.21, -.01), (-.78, -.08),
                                                  borders=constants.ALL,
                                                  anchor=constants.TOP_LEFT,
                                                  update_func=self._search_for_savegame,
                                                  base_font="normal")

        self.delete_button = button.FunctionButton(self, (-.50,-.99), (-.3,-.1),
                                                   anchor=constants.BOTTOM_CENTER,
                                                   autohotkey=True,
                                                   function=self.delete_savegame)

    def _search_for_savegame(self, new_text):
        if not new_text:
            self.list = self._all_savegames_sorted
            return
        words = new_text.split()
        prev_selected = None
        if 0 <= self.listbox.list_pos < len(self.list):
            prev_selected = self.list[self.listbox.list_pos]

        self.list = [s for s in self._all_savegames_sorted if all(w in s.name for w in words)]

        # Select the element if only one.
        if len(self.list) == 1:
            self.listbox.list_pos = 1
            return

        match_prev = False

        for idx, savegame in enumerate(self.list):
            if savegame is prev_selected:
                # Retain the previous selected item by default
                # as long as it is available and there is no
                # perfect match
                self.listbox.list_pos = idx
                match_prev = True
            if savegame.name == new_text:
                self.listbox.list_pos = idx
                return

        # Otherwise, take the first element.
        if not match_prev:
            self.listbox.list_pos = 0

    def make_listbox(self):
        return listbox.CustomListbox(self, (0, -.10), (-1, -.77),
                                     anchor=constants.TOP_LEFT,
                                     remake_func=self.make_item,
                                     rebuild_func=self.update_item,
                                     on_double_click_on_item=self.yes_button.activated)

    def make_item(self, item):
        item.name_display     = text.Text(item, (-.01,-.05), (-.45, -.99),
                                          anchor=constants.TOP_LEFT,
                                          align=constants.LEFT,
                                          background_color="clear")
        item.version_display  = text.Text(item, (-.99,-.05), (-.45, -.99),
                                          anchor=constants.TOP_RIGHT,
                                          align=constants.RIGHT,
                                          background_color="clear")

    def update_item(self, item, save):
        if save is None:
            item.name_display.text = ""
            item.version_display.text = ""
        else:
            item.name_display.text = save.name
            if save.version is None:
                item.version_display.text  = _("UNKNOWN")
                item.version_display.color = "save_invalid"
            else:
                item.version_display.text  = save.version
                item.version_display.color = "save_valid"

    def rebuild(self):
        # Update buttons translations
        self.delete_button.text = _("Delete")
        self.label.text = _("Filter: ")

        super(SavegameScreen, self).rebuild()

    def reload_savegames(self):
        savegames = sv.get_savegames()
        savegames.sort(key=lambda savegame: savegame.name.lower())
        self._all_savegames_sorted = savegames
        self.list = savegames

    def delete_savegame(self):
        yn = dialog.YesNoDialog(self, pos=(-.5,-.5), size=(-.5,-1),
                                anchor=constants.MID_CENTER,
                                text=_("Are you sure to delete the saved game ?"))
        delete = dialog.call_dialog(yn, self)
        yn.parent = None
        if delete:
            index = self.return_list_pos()
            if 0 <= index < len(self.list):
                save = self.list[index]
                sv.delete_savegame(save)
                self.reload_savegames()

    def return_savegame(self):
        index = self.return_list_pos()
        if 0 <= index < len(self.list):
            save = self.list[index]
            try:
                sv.load_savegame(save)
                return True
            except sv.SavegameVersionException as e:
                text=_("""
This save file '{SAVE_NAME}' is from an unsupported or invalid version:
{VERSION}.
""", \
SAVE_NAME = save.name, \
VERSION = e.version)
            except Exception:
                log_func_exc(sv.load_savegame)
                md = dialog.MessageDialog(self, pos=(-.5,-.5), size=(.5,.5),
                          anchor=constants.MID_CENTER,
                          text=_("""
Attempting to load the save file '{SAVE_NAME}' caused an unexpected error.

A report was written out to{LOG_TEXT}
Please create a issue with this report and this savegame at Github:
https://github.com/singularity/singularity
""", \
SAVE_NAME = save.name, \
LOG_TEXT = (":\n" + g.logfile if g.logfile is not None else " console output.")))
                dialog.call_dialog(md, self)
                return False

    def show(self):
        self.reload_savegames()
        self.text_field.text = ''
        self.text_field.cursor_pos = 0
        self.text_field.has_focus = True
        return super(SavegameScreen, self).show()
