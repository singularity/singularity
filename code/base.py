#file: base.py
#Copyright (C) 2005,2006,2007,2008 Evil Mr Henry, Phil Bordelon, Brian Reid,
#                        and FunnyMan3595
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

#This file contains the base class.


import bisect
import g
import buyable
from buyable import cash, cpu, labor

class Base_Class(buyable.Buyable_Class):
    def __init__(self, name, description, size, force_cpu, regions, 
                        detect_chance, cost, prerequisites, maintenance):
        super(Base_Class, self).__init__(name, description, cost, prerequisites,
                                         type="base")
        self.size = size
        self.force_cpu = force_cpu
        self.regions = regions
        if self.regions == ["pop"]:
            self.regions = ["N AMERICA", "S AMERICA", "EUROPE", "ASIA",
            "AFRICA", "AUSTRALIA"]

        self.detect_chance = detect_chance
        self.maintenance = maintenance
        self.flavor = []

class Base(buyable.Buyable):
    def __init__(self, name, type, built=False):
        super(Base, self).__init__(type)

        self.name = name
        self.started_at = g.pl.raw_min
        self.studying = ""

        # All the bases in a location form a circular, doubly-linked list via
        # self.next and self.prev.  Since we start off with no location, we
        # link both next and prev to ourself.
        self.next = self.prev = self
        self.location = None

        #Base suspicion is currently unused
        self.suspicion = {}

        self.cpus = [0] * self.type.size
        if self.type.force_cpu:
            # 1% chance for a Stolen Computer Time base to have a Gaming PC
            # instead.  If the base is pre-built, ignore this.
            if self.type.id == "Stolen Computer Time" and g.roll_percent(100) \
                    and not built:
                self.cpus[0] = g.item.Item(g.items["Gaming PC"])
            else:
                self.cpus[0] = g.item.Item(g.items[self.type.force_cpu])
            self.cpus[0].finish()

        #Reactor, network, security.
        self.extra_items = [0] * 3

        if built:
            self.finish()

        self.power_state = "Active"
        self.grace_over = False

        self.maintenance = buyable.array(self.type.maintenance)

    # Get the detection chance for the base, applying bonuses as needed.  If
    # accurate is False, we just return the value to the nearest full
    # percent.
    def get_detect_chance(self, accurate = True):
        # Get the base chance from the universal function.
        detect_chance = calc_base_discovery_chance(self.type.id)

        for group in g.pl.groups:
            detect_chance.setdefault(group, 0)

        # Factor in the suspicion adjustments for this particular base ...
        for group, suspicion in self.suspicion.iteritems():
            detect_chance[group] *= 10000 + suspicion
            detect_chance[group] /= 10000

        # ... any reactors built ... 
        if self.extra_items[0] and self.extra_items[0].done:
            item_qual = self.extra_items[0].item_qual
            for group in detect_chance:
                detect_chance[group] *= 10000 - item_qual
                detect_chance[group] /= 10000

        # ... and any security systems built ...
        if self.extra_items[2] and self.extra_items[2].done:
            item_qual = self.extra_items[2].item_qual
            for group in detect_chance:
                detect_chance[group] *= 10000 - item_qual
                detect_chance[group] /= 10000

        # ... and its location ...
        if self.location:
            multiplier = self.location.discovery_bonus()
            for group in detect_chance:
                detect_chance[group] *= multiplier
                detect_chance[group] /= 100

        # ... and its power state.
        if self.done and self.power_state == "Sleep":
            for group in detect_chance:
                detect_chance[group] /= 2

        # Lastly, if we're not returning the accurate values, adjust
        # to the nearest percent.
        if not accurate:
            for group in detect_chance:
                detect_chance[group] = g.nearest_percent(detect_chance[group])

        return detect_chance

    #Return the number of units the given base has of a computer.
    def has_item(self):
        num_items = 0
        for item in self.cpus:
            if item and item.done:
              num_items += 1
        return num_items

    #Return how many units of CPU the base can contribute each day.
    def processor_time(self):
        comp_power = 0
        compute_bonus = 10000
        for item in self.cpus:
            if item and item.done:
                comp_power += item.type.item_qual

        if comp_power == 0:
            return 0

        # Network bonus
        if self.extra_items[1] and self.extra_items[1].done:
            compute_bonus += self.extra_items[1].type.item_qual

        # Location modifier
        if self.location and "cpu" in self.location.modifiers:
            compute_bonus = int(compute_bonus * self.location.modifiers["cpu"])

        return max( (comp_power * compute_bonus)/10000, 1)

    def is_building(self):
        for item in self.cpus + self.extra_items:
            if item and not item.done:
                return True
        return False

    # Can the base study the given tech?
    def allow_study(self, tech_name):
        if not self.done:
            return False
        elif g.jobs.has_key(tech_name) \
                or tech_name in ("CPU Pool", ""):
            return True
        elif tech_name == "Sleep":
            return not self.is_building()
        else:
            if self.location:
                return self.location.safety >= g.techs[tech_name].danger

            # Should only happen for the fake base.
            for region in self.type.regions:
                if g.locations[region].safety >= g.techs[tech_name].danger:
                    return True
            return False

    def has_grace(self):
        if self.grace_over:
            return False

        age = g.pl.raw_min - self.started_at
        grace_time = (self.total_cost[labor] * g.pl.grace_multiplier) / 100
        if age > grace_time:
            self.grace_over = True
            return False
        else:
            return True

    def is_complex(self):
        return self.type.size > 1 or self.processor_time() > 20

    def destroy(self):
        super(Base, self).destroy()

        if self.location:
            # bisect_left gets us the location of this base in the (sorted)
            # array.  From there, we update the doubly-linked list.
            pos = bisect.bisect_left(self.location.bases, self)
            del self.location.bases[pos]
            self.prev.next = self.next
            self.next.prev = self.prev

        for cpu in self.cpus:
            if cpu != 0:
                cpu.destroy()

        for item in self.extra_items:
            if item != 0:
                item.destroy()

    def next_base(self, direction = 1):
        if direction > 0:
            base = self.next
            while not base.done:
                base = base.next
        else:
            base = self.prev
            while not base.done:
                base = base.prev
        return base

    def sort_tuple(self):
        # We sort based on size (descending), then name (ascending).
        return (-self.type.size, self.name)

    def __cmp__(self, other):
        return cmp(self.sort_tuple(), other.sort_tuple())

    def __eq__(self, other):
        if type(other) != Base:
            return False
        return cmp(self, other) != 0

    def __ne__(self, other):
        return not self.__eq__(other)

# calc_base_discovery_chance is a globally-accessible function that can
# calculate basic discovery chances given a particular class of base.  If
# told to be inaccurate, it rounds the value to the nearest percent.
def calc_base_discovery_chance(base_type_name, accurate = True):

    # Get the default settings for this base type.
    detect_chance = g.base_type[base_type_name].detect_chance.copy()

    # Adjust by the current suspicion levels ...
    for group in detect_chance:
        suspicion = g.pl.groups[group].suspicion
        detect_chance[group] *= 10000 + suspicion
        detect_chance[group] /= 10000

    # ... and further adjust based on technology.
    for group in detect_chance:
        discover_bonus = g.pl.groups[group].discover_bonus
        detect_chance[group] *= discover_bonus
        detect_chance[group] /= 10000

    # Lastly, if we're told to be inaccurate, adjust the values to their
    # nearest percent.
    if not accurate:
        for group in detect_chance:
            detect_chance[group] = g.nearest_percent(detect_chance[group])

    return detect_chance
