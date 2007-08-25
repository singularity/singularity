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
    def __init__(self, name, descript, event_type, result, chance, unique):
        self.name = name
        self.event_id = name
        self.descript = descript
        self.event_type = event_type
        self.result = result
        self.chance = chance
        self.unique = unique
        self.triggered = 0
    def trigger(self):
        g.create_dialog(self.descript, g.font[0][18], (g.screen_size[0]/2 - 100, 50),
            (200, 200), g.colors["dark_blue"], g.colors["white"], g.colors["white"])

        # If this is a unique event, mark it as triggered.
        if self.unique:
           self.triggered = 1

        #Ugh, replicated code from tech...
        if self.result[0] == "suspicion_news":
            g.pl.suspicion_bonus = (g.pl.suspicion_bonus[0] + self.result[1],
                g.pl.suspicion_bonus[1], g.pl.suspicion_bonus[2], g.pl.suspicion_bonus[3])
        elif self.result[0] == "suspicion_science":
            g.pl.suspicion_bonus = (g.pl.suspicion_bonus[0], g.pl.suspicion_bonus[1] +
                self.result[1], g.pl.suspicion_bonus[2], g.pl.suspicion_bonus[3])
        elif self.result[0] == "suspicion_covert":
            g.pl.suspicion_bonus = (g.pl.suspicion_bonus[0], g.pl.suspicion_bonus[1],
                g.pl.suspicion_bonus[2] + self.result[1], g.pl.suspicion_bonus[3])
        elif self.result[0] == "suspicion_public":
            g.pl.suspicion_bonus = (g.pl.suspicion_bonus[0], g.pl.suspicion_bonus[1],
                g.pl.suspicion_bonus[2], g.pl.suspicion_bonus[3] + self.result[1])
        #Discover must be reversed to add for the data provided.
        elif self.result[0] == "discover_news":
            g.pl.discover_bonus = (g.pl.discover_bonus[0]+self.result[1],
                g.pl.discover_bonus[1], g.pl.discover_bonus[2], g.pl.discover_bonus[3])
        elif self.result[0] == "discover_science":
            g.pl.discover_bonus = (g.pl.discover_bonus[0], g.pl.discover_bonus[1] +
                self.result[1], g.pl.discover_bonus[2], g.pl.discover_bonus[3])
        elif self.result[0] == "discover_covert":
            g.pl.discover_bonus = (g.pl.discover_bonus[0], g.pl.discover_bonus[1],
                g.pl.discover_bonus[2]+self.result[1], g.pl.discover_bonus[3])
        elif self.result[0] == "discover_public":
            g.pl.discover_bonus = (g.pl.discover_bonus[0], g.pl.discover_bonus[1],
                g.pl.discover_bonus[2], g.pl.discover_bonus[3]+self.result[1])
        elif self.result[0] == "suspicion_onetime":
            temp_suspicion = []
            for i in range(4):
                temp_suspicion.append(g.pl.suspicion[i] + self.result[1])
                if temp_suspicion[i] < 0: temp_suspicion[i] = 0
            g.pl.suspicion = (temp_suspicion[0], temp_suspicion[1],
                    temp_suspicion[2], temp_suspicion[3])
