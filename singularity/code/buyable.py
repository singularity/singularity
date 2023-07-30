# file: buyable.py
# Copyright (C) 2008 Evil Mr Henry, Phil Bordelon, and FunnyMan3595
# This file is part of Endgame: Singularity.

# Endgame: Singularity is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# Endgame: Singularity is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Endgame: Singularity; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

# This file contains the buyable class, a super class for item, base and tech

from __future__ import absolute_import

from operator import truediv
from singularity.code import g, spec, prerequisite
from singularity.code.pycompat import *

cash, cpu, labor = range(3)

import numpy
from numpy import int64

numpy.seterr(all="ignore")
array = numpy.array


def spec_parse_cost(value):
    spec.validate_must_be_list(value)
    if len(value) != 3:  # pragma: no cover
        raise ValueError(
            "Cost must have exactly 3 values (CPU, money, time), got %d items (value: %s)"
            % (len(value), repr(value))
        )
    return [int(x) for x in value]


SPEC_FIELD_PREREQUISITES = spec.SpecDataField(
    "prerequisites",
    data_field_name="pre",
    converter=spec.promote_to_list,
    default_value=list,
)
SPEC_FIELD_COST = spec.SpecDataField("cost", converter=spec_parse_cost)


class BuyableSpec(spec.GenericSpec, prerequisite.Prerequisite):
    def __init__(self, id, cost, prerequisites):
        spec.GenericSpec.__init__(self, id)
        prerequisite.Prerequisite.__init__(self, prerequisites)

        self.name = id
        # This will be set when languages are (re)loaded
        self.description = ""
        self._cost = cost

    @property
    def cost(self):
        cost = array(self._cost, int64)
        cost[labor] *= g.minutes_per_day * getattr(g.pl, "labor_bonus", 1)
        cost[labor] /= 10000
        cost[cpu] *= g.seconds_per_day
        return cost

    def describe_cost(self, cost, hide_time=False):
        cpu_label = _("%s CPU") % g.to_cpu(cost[cpu])
        cash_label = _("%s money") % g.to_money(cost[cash])
        labor_label = ", %s" % g.to_time(cost[labor]).replace(" ", "\xA0")
        if hide_time:
            labor_label = ""
        return "%s, %s%s" % (
            cpu_label.replace(" ", "\xA0"),
            cash_label.replace(" ", "\xA0"),
            labor_label,
        )

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

    def __lt__(self, other):
        # For sorting buyables, we sort by cost; Python is smart enough
        # to handle this properly for tuples.  The first element is price in
        # cash, which is the one we care about the most.
        return tuple(self.cost) < tuple(other.cost)


class Buyable(object):
    def __init__(self, spec, count=1):
        self.spec = spec
        self.prerequisites = spec.prerequisites

        self.total_cost = spec.cost * count
        self.total_cost[labor] //= count
        self.cost_left = array(self.total_cost, int64)

        self.count = count
        self.done = False

    @property
    def id(self):
        return self.spec.id

    @property
    def name(self):
        if hasattr(self, "_name"):
            return self._name
        return self.spec.name

    @property
    def description(self):
        return self.spec.description

    # Note that this is a method, handled by a property to avoid confusing
    # pickle.
    @property
    def available(self):
        return self.spec.available

    @property
    def cost_paid(self):
        return self.total_cost - self.cost_left

    @cost_paid.setter
    def cost_paid(self, value):
        self.cost_left = self.total_cost - value

    def finish(self, is_player=True, loading_savegame=False):
        if not self.done:
            self.cost_left = array([0, 0, 0], int64)
            self.done = True

            if is_player:
                self.spec.created += 1

    def _percent_complete(self, available=(0, 0, 0)):
        available_array = array(available, int64)
        return truediv(self.cost_paid + available_array, self.total_cost)

    def min_valid(self, complete):
        return complete[self.total_cost > 0].min()

    def percent_complete(self):
        return self.min_valid(self._percent_complete())

    def calculate_work(self, cash_available, cpu_available, time=0):
        """Given an amount of available resources, calculates and returns the
        amount that would be spent and the progress towards completion."""

        # Figure out how much we could complete.
        pct_complete = self._percent_complete([cash_available, cpu_available, time])

        # Find the least-complete resource.
        least_complete = self.min_valid(pct_complete)

        # Limit the other two be up to the least-complete
        complete_cap = min(1, least_complete)
        pct_complete[pct_complete > complete_cap] = complete_cap

        # Translate that back to the total amount complete.
        raw_paid = pct_complete * self.total_cost

        # And apply it.
        was_complete = self.cost_paid
        cost_paid = numpy.maximum(
            numpy.cast[int64](numpy.round(raw_paid)), was_complete
        )
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
        # Does nothing by default
        pass

    def serialize_buyable_fields(self, serialized_mapping=None):
        if serialized_mapping is None:
            serialized_mapping = {}
        if self.done:
            serialized_mapping["done"] = self.done
        else:
            serialized_mapping["cost_paid"] = [long(x) for x in self.cost_paid]
        if self.count != 1:
            serialized_mapping["count"] = self.count
        return serialized_mapping

    def restore_buyable_fields(self, obj_data, game_version):
        is_done = obj_data.get("done", 0)
        self.count = obj_data.get("count", 1)
        if is_done:
            self.finish(is_player=False, loading_savegame=True)
        else:
            self.cost_paid = array(obj_data["cost_paid"], int64)
