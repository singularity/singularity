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

# List with element-wise math.  Similar to numpy.array.
class array(list):
    def __add__(self, other):
        self, other = coerce(self, other)
        return array([self[i] + other[i] for i in range(len(self))])

    def __iadd__(self, other):
        return self + other

    def __sub__(self, other):
        self, other = coerce(self, other)
        return array([self[i] - other[i] for i in range(len(self))])

    def __mul__(self, other):
        self, other = coerce(self, other)
        return array([self[i] * other[i] for i in range(len(self))])

    def __divfloor__(self, other):
        self, other = coerce(self, other)
        return array([self[i] // other[i] for i in range(len(self))])

    def __div__(self, other):
        self, other = coerce(self, other)
        return array([div(self[i], other[i]) for i in range(len(self))])

    def __truediv__(self, other):
        self, other = coerce(self, other)
        return array([truediv(self[i], other[i]) for i in range(len(self))])

    def integer_part(self):
        return array([int(self[i]) for i in range(len(self))])

    def __nonzero__(self):
        for element in self:
            if element > 0:
                return True
        return False

    def __coerce__(self, other):
        if type(other) in (float, int):
            return self, array([other] * len(self))
        else:
            return self, other

    def __str__(self):
        return "array(%s)" % super(array, self).__str__()

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
    def __init__(self, type):
        self.type = type
        type.count += 1
        type.total_count += 1

        self.name = self.id = type.id
        self.description = type.description
        self.prerequisites = type.prerequisites

        self.total_cost = type.cost
        self.cost_left = array(self.total_cost)

        self.done = False

    # Note that this is a method, handled by a property to avoid confusing
    # pickle.
    available = property(lambda self: self.type.available)

    def convert_from(self, save_version):
        if save_version <= 3:
            if self.cost_left[cpu] < self.total_cost[cpu]:
                self.cost_left[cpu] *= g.seconds_per_day

    def _work_on(self, cost_towards):
        self.cost_left -= array(cost_towards)
        if not self.cost_left:
            self.finish()
            return True
        return False

    def finish(self):
        if not self.done:
            self.cost_left = array([0,0,0])
            self.done = True
            self.type.complete_count += 1
            self.type.total_complete_count += 1

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

        # cash_available defaults to all the player's cash.
        if cash_available == None:
            cash_available = g.pl.cash

        # cpu_available defaults to the entire CPU Pool.
        if cpu_available == None:
            cpu_available = g.pl.cpu_pool

        # CPU depends on nothing.
        cpu_wanted = self.cost_left[cpu]
        cpu_work = min(cpu_wanted, cpu_available)

        # Cash depends on CPU.
        cash_wanted = self.get_wanted(cash, cpu, cpu_work)
        max_cash_flow = min(cash_wanted, cash_available)

        # Labor depends on CPU and Cash.
        labor_wanted = min( self.get_wanted(labor, cpu, cpu_work),
                            self.get_wanted(labor, cash, max_cash_flow) )
        time_spent = min(labor_wanted, time)

        # We limit cash flow to a maximum buffer of 5%, to avoid slurping all
        # the cash at the very start.
        cash_flow = min(max_cash_flow, self.get_wanted(cash, labor, time_spent)
                                       + int(.05 * self.total_cost[cash]))

        # Consume CPU and Cash.
        g.pl.cpu_pool -= cpu_work
        g.pl.cash -= cash_flow

        return self._work_on([cash_flow, cpu_work, time_spent])

    def destroy(self):
        self.type.count -= 1
        if self.done:
            self.type.complete_count -= 1
