from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals
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

import singularity.code.g
#detection = (news, science, covert, person)

class Event(object):
    # For some as-yet-unknown reason, cPickle decides to call event.__init__()
    # when an event is loaded, but before filling it.  So Event pretends to
    # allow no arguments, even though that would cause Bad Things to happen.
    def __init__(self, name=None, description=None, event_type=None,
                 result=None, chance=None, unique=None):
        self.name = name
        self.event_id = name
        self.description = description
        self.event_type = event_type
        self.result = result
        self.chance = chance
        self.unique = unique
        self.triggered = 0
    def trigger(self):
        singularity.code.g.map_screen.show_message(self.description)

        # If this is a unique event, mark it as triggered.
        if self.unique:
            self.triggered = 1

        # TODO: Merge this code with its duplicate in tech.py.
        what, who = self.result[0].split("_", 1)
        if who in singularity.code.g.pl.groups:
            if what == "suspicion":
                singularity.code.g.pl.groups[who].alter_suspicion_decay(self.result[1])
            elif what == "discover":
                singularity.code.g.pl.groups[who].alter_discover_bonus(-self.result[1])
            else:
                print("Unknown bonus '%s' in event %s." % (what, self.name))
        elif who == "onetime" and what == "suspicion":
            for group in singularity.code.g.pl.groups.values():
                group.alter_suspicion(-self.result[1])
        else:
            print("Unknown group/bonus '%s' in event %s. " % (self.result[0],
                                                              self.name))
