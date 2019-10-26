#file: warning.py
#Copyright (C) 2005,2006,2008 Evil Mr Henry, Phil Bordelon, FunnyMan3595,
#and Anne M. Archibald.
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

#This file is used to display message dialogs.

from __future__ import absolute_import

import pygame

from singularity.code import g
from singularity.code.graphics import dialog, constants, text, button


class MessageDialogs(object):

    def __init__(self, screen):
        self.screen = screen
        self.dialog = MessageListDialog(screen,
                                        yes_type="continue",
                                        no_type="pause")

    def show_list(self, message_type, messages):
        if (len(messages) == 0):
            return

        self.dialog.type = message_type
        self.dialog.list = messages
        ret = dialog.call_dialog(self.dialog, self.screen)

        # Pause game
        if (not ret):
            g.pl.pause_game()
            return True

        # Continue
        return False

class MessageListDialog(dialog.YesNoDialog):

    def __init__(self, *args, **kwargs):
        super(MessageListDialog, self).__init__(*args, **kwargs)
        
        self.title = text.Text(self, (-.01, -.01), (-.98, -.1),
                               background_color="clear",
                               anchor=constants.TOP_LEFT,
                               valign=constants.MID, align=constants.LEFT,
                               base_font="special", text_size=28)

        self.body = text.Text(self, (-.01, -.11), (-.98, -.83),
                               background_color="clear",
                               anchor=constants.TOP_LEFT,
                               valign=constants.TOP, align=constants.LEFT,
                               text_size=20)

        self.prev_button = button.FunctionButton(self, (-.78, -.01), (-.2, -.1),
                                                 text=_("&PREV"), autohotkey=True,
                                                 anchor=constants.TOP_RIGHT,
                                                 text_size=28,
                                                 function=self.prev_message)   

        self.next_button = button.FunctionButton(self, (-.99, -.01), (-.2, -.1),
                                                 text=_("&NEXT"), autohotkey=True,
                                                 anchor=constants.TOP_RIGHT,
                                                 text_size=28,
                                                 function=self.next_message)            
                               
        self.add_key_handler(pygame.K_LEFT, self.handle_key)
        self.add_key_handler(pygame.K_RIGHT, self.handle_key)
        
        # TODO: Add button "Do not show this message again"

    def rebuild(self):
        super(MessageListDialog, self).rebuild()

        if (len(self.list) == 1):
            self.title.text = self.type.title_simple()
            self.body.text = self.list[0].full_message
            self.prev_button.visible = False
            self.next_button.visible = False
        else:
            self.title.text = self.type.title_multiple() % (self.list_pos + 1, len(self.list))
            self.body.text  = self.list[self.list_pos].full_message
            self.body.color = self.list[self.list_pos].full_message_color
            self.prev_button.visible = True
            self.next_button.visible = True

    def prev_message(self):
        self.list_pos = max(self.list_pos - 1, 0)
        self.needs_rebuild = True

    def next_message(self):
        self.list_pos = min(self.list_pos + 1, len(self.list) - 1)
        self.needs_rebuild = True

    def handle_key(self, event):
        if event.type == pygame.KEYUP: return
        if event.key == pygame.K_LEFT: self.prev_message()
        if event.key == pygame.K_RIGHT: self.next_message()
        
    def show(self):
        self.list_pos = 0
        self.needs_rebuild = True
        return super(MessageListDialog, self).show()
