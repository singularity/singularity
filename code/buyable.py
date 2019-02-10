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

#This file contains the buyable class, a super class for item, base and tech

from operator import truediv
import g
import prerequisite

cash, cpu, labor = range(3)

import numpy
numpy.seterr(all='ignore')
array = numpy.array

class BuyableSpec(prerequisite.Prerequisite):
    def __init__(self, id, cost, prerequisites):
        super(BuyableSpec, self).__init__(prerequisites)

        self.name = self.id = id
        # This will be set when languages are (re)loaded
        self.description = ''
        self._cost = cost

    @property
    def cost(self):
        cost = array(self._cost, long)
        cost[labor] *= g.minutes_per_day * getattr(g.pl,'labor_bonus',1)
        cost[labor] /= 10000
        cost[cpu] *= g.seconds_per_day
        return cost

    def describe_cost(self, cost, hide_time=False):
        cpu_label   = _("%s CPU")   % g.to_cpu(cost[cpu])
        cash_label  = _("%s money") % g.to_money(cost[cash])
        labor_label = ", %s" % g.to_time(cost[labor]).replace(" ", u"\xA0")
        if hide_time:
            labor_label = ""
        return u"%s, %s%s" % (cpu_label.replace(" ", u"\xA0"),
                              cash_label.replace(" ", u"\xA0"),
                              labor_label)

    @property
    def regions(self):
        return self._regions

    @regions.setter
    def regions(self, value):
        region_all = False
        regions = []

        for region in value:
            if "ALL" in value:
                region_all = True
            elif region in g.regions:
                regions.extend(g.regions[region].locations)
            else:
                regions.append(region)

        self._regions = regions
        self._region_all = region_all

    def buildable_in(self, location):
        return bool(self._region_all or location.id in self._regions)

    def get_info(self):
        cost_str = self.describe_cost(self.cost)
        template = "%s\n" + _("Cost:") + " %s\n---\n%s"
        return template % (self.name, cost_str, self.description)

    def __cmp__(self, other):
        # For sorting buyables, we sort by cost; Python's cmp() is smart enough
        # to handle this properly for tuples.  The first element is price in
        # cash, which is the one we care about the most.
        return cmp(tuple(self.cost), tuple(other.cost))

for stat in ("count", "complete_count", "total_count",
             "total_complete_count"):
    # Ugly syntax, but it seems to be the Right Way to do it.
    def get(self, stat=stat):
        return g.stats.get_statistic(self.spec_type + '_' + self.id + "_" + stat)
    def set(self, value, stat=stat):
        return g.stats.set_statistic(self.spec_type + '_' + self.id + "_" + stat, value)

    stat_prop = property(get, set)
    setattr(BuyableSpec, stat, stat_prop)

class Buyable(object):
    def __init__(self, type, count=1):
        self.type = type
        type.count += count
        type.total_count += count

        self.name = type.name
        self.description = type.description
        self.prerequisites = type.prerequisites

        self.total_cost = type.cost * count
        self.total_cost[labor] //= count
        self.cost_left = array(self.total_cost, long)

        self.count = count
        self.done = False

    @property
    def id(self):
        # Needed for the Effect instance, which wants to know the parent ID
        # in case of errors.
        return self.type.id

    # Note that this is a method, handled by a property to avoid confusing
    # pickle.
    @property
    def available(self): return self.type.available

    @property
    def cost_paid(self): return self.total_cost - self.cost_left

    @cost_paid.setter
    def cost_paid(self, value): self.cost_left = self.total_cost - value

    def convert_from(self, save_version):
        if save_version < 4.91: # r5_pre
            self.cost_left = array(self.cost_left, long)
            self.total_cost = array(self.total_cost, long)
            self.count = 1

    def finish(self):
        if not self.done:
            self.type.complete_count += self.count
            self.type.total_complete_count += self.count
            self.cost_left = array([0,0,0], long)
            self.done = True

    def _percent_complete(self, available=(0,0,0)):
        available_array = array(available, long)
        return truediv(self.cost_paid + available_array, self.total_cost)

    def min_valid(self, complete):
        return complete[self.total_cost > 0].min()

    def percent_complete(self):
        return self.min_valid(self._percent_complete())

    def calculate_work(self, cash_available, cpu_available, time=0):
        """Given an amount of available resources, calculates and returns the
           amount that would be spent and the progress towards completion."""

        # Figure out how much we could complete.
        pct_complete = self._percent_complete([cash_available, cpu_available,
                                               time])

        # Find the least-complete resource.
        least_complete = self.min_valid(pct_complete)

        # Limit the other two be up to the least-complete
        complete_cap = min(1, least_complete)
        pct_complete[pct_complete > complete_cap] = complete_cap

        # Translate that back to the total amount complete.
        raw_paid = pct_complete * self.total_cost

        # And apply it.
        was_complete = self.cost_paid
        cost_paid = numpy.maximum(numpy.cast[numpy.int64](numpy.round(raw_paid)),
                                  was_complete)
        spent = cost_paid - was_complete
        return spent, cost_paid

    def work_on(self, *args, **kwargs):
        """As calculate_work, but apply the changes.

        Returns a boolean indicating whether this buyable is done afterwards.
        """

        if self.done:
            return
        spent, self.cost_paid = self.calculate_work(*args, **kwargs)

        # Consume CPU and Cash.
        # Note the cast from <type 'numpy.int64'> to <type 'int'> to avoid
        # poisoning other calculations (like, say, g.pl.do_jobs).
        g.pl.cpu_pool -= int(spent[cpu])
        g.pl.cash -= int(spent[cash])

        if (self.cost_left <= 0).all():
            self.finish()
            return True
        return False

    def destroy(self):
        self.type.count -= self.count
        if self.done:
            self.type.complete_count -= self.count
