#file: tech.py
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

#This file contains the tech class.


import pygame
import g

#cost = (money, ptime, labor)
#detection = (news, science, covert, person)
class tech:
    def __init__(self, tech_id, descript, known, cost, prereq, danger, tech_type,
                                        secondary_data):
        self.tech_id = tech_id
        self.name = tech_id
        self.descript = descript
        self.known = known
        self.cost = cost
        self.prereq = prereq
        self.danger = danger
        self.result = ""
        self.tech_type = tech_type
        self.secondary_data = secondary_data
    def study(self, cost_towards):
        self.cost = (self.cost[0]-cost_towards[0], self.cost[1]-cost_towards[1],
                self.cost[2]-cost_towards[2])
        if self.cost[0] <= 0: self.cost = (0, self.cost[1], self.cost[2])
        if self.cost[1] <= 0: self.cost = (self.cost[0], 0, self.cost[2])
        if self.cost[2] <= 0: self.cost = (self.cost[0], self.cost[1], 0)
        if self.cost == (0, 0, 0):
            self.gain_tech()
            return 1
        return 0
    def gain_tech(self):
        self.cost = (0, 0, 0)
        self.known = 1

        #give the effect of the tech

        if self.tech_id == "Personal Identification":
            for base_loc in g.bases:
                for base_name in g.bases[base_loc]:
                    if base_name.studying == "Menial Jobs":
                        base_name.studying = "Basic Jobs"
        if self.tech_id == "Voice Synthesis":
            for base_loc in g.bases:
                for base_name in g.bases[base_loc]:
                    if base_name.studying == "Basic Jobs":
                        base_name.studying = "Intermediate Jobs"
        if self.tech_id == "Simulacra":
            for base_loc in g.bases:
                for base_name in g.bases[base_loc]:
                    if base_name.studying == "Intermediate Jobs":
                        base_name.studying = "Expert Jobs"

        if self.tech_type == "interest":
            g.pl.interest_rate += self.secondary_data
        elif self.tech_type == "income":
            g.pl.income += self.secondary_data
        elif self.tech_type == "cost_labor_bonus":
            g.pl.labor_bonus -= self.secondary_data
        elif self.tech_type == "job_expert":
            g.pl.job_bonus += self.secondary_data
        elif self.tech_type.startswith("suspicion_"):
            who = self.tech_type[10:]
            if who == "onetime":
                for group in g.pl.groups.values():
                    group.alter_suspicion(-self.secondary_data)
            elif who in g.pl.groups:
                g.pl.groups[who].alter_suspicion_decay(self.secondary_data)
            else:
                print "Unknown group '%s' in tech %s." % (who, self.name)
        elif self.tech_type.startswith("discover_"):
            who = self.tech_type[9:]
            if who in g.pl.groups:
                g.pl.groups[who].alter_discover_bonus(-self.secondary_data)
            else:
                print "Unknown group '%s' in tech %s." % (who, self.name)
        elif self.tech_type == "endgame_sing":
            g.play_music("win")
            g.create_dialog(g.strings["wingame"])
            for group in g.pl.groups.values():
                group.discover_bonus = 0
