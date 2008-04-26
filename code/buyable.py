#file: buyable.py
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

#This file contains the item class.

import pygame
import g

cash, cpu, labor = range(3)

# List with element-wise math.  Similar to numpy.array.
class array(list):
    def __add__(self, other):
        return array([self[i] + other[i] for i in range(len(self))])

    def __sub__(self, other):
        return array([self[i] - other[i] for i in range(len(self))])

    def __mul__(self, other):
        return array([self[i] * other[i] for i in range(len(self))])

    def __divfloor__(self, other):
        return array([self[i] // other[i] for i in range(len(self))])

    def __div__(self, other):
        return array([self[i].__div__(other[i]) for i in range(len(self))])

    def __truediv__(self, other):
        return array([self[i].__truediv__(other[i]) for i in range(len(self))])

    def __nonzero__(self):
        for element in self:
            if element > 0:
                return True
        return False

class Buyable_Class(object):
    def __init__(self, id, description, cost, prerequisites):
        self.name = self.id = id
        self.description = description
        self.cost = cost
        self.prerequisites = prerequisites

    def __cmp__(self, other):
        # For sorting buyables, we sort by cost; Python's cmp() is smart enough
        # to handle this properly for tuples.  The first element is price in
        # cash, which is the one we care about the most.
        return cmp(self.cost, other.cost)

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

class Buyable(object):
    def __init__(self, type):
        self.type = type
        self.name = self.id = type.id
        self.description = type.description
        self.prerequisites = type.prerequisites

        # Note that this is a method.
        self.available = type.available

        self.total_cost = array(type.cost)
        self.total_cost[labor] *= g.minutes_per_day * g.pl.labor_bonus
        self.total_cost[labor] /= 10000
        self.cost_left = array(self.total_cost)

        self.done = False

    def _work_on(self, cost_towards):
        self.cost_left -= array(cost_towards)
        if not self.cost_left:
            self.finish()
            return True
        return False

    def finish(self):
        self.cost_left = array([0,0,0])
        self.done = True

    cost_paid = property(lambda self: self.total_cost - self.cost_left)

    def get_wanted(self, resource, limiting, available_limiting):
        # Gets the highest amount of additional resource possible, such that:
        #   resource_spent/resource_total <= limiting_spent/limiting_total
        # i.e. % resource complete <= % limiting complete.

        limit_max = self.total_cost[limiting]
        limit_paid = self.cost_paid[limiting]
        limit_left = self.cost_left[limiting]

        if limit_left <= available_limiting:
            return self.cost_left[resource]

        limit = limit_paid + available_limiting

        total_wanted = (self.total_cost[resource] * limit) // limit_max

        return total_wanted - self.cost_paid[resource]

    def work_on(self, cash_available = None, cpu_available = None, time = 0):
        if self.done:
           return

        # cash_available is unused.  Could be used to limit expenditures later.
        # Right now, we just default to all the player's cash.
        if cash_available == None:
            cash_available = g.pl.cash

        # cpu_available is used for researching.  It defaults to cpu_for_day for
        # construction.
        if cpu_available == None:
            cpu_available = g.pl.cpu_for_day

        #print cash_available, cpu_available, 

        if time > self.cost_left[labor]:
            time = self.cost_left[labor]

        cash_wanted = self.cost_left[cash]
        cpu_wanted = self.cost_left[cpu]

        # Labor limits CPU spent.
        cpu_wanted = self.get_wanted(cpu, labor, time)
        cpu_work = min(cpu_wanted, cpu_available)

        # Labor and CPU limit cash spent.
        cash_wanted = min( self.get_wanted(cash, labor, time),
                           self.get_wanted(cash, cpu, cpu_work) ) 
        cash_flow = min(cash_wanted, cash_available)

        g.pl.cpu_for_day -= cpu_work
        g.pl.cash -= cash_flow

        return self._work_on([cash_flow, cpu_work, time])

