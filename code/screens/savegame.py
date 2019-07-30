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


from code import savegame as sv
from code.graphics import dialog, button, text, constants, listbox


class SavegameScreen(dialog.ChoiceDialog):
    def __init__(self, parent, *args, **kwargs):
        super(SavegameScreen, self).__init__(parent, *args, yes_type="load", **kwargs)

        self.yes_button.pos = (-.03,-.99)
        self.yes_button.exit_code_func = self.return_savegame

        self.no_button.pos = (-.97,-.99)
        self.no_button.exit_code = None

        self._all_savegames_by_name = {}
        self._all_savegames_sorted = []
        self._search_enabled = True

        self.label = text.Text(self, (0, 0), (0.1, .04),
                               borders=constants.ALL,
                               anchor=constants.TOP_LEFT,
                               base_font="normal")
        self.text_field = text.UpdateEditableText(self, (0.1, 0), (0.4, .04),
                                                  borders=constants.ALL,
                                                  anchor=constants.TOP_LEFT,
                                                  update_func=self._search_for_savegame,
                                                  base_font="normal")

        self.delete_button = button.FunctionButton(self, (-.50,-.99), (-.3,-.1),
                                                   anchor=constants.BOTTOM_CENTER,
                                                   autohotkey=True,
                                                   function=self.delete_savegame)

    def _on_item_selected(self, event, new_pos, old_pos):
        if 0 <= new_pos < len(self.list):
            savegame = self.list[new_pos]
            try:
                # Disable searching to avoid re-shuffling the
                # list during a double click.
                self._search_enabled = False
                self.text_field.text = savegame.name
                self.text_field.cursor_pos = len(savegame.name)
            finally:
                self._search_enabled = True

    def _search_for_savegame(self, new_text):
        if not self._search_enabled:
            return
        if not new_text:
            self.list = self._all_savegames_sorted
            return
        words = new_text.split()
        self.list = [s for s in self._all_savegames_sorted if all(w in s.name for w in words)]

    def make_listbox(self):
        return listbox.CustomListbox(self, (0, 0.04), (-1, -.81),
                                     anchor=constants.TOP_LEFT,
                                     remake_func=self.make_item,
                                     rebuild_func=self.update_item,
                                     on_double_click_on_item=self.yes_button.activated,
                                     on_item_selected=self._on_item_selected,
                                     )

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
        self.label.text = _("Name: ")

        super(SavegameScreen, self).rebuild()

    def reload_savegames(self):
        savegames = sv.get_savegames()
        savegames.sort(key=lambda savegame: savegame.name.lower())

        self._all_savegames_by_name = {s.name: s for s in savegames}
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
        savegame_name = self.text_field.text
        savegame = self._all_savegames_by_name.get(savegame_name)
        if savegame is not None:
            return sv.load_savegame(savegame)
        return False

    def show(self):
        self.reload_savegames()
        self.text_field.text = ''
        self.text_field.cursor_pos = 0
        self.text_field.has_focus = True
        return super(SavegameScreen, self).show()
