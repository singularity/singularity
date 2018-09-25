#file: event.py
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

#This file contains the event class.

import g
import effect
#detection = (news, science, covert, person)

class Event(object):
    # For some as-yet-unknown reason, cPickle decides to call event.__init__()
    # when an event is loaded, but before filling it.  So Event pretends to
    # allow no arguments, even though that would cause Bad Things to happen.
    def __init__(self, id=None, description=None, log_description=None, event_type=None,
                 effects=None, chance=None, unique=None):
        self.event_id = self.name = self.id = id
        self.description = description
        self.log_description = log_description
        self.event_type = event_type
        self.effect = effect.Effect(self, effects)
        self.chance = chance
        self.unique = unique
        self.triggered = 0

    def convert_from(self, old_version):
        if old_version < 99: # < 1.0dev
            self.log_description = ""
        if old_version < 99.2: # < 1.0dev
            self.id = self.name
            self.effect = effect.Effect(self, self.result[0], self.result[1])
            del self.result

    def trigger(self):
        g.map_screen.show_message(self.description)

        # If this is a unique event, mark it as triggered.
        if self.unique:
            self.triggered = 1

        self.effect.trigger()
