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
import buyable

class Tech(buyable.Buyable):
    def __init__(self, id, description, known, cost, prerequisites, danger, 
                 tech_type, secondary_data):
        # A bit silly, but it does the trick.
        type = buyable.Buyable_Class(id, description, cost, prerequisites,
                                     type="tech")
        super(Tech, self).__init__(type)

        self.danger = danger
        self.result = ""
        self.tech_type = tech_type
        self.secondary_data = secondary_data

        if known:
            # self.finish would re-apply the tech benefit, which is already in
            # place.
            super(Tech, self).finish()

    def finish(self):
        super(Tech, self).finish()
        self.gain_tech()

    def gain_tech(self):
        #give the effect of the tech
        if self.id == "Personal Identification":
            for base_loc in g.bases:
                for base_name in g.bases[base_loc]:
                    if base_name.studying == "Menial Jobs":
                        base_name.studying = "Basic Jobs"
        if self.id == "Voice Synthesis":
            for base_loc in g.bases:
                for base_name in g.bases[base_loc]:
                    if base_name.studying == "Basic Jobs":
                        base_name.studying = "Intermediate Jobs"
        if self.id == "Simulacra":
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
