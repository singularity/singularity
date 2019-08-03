#file: tech.py
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

#This file contains the tech class.

from __future__ import absolute_import

from code import buyable, effect
from code.stats import stat


class TechSpec(buyable.BuyableSpec):
    spec_type = 'tech'
    created = stat(spec_type + "_created")


class Tech(buyable.Buyable):

    def __init__(self, id, cost, prerequisites, danger,
                 effect_data):
        # A bit silly, but it does the trick.
        spec = TechSpec(id, cost, prerequisites)
        super(Tech, self).__init__(spec)

        self.danger = danger
        self.result = ""
        self.effect = effect.Effect(self, effect_data)

    def convert_from(self, old_version):
        super(Tech, self).convert_from(old_version)
        if old_version < 99.2: # < 1.0dev
            self.effect = effect.Effect(self, [self.tech_type, self.secondary_data])
            del self.tech_type
            del self.secondary_data

    def __cmp__(self, other):
        if not isinstance(other, Tech):
            return -1
        else:
            return cmp(self.spec, other.spec)

    def get_info(self):
        cost = self.spec.describe_cost(self.total_cost, True)
        left = self.spec.describe_cost(self.cost_left, True)
        return ("%s\n%s: %s\n%s: %s\n---\n%s" %
                (self.name,
                 _("Total cost"), cost,
                 _("Cost left"), left,
                 self.description))

    def finish(self, is_player=True):
        super(Tech, self).finish(is_player)
        
        self.gain_tech()

    def gain_tech(self):
        #give the effect of the tech
        self.effect.trigger()
