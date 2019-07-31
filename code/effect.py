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

from __future__ import absolute_import

from code import g, mixer

class Effect(object):

    def __init__(self, parent, effect_stack):
        self.parent_id = parent.id
        self.parent_name = parent.__class__.__name__
        self.effect_stack = effect_stack

    def trigger(self):
        # effect_data is now a stack of instructions to run the effect.
        # multiple effect can be run simultaneous
        effect_iter = iter(self.effect_stack)
        
        for current in effect_iter:

            if current == "interest":
                g.pl.interest_rate += int(next(effect_iter))
            elif current == "income":
                g.pl.income += int(next(effect_iter))
            elif current == "cost_labor":
                g.pl.labor_bonus -= int(next(effect_iter))
            elif current == "job_profit":
                g.pl.job_bonus += int(next(effect_iter))
            elif current == "display_discover":
                g.pl.display_discover = next(effect_iter)
            elif current == "endgame":
                mixer.play_music("win")
                g.map_screen.show_story_section("Win")
                for group in g.pl.groups.values():
                    group.is_actively_discovering_bases = False
                g.pl.apotheosis = True
                g.pl.had_grace = True
            elif current == "suspicion":
                who = next(effect_iter)
                value = int(next(effect_iter))

                if who in g.pl.groups:
                    g.pl.groups[who].alter_suspicion_decay(value)
                elif who == "onetime":
                    for group in g.pl.groups.values():
                        group.alter_suspicion(-value)
                else:
                    print("Unknown group/bonus '%s' in %s %s." \
                    % (who, self.parent_name, self.parent_id))
            elif current == "discover":
                who = next(effect_iter)
                value = int(next(effect_iter))

                if who in g.pl.groups:
                    g.pl.groups[who].alter_discover_bonus(-value)
                else:
                    print("Unknown group/bonus '%s' in %s %s." \
                    % (who, self.parent_name, self.parent_id))
            else:
                print("Unknown action '%s' in %s %s." \
                % (current, self.parent_name, self.parent_id))

