#file: buyable.py
#Copyright (C) 2008 Evil Mr Henry, Phil Bordelon, and FunnyMan3595
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

#This file contains the item class.

from operator import div, truediv
import g

cash, cpu, labor = range(3)

import numpy
array = numpy.array

class BuyableClass(object):
    def __init__(self, id, description, cost, prerequisites, type = ""):
        self.name = self.id = id
        self.description = description
        self._cost = cost
        self.prerequisites = prerequisites

        if type:
            self.prefix = type + "_"
        else:
            self.prefix = ""

    def get_cost(self):
        cost = array(self._cost)
        cost[labor] *= g.minutes_per_day * g.pl.labor_bonus
        cost[labor] /= 10000
        cost[cpu] *= g.seconds_per_day
        return cost
        
    cost = property(get_cost)

    def __cmp__(self, other):
        # For sorting buyables, we sort by cost; Python's cmp() is smart enough
        # to handle this properly for tuples.  The first element is price in
        # cash, which is the one we care about the most.
        return cmp(tuple(self.cost), tuple(other.cost))

    def available(self):
        or_mode = False
        assert type(self.prerequisites) == list
        for prerequisite in self.prerequisites:
            if prerequisite == "OR":
                or_mode = True
            if prerequisite in g.techs and g.techs[prerequisite].done:
                if or_mode:
                    return True
            else:
                if not or_mode:
                    return False
        # If we're not in OR mode, we met all our prerequisites.  If we are, we
        # didn't meet any of the OR prerequisites.
        return not or_mode

for stat in ("count", "complete_count", "total_count", 
             "total_complete_count"):
    # Ugly syntax, but it seems to be the Right Way to do it.
    def get(self, stat=stat):
        return g.stats.get_statistic(self.prefix + self.id + "_" + stat)
    def set(self, value, stat=stat):
        return g.stats.set_statistic(self.prefix + self.id + "_" + stat, value)

    stat_prop = property(get, set)
    setattr(BuyableClass, stat, stat_prop)

class Buyable(object):
    def __init__(self, type, count=1):
        self.type = type
        type.count += count
        type.total_count += count

        self.name = self.id = type.id
        self.description = type.description
        self.prerequisites = type.prerequisites

        self.total_cost = type.cost * count
        self.total_cost[labor] //= count
        self.cost_left = array(self.total_cost)

        self.count = count
        self.done = False

    # Note that this is a method, handled by a property to avoid confusing
    # pickle.
    available = property(lambda self: self.type.available)

    def convert_from(self, save_version):
        if save_version <= 3:
            if self.cost_left[cpu] < self.total_cost[cpu]:
                self.cost_left[cpu] *= g.seconds_per_day

    def finish(self):
        if not self.done:
            self.type.complete_count += self.count
            self.type.total_complete_count += self.count
            self.cost_left = array([0,0,0])
            self.done = True

    def get_cost_paid(self):
        return self.total_cost - self.cost_left

    def set_cost_paid(self, value):
        self.cost_left = self.total_cost - value

    cost_paid = property(get_cost_paid, set_cost_paid)

    def work_on(self, cash_available = None, cpu_available = None, time = 0):
        if self.done:
            return

        # cash_available defaults to all the player's cash.
        if cash_available == None:
            cash_available = g.pl.cash

        # cpu_available defaults to the entire CPU Pool.
        if cpu_available == None:
            cpu_available = g.pl.cpu_pool

        # Figure out how much we could complete.
        was_complete = self.cost_paid
        available = array([cash_available, cpu_available, time])
        pct_complete = truediv(was_complete + available, self.total_cost)

        # Find the least-complete resource, and let the other two be up to
        # 5 percentage points closer to completion.
        max = pct_complete.min() + .05
        pct_complete[pct_complete > max] = max

        # Translate that back to the total amount complete.
        self.cost_paid = numpy.cast[int](pct_complete * self.total_cost)
        spent = self.cost_paid - was_complete

        # Consume CPU and Cash.
        g.pl.cpu_pool -= spent[cpu]
        g.pl.cash -= spent[cash]

        if (self.cost_left <= 0).all():
            self.finish()
            return True
        return False

    def destroy(self):
        self.type.count -= self.count
        if self.done:
            self.type.complete_count -= self.count
