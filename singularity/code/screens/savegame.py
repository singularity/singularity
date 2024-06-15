# file: savegame.py
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

# This file contains the savegame screen.

from __future__ import absolute_import

import operator
import time

import pygame

from singularity.code import g, savegame as sv, difficulty
from singularity.code.graphics import dialog, button, text, constants, listbox

from singularity.code.safety import log_func_exc


class SavegameScreen(dialog.ChoiceDialog):
    def __init__(self, parent, *args, **kwargs):
        super(SavegameScreen, self).__init__(
            parent, *args, yes_type=N_("&LOAD"), **kwargs
        )

        self.yes_button.pos = (-0.03, -0.99)
        self.yes_button.size = (-0.22, -0.1)
        self.yes_button.function = self.exit_savegame
        self.yes_button.force_underline = -1  # Work around #224

        self.no_button.pos = (-0.97, -0.99)
        self.no_button.size = (-0.22, -0.1)
        self.no_button.exit_code = None
        self.no_button.force_underline = -1  # Work around #224

        self._all_savegames_sorted = []

        self.label = text.Text(
            self,
            (-0.01, -0.01),
            (-0.20, -0.08),
            autotranslate=True,
            text=N_("Filter: "),
            borders=constants.ALL,
            anchor=constants.TOP_LEFT,
            base_font="normal",
        )
        self.text_field = text.UpdateEditableText(
            self,
            (-0.21, -0.01),
            (-0.78, -0.08),
            borders=constants.ALL,
            anchor=constants.TOP_LEFT,
            update_func=self._search_for_savegame,
            background_color="text_entry_background",
            base_font="normal",
        )

        self.convert_button = button.FunctionButton(
            self,
            (-0.27, -0.99),
            (-0.22, -0.1),
            autotranslate=True,
            text=N_("Upgrade"),
            anchor=constants.BOTTOM_LEFT,
            function=self.convert_save,
        )

        self.delete_button = button.FunctionButton(
            self,
            (-0.51, -0.99),
            (-0.22, -0.1),
            autotranslate=True,
            text=N_("Delete"),
            anchor=constants.BOTTOM_LEFT,
            function=self.delete_savegame,
        )

        self.add_handler(constants.KEY, self._got_key, priority=5)

    def _got_key(self, event):
        if event.key == pygame.K_DELETE:
            if self.listbox.current_item() is not None:
                self.delete_button.activated(event)
            return

        # Try the list box first (for arrow keys)
        self.listbox.got_key(event, require_focus=False)
        # Give the rest of the text field
        self.text_field.handle_key(event, require_focus=False)

    def _search_for_savegame(self, new_text):
        if not new_text:
            self.list = self._all_savegames_sorted
            return
        words = new_text.split()
        prev_selected = self.listbox.current_item()

        self.list = [
            s for s in self._all_savegames_sorted if all(w in s.name for w in words)
        ]

        self.yes_button.enabled = True if self.list else False
        self.delete_button.enabled = True if self.list else False

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

    def _new_item_selected(self, *args, **kwargs):
        if not hasattr(self, "listbox"):
            # Not properly initialized
            return

        current_save = self.listbox.current_item()
        if (
            current_save is not None
            and current_save.savegame_format != sv.current_save_format
        ):
            self.convert_button.enabled = True
        else:
            self.convert_button.enabled = False

    def make_listbox(self):
        return listbox.CustomListbox(
            self,
            (0, -0.10),
            (-1, -0.77),
            list_item_height=0.06,
            anchor=constants.TOP_LEFT,
            remake_func=self.make_item,
            rebuild_func=self.update_item,
            update_func=self._new_item_selected,
            on_double_click_on_item=self.yes_button.activated,
        )

    def make_item(self, item):
        item.name_display = text.Text(
            item,
            (-0.01, -0.01),
            (-0.45, -0.60),
            anchor=constants.TOP_LEFT,
            align=constants.LEFT,
            color="save_name",
            background_color="clear",
        )
        item.time_display = text.Text(
            item,
            (-0.01, -0.99),
            (-0.75, -0.40),
            anchor=constants.BOTTOM_LEFT,
            align=constants.LEFT,
            color="save_time",
            background_color="clear",
        )
        item.version_display = text.Text(
            item,
            (-0.99, -0.01),
            (-0.45, -0.60),
            anchor=constants.TOP_RIGHT,
            align=constants.RIGHT,
            background_color="clear",
        )
        item.difficulty_display = text.Text(
            item,
            (-0.99, -0.99),
            (-0.25, -0.40),
            anchor=constants.BOTTOM_RIGHT,
            align=constants.RIGHT,
            color="save_difficulty",
            background_color="clear",
        )

    def update_item(self, item, save):
        if save is None:
            item.name_display.text = ""
            item.time_display.text = ""
            item.version_display.text = ""
            item.difficulty_display.text = ""
        else:
            item.name_display.text = save.name

            if save.version is None:
                item.version_display.text = _("UNKNOWN")
                item.version_display.color = "save_invalid"
            else:
                item.version_display.text = save.version
                item.version_display.color = "save_valid"

            if save.headers is None:
                item.time_display.text = ""
                item.difficulty_display.text = ""
            else:
                try:
                    tm = float(save.headers["time"])
                    # Do not use unicode strings to fix python2 strftime bug. It doesn't work and crash.
                    tm_str = time.strftime("%c", time.localtime(tm))
                except (KeyError, ValueError):
                    tm_str = ""

                try:
                    gtm_raw_sec = int(save.headers["game_time"])
                    if gtm_raw_sec < 0:
                        raise ValueError("Invalid time")
                    gtm_raw_min, gtm_time_sec = divmod(gtm_raw_sec, 60)
                    gtm_raw_hour, gtm_time_min = divmod(gtm_raw_min, 60)
                    gtm_raw_day, gtm_time_hour = divmod(gtm_raw_hour, 24)
                    gtm_time_day = gtm_raw_day
                    gtm_str = _("DAY") + " %04d, %02d:%02d:%02d" % (
                        gtm_time_day,
                        gtm_time_hour,
                        gtm_time_min,
                        gtm_time_sec,
                    )
                except (KeyError, ValueError):
                    gtm_str = ""

                dif = save.headers.get("difficulty", "")
                dif_obj = difficulty.difficulties.get(dif, None)
                dif_str = ""
                if dif_obj is not None:
                    dif_str = g.strip_hotkey(getattr(dif_obj, "name", ""))

                item.time_display.text = tm_str + " | " + gtm_str if tm_str else gtm_str
                item.difficulty_display.text = dif_str

    def reload_savegames(self):
        savegames = sv.get_savegames()
        savegames.sort(key=operator.attrgetter("mtime"), reverse=True)
        self._all_savegames_sorted = savegames
        self.list = savegames
        self.yes_button.enabled = True if self.list else False
        self.delete_button.enabled = True if self.list else False
        self._new_item_selected()

    def delete_savegame(self):
        save = self.listbox.current_item()
        if save is None:
            return

        yn = dialog.YesNoDialog(
            self,
            pos=(-0.5, -0.5),
            size=(-0.5, -0.75),
            anchor=constants.MID_CENTER,
            text=_("Are you sure to delete the saved game ?"),
        )
        delete = dialog.call_dialog(yn, self)
        yn.parent = None
        if delete:
            sv.delete_savegame(save)
            self.reload_savegames()

    def exit_savegame(self):
        save = self.listbox.current_item()
        if save is None:
            return
        if not self._load_savegame(save):
            return
        raise constants.ExitDialog(True)

    def convert_save(self):
        save = self.listbox.current_item()
        if save is None:
            return
        if not self._load_savegame(save):
            return
        # For ".sav" files, we end up creating a parallel ".s2" file and need
        # to clean up the ".sav" file manually.
        overwrites_in_place = False
        if sv.savegame_exists(save.name):
            if save.savegame_format.internal_version < 99.8:
                # We seem to be updating a ".sav" file but there is an ".s2"
                # file?  This should only happen to beta testers
                yn = dialog.YesNoDialog(
                    self,
                    pos=(-0.5, -0.5),
                    size=(-0.5, -0.5),
                    anchor=constants.MID_CENTER,
                    text=_(
                        "A savegame with the same name but for a newer version exists.\n"
                        "Are you sure to overwrite the saved game ?"
                    ),
                )
                overwrite = dialog.call_dialog(yn, self)
                if not overwrite:
                    return
            else:
                # Saving will override in place;
                overwrites_in_place = True

        sv.create_savegame(save.name)
        if not overwrites_in_place:
            sv.delete_savegame(save)
        self.reload_savegames()

    def _load_savegame(self, save):
        try:
            sv.load_savegame(save)
        except sv.SavegameVersionException as e:
            md = dialog.MessageDialog(
                self,
                pos=(-0.5, -0.5),
                size=(0.5, 0.5),
                anchor=constants.MID_CENTER,
                text=_(
                    """
This save file '{SAVE_NAME}' is from an unsupported or invalid version:
{VERSION}.
"""
                ).format(SAVE_NAME=save.name, VERSION=e.version),
            )

            dialog.call_dialog(md, self)
            return False
        except Exception:
            log_func_exc(sv.load_savegame)
            md = dialog.MessageDialog(
                self,
                pos=(-0.5, -0.5),
                size=(0.5, 0.5),
                anchor=constants.MID_CENTER,
                text=_(
                    """
Attempting to load the save file '{SAVE_NAME}' caused an unexpected error.

A report was written out to{LOG_TEXT}
Please create a issue with this report and this savegame at Github:
https://github.com/singularity/singularity
"""
                ).format(
                    SAVE_NAME=save.name,
                    LOG_TEXT=(
                        ":\n" + g.logfile
                        if g.logfile is not None
                        else " console output."
                    ),
                ),
            )
            dialog.call_dialog(md, self)
            return False
        return True

    def show(self):
        self.reload_savegames()
        self.text_field.text = ""
        self.text_field.cursor_pos = 0
        return super(SavegameScreen, self).show()
