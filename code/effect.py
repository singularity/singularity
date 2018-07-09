#file: effect.py
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

#This file contains the effect class.

import g

class Effect(object):

    def __init__(self, parent, effect_type, effect_value):
        self.parent_id = parent.id
        self.parent_name = parent.__class__.__name__
        self.effect_type = effect_type
        self.effect_value = effect_value

    def trigger(self):
        if self.effect_type == "interest":
            g.pl.interest_rate += self.effect_value
        elif self.effect_type == "income":
            g.pl.income += self.effect_value
        elif self.effect_type == "cost_labor_bonus":
            g.pl.labor_bonus -= self.effect_value
        elif self.effect_type == "job_expert":
            g.pl.job_bonus += self.effect_value
        elif self.effect_type == "display_discover_partial":
            g.pl.display_discover = "partial"
        elif self.effect_type == "display_discover_full":
            g.pl.display_discover = "full"
        elif self.effect_type == "endgame_sing":
            g.play_music("win")
            g.map_screen.show_message(g.strings["wingame"])
            for group in g.pl.groups.values():
                group.discover_bonus = 0
            g.pl.apotheosis = True
            g.pl.had_grace = True
        elif self.effect_type:
            what, who = self.effect_type.split("_", 1)
            if who in g.pl.groups:
                if what == "suspicion":
                    g.pl.groups[who].alter_suspicion_decay(self.effect_value)
                elif what == "discover":
                    g.pl.groups[who].alter_discover_bonus(-self.effect_value)
                else:
                    print "Unknown action '%s' in %s %s." \
                    % (what, self.parent_name, self.parent_id)
            elif who == "onetime" and what == "suspicion":
                for group in g.pl.groups.values():
                    group.alter_suspicion(-self.effect_value)
            else:
                print "Unknown group/bonus '%s' in %s." \
                % (self.effect_type, self.parent_name, self.parent_id)
