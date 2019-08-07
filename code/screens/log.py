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

#This file is used to display the log of player action

from __future__ import absolute_import


from code import g
from code.graphics import dialog, constants, listbox
from code.logmessage import AbstractLogMessage


class LogScreen(dialog.ChoiceDialog):
    def __init__(self, parent, pos=(.5, .5), size=(.73, .63), *args, **kwargs):
        super(LogScreen, self).__init__(parent, pos, size, *args, **kwargs)
        self.anchor = constants.MID_CENTER

        self.yes_button.parent = None
        self.no_button.pos = (-.5,-.99)
        self.no_button.anchor = constants.BOTTOM_CENTER

    def make_listbox(self):
        return listbox.Listbox(self, (0, 0), (-1, -.85),
                               anchor=constants.TOP_LEFT, align=constants.LEFT,
                               on_double_click_on_item=self.handle_double_click,
                               item_borders=False, item_selectable=True)

    def handle_double_click(self, event):
        if self.listbox.is_over(event.pos) and 0 <= self.listbox.list_pos < len(g.pl.log):
            message = g.pl.log[self.listbox.list_pos]
            message_dialog = dialog.MessageDialog(self, text_size=20)
            if isinstance(message, AbstractLogMessage):
                message_dialog.text = message.full_message
                message_dialog.color = message.full_message_color
            else:
                # Old style message; fall back to rendering the log line
                message_dialog.text = self.create_log_text(message[1], message[2])
            dialog.call_dialog(message_dialog, self)

    def show(self):
        self.list = [self.render_log_message(message) for message in g.pl.log]

        self.default = len(self.list) - 1

        return super(LogScreen, self).show()

    def render_log_message(self, message):
        if isinstance(message, AbstractLogMessage):
            log_emit_time = message.log_emit_time
            log_message = message.log_line
        else:
            # Old style messages
            log_emit_time = message[0]
            log_message = self.create_log_text(message[1], message[2])
        return "%s -- %s" % (_("DAY") + " %04d, %02d:%02d:%02d" % log_emit_time, log_message)

    def create_log_text(self, log_name, log_data):
        """ Dispatch log to a function.
            This is needed because some log needs to parse its data,
            to computate them or to fully translate them.
        """
        
        method_name = 'create_' + str(log_name) + '_text'
        method = getattr(self, method_name, lambda name, data: g.strings[name] % data)
        
        return method(log_name, log_data)
        
    def create_log_destroy_text(self, log_name, log_data):
        reason = log_data[0] # reason
        name = log_data[1] # base.name
        
        log_format = log_name + '_' + reason if reason else log_name
        
        # Get BASE and LOCATION from id
        base_type = g.base_type[log_data[2]]  # base.spec.id
        location = g.pl.locations[log_data[3]]  # base.location.id
        
        return g.strings[log_format] % (name, base_type.name, location.name)

    def create_log_event_text(self, log_name, log_data):
        event = g.events[log_data[0]] # event.id
        return event.log_description
