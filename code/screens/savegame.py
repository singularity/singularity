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

import pygame

from code import g, savegame as sv
from code.graphics import dialog, button, slider, text, constants, listbox, g as gg

class SavegameScreen(dialog.ChoiceDialog):
    def __init__(self, parent, *args, **kwargs):
        super(SavegameScreen, self).__init__(parent, *args, yes_type="load", **kwargs)

        self.yes_button.pos = (-.03,-.99)
        self.yes_button.exit_code_func = self.return_savegame

        self.no_button.pos = (-.97,-.99)
        self.no_button.exit_code = None

        self.delete_button = button.FunctionButton(self, (-.50,-.99), (-.3,-.1),
                                                   anchor=constants.BOTTOM_CENTER,
                                                   autohotkey=True,
                                                   function=self.delete_savegame)

    def make_listbox(self):
        return listbox.CustomListbox(self, (0, 0), (-1, -.85),
                                     anchor=constants.TOP_LEFT,
                                     remake_func=self.make_item,
                                     rebuild_func=self.update_item)

    def make_item(self, item):
        item.name_display     = text.Text(item, (-.01,-.05), (-.45, -.99),
                                          anchor=constants.TOP_LEFT,
                                          align=constants.LEFT,
                                          background_color=gg.colors["clear"])
        item.version_display  = text.Text(item, (-.99,-.05), (-.45, -.99),
                                          anchor=constants.TOP_RIGHT,
                                          align=constants.RIGHT,
                                          background_color=gg.colors["clear"])

    def update_item(self, item, name, save):
        if save is None:
            item.name_display.text = ""
            item.version_display.text = ""
        else:
            item.name_display.text = save.name
            if save.version is None:
                item.version_display.text  = _("UNKNOWN")
                item.version_display.color = gg.colors["save_invalid"]
            else:
                item.version_display.text  = save.version
                item.version_display.color = gg.colors["save_valid"]

    def rebuild(self):
        # Update buttons translations
        self.delete_button.text = _("Delete")

        super(SavegameScreen, self).rebuild()

    def reload_savegames(self):
        savegames = sv.get_savegames()
        savegames.sort(key=lambda savegame: savegame.name.lower())

        self.listbox.key_list = savegames
        self.list = [save.name for save in savegames]

    def delete_savegame(self):
        yn = dialog.YesNoDialog(self, pos=(-.5,-.5), size=(-.5,-1),
                                anchor=constants.MID_CENTER,
                                text=_("Are you sure to delete the saved game ?"))
        delete = dialog.call_dialog(yn, self)
        yn.remove_hooks()
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
            return sv.load_savegame(save)
        return False

    def show(self):
        self.reload_savegames()

        return super(SavegameScreen, self).show()
