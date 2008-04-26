#file: event.py
#Copyright (C) 2005,2006 Evil Mr Henry and Phil Bordelon
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

import pygame
import g
#detection = (news, science, covert, person)

class event_class:
    def __init__(self, name, description, event_type, result, chance, unique):
        self.name = name
        self.event_id = name
        self.description = description
        self.event_type = event_type
        self.result = result
        self.chance = chance
        self.unique = unique
        self.triggered = 0
    def trigger(self):
        g.create_dialog(self.description, g.font[0][18], (g.screen_size[0]/2 - 100, 50),
            (200, 200), g.colors["dark_blue"], g.colors["white"], g.colors["white"])

        # If this is a unique event, mark it as triggered.
        if self.unique:
            self.triggered = 1

        # TODO: Merge this code with its duplicate in tech.py.
        if self.result[0].startswith("suspicion_"):
            who = self.result[0][10:]
            if who == "onetime":
                for group in g.pl.groups.values():
                    group.alter_suspicion(-self.result[1])
            elif who in g.pl.groups:
                g.pl.groups[who].alter_suspicion_decay(self.result[1])
            else:
                print "Unknown group '%s' in event %s." % (who, self.name)
        elif self.result[0].startswith("discover_"):
            who = self.result[0][9:]
            if who in g.pl.groups:
                g.pl.groups[who].alter_discover_bonus(-self.result[1])
            else:
                print "Unknown group '%s' in event %s." % (who, self.name)
