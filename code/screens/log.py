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

from numpy import array
import pygame

from code import g
from code.graphics import dialog, button, slider, text, constants, listbox, g as gg

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
                               item_borders=False, item_selectable=False)

    def show(self):
        self.list = ["%s -- %s" % (_("DAY") + " %04d, %02d:%02d:%02d" % log[0],
                                   self.create_log_text(log[1], log[2])) for log in g.pl.log]

        self.default = len(self.list) - 1

        return super(LogScreen, self).show()

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
