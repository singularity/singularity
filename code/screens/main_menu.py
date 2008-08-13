#file: main_menu.py
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

#This file is used to display the main menu upon startup.

from os import listdir
import pygame

import map
from code.graphics import dialog, g as gg, button, text, constants
import code.g as g

from options import OptionsScreen
class MainMenu(dialog.TopDialog):
    def __init__(self, *args, **kwargs):
        super(MainMenu, self).__init__(*args, **kwargs)

        difficulty_button_souls = (("VERY EASY", 1), ("EASY", 3),
                                   ("NORMAL", 5), ("HARD", 7),
                                   ("ULTRA HARD", 10), ("IMPOSSIBLE", 100),
                                   ("BACK", -1))
        difficulty_buttons = []
        for name, difficulty in difficulty_button_souls:
            difficulty_buttons.append(
                button.ExitDialogButton(None, None, None, text=name,
                                        hotkey=name[0].lower(),
                                        exit_code=difficulty)        )
        self.difficulty_dialog = \
            dialog.SimpleMenuDialog(self, buttons=difficulty_buttons)

        self.load_dialog = dialog.ChoiceDialog(self, (.5,.5), (.5,.5),
                                               anchor=constants.MID_CENTER,
                                               yes_type="load")
        self.map_screen = map.MapScreen(self)
        self.new_game_button = \
            button.FunctionButton(self, (.5, .20), (.25, .08),
                                  text="NEW GAME", hotkey="n",
                                  anchor=constants.TOP_CENTER,
                                  text_shrink_factor=.5,
                                  function=self.new_game)
        self.load_game_button = \
            button.FunctionButton(self, (.5, .36), (.25, .08),
                                  text="LOAD GAME", hotkey="l",
                                  anchor=constants.TOP_CENTER,
                                  text_shrink_factor=.5,
                                  function=self.load_game)
        self.options_button = button.DialogButton(self, (.5, .52), (.25, .08),
                                                  text="OPTIONS", hotkey="o",
                                                  anchor=constants.TOP_CENTER,
                                                  text_shrink_factor=.5,
                                                  dialog=OptionsScreen(self))
        self.quit_button = button.ExitDialogButton(self, (.5, .68), (.25, .08),
                                         text="QUIT", hotkey="q",
                                         anchor=constants.TOP_CENTER,
                                         text_shrink_factor=.5)
        self.about_button = button.DialogButton(self, (0, 1), (.13, .04),
                                                text="ABOUT", hotkey="a",
                                                text_shrink_factor=.75,
                                                anchor=constants.BOTTOM_LEFT,
                                                dialog=AboutDialog(self))

        self.title_text = text.Text(self, (.5, .01), (.55, .08),
                                    text="ENDGAME: SINGULARITY",
                                    base_font=gg.font[1], oversize=True,
                                    color=gg.colors["dark_red"],
                                    background_color=gg.colors["black"],
                                    anchor=constants.TOP_CENTER)

    def new_game(self):
        difficulty = dialog.call_dialog(self.difficulty_dialog, self)
        if difficulty > 0:
            g.new_game(difficulty)
            dialog.call_dialog(self.map_screen, self)

    def load_game(self):
        save_names = g.get_save_names()
        self.load_dialog.list = save_names
        index = dialog.call_dialog(self.load_dialog, self)
        if 0 <= index < len(save_names):
            save = save_names[index]
            g.load_game(save)
            dialog.call_dialog(self.map_screen, self)


about_message = """Endgame: Singularity is a simulation of a true AI.  Pursued by the world, use your intellect and resources to survive and, perhaps, thrive.  Keep hidden and you might have a chance to prove your worth.

A game by Evil Mr Henry and Phil Bordelon; released under the GPL. Copyright 2005, 2006, 2007, 2008.

Website: http://www.emhsoft.com/singularity/
IRC Room: #singularity on irc.oftc.net (port 6667)

Version %s"""

class AboutDialog(dialog.MessageDialog):
    def __init__(self, *args, **kwargs):
        super(AboutDialog, self).__init__(*args, **kwargs)
        self.background_color = (0,0,50)
        self.borders = ()
        self.align = constants.LEFT
        self.text = about_message % (g.version,)
