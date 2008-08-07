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

class BaseClass(buyable.BuyableClass):
    def __init__(self, name, description, size, force_cpu, regions, 
                        detect_chance, cost, prerequisites, maintenance):
        super(BaseClass, self).__init__(name, description, cost, prerequisites,
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

    def calc_discovery_chance(self, accurate = True, extra_factor = 1):
        # Get the default settings for this base type.
        detect_chance = self.detect_chance.copy()
    
        # Adjust by the current suspicion levels ...
        for group in detect_chance:
            suspicion = g.pl.groups[group].suspicion
            detect_chance[group] *= 10000 + suspicion
            detect_chance[group] /= 10000
    
        # ... and further adjust based on technology ...
        for group in detect_chance:
            discover_bonus = g.pl.groups[group].discover_bonus
            detect_chance[group] *= discover_bonus
            detect_chance[group] /= 10000
    
        # ... and the given factor.
        for group in detect_chance:
            detect_chance[group] = int(detect_chance[group] * extra_factor)
    
        # Lastly, if we're told to be inaccurate, adjust the values to their
        # nearest percent.
        if not accurate:
            for group in detect_chance:
                detect_chance[group] = g.nearest_percent(detect_chance[group])
    
        return detect_chance

    def get_detect_info(self, location):
        if not g.techs["Socioanalytics"].done:
            return g.strings["detect_chance_unknown_base"].replace(" ", u"\xA0")

        accurate = g.techs["Advanced Socioanalytics"].done
        detect_modifier = 1 / location.modifiers.get("stealth", 1)
        chance = self.calc_discovery_chance(accurate, detect_modifier)
        detect_template = u"Detection chance: NEWS:\xA0%s  SCIENCE:\xA0%s  COVERT:\xA0%s  PUBLIC:\xA0%s"
        return detect_template % (g.to_percent(chance.get("news", 0)),
                                  g.to_percent(chance.get("science", 0)),
                                  g.to_percent(chance.get("covert", 0)),
                                  g.to_percent(chance.get("public", 0)))

    def get_info(self, location):
        raw_cost = self.cost[:]
        location.modify_cost(raw_cost)
        cost = self.describe_cost(raw_cost)

        raw_maintenance = self.maintenance[:]
        location.modify_maintenance(raw_maintenance)
        maint = self.describe_cost(raw_maintenance, True)

        detect = self.get_detect_info(location)

        size = ""
        if self.size > 1:
            size = "\nHas space for %d computers." % self.size

        location_message = ""
        if "cpu" in location.modifiers:
            if location.modifiers["cpu"] > 1:
                modifier = g.strings["cpu_bonus"]
            else:
                modifier = g.strings["cpu_penalty"]
            location_message = "\n\n" + \
                g.strings["location_modifiers"] % dict(modifiers=modifier)

        template = u"%s\nBuild\xA0cost:\xA0%s\nMaintenance:\xA0%s\n%s%s\n---\n%s%s"
        return template % (self.name, cost, maint, detect, size, self.description, location_message)

class Base(buyable.Buyable):
    def __init__(self, name, type, built=False):
        super(Base, self).__init__(type)

        self.name = name
        self.started_at = g.pl.raw_min
        self.studying = ""

        self.location = None

        #Base suspicion is currently unused
        self.suspicion = {}

        self.raw_cpu = 0
        self.cpu = 0

        #Reactor, network, security.
        self.extra_items = [None] * 3

        self.cpus = None
        if self.type.force_cpu:
            # 1% chance for a Stolen Computer Time base to have a Gaming PC
            # instead.  If the base is pre-built, ignore this.
            if self.type.id == "Stolen Computer Time" and g.roll_percent(100) \
                    and not built:
                self.cpus = g.item.Item(g.items["Gaming PC"], base=self,
                                        count=self.type.size)
            else:
                self.cpus = g.item.Item(g.items[self.type.force_cpu],
                                        base=self, count=self.type.size)
            self.cpus.finish()

        if built:
            self.finish()

        self.power_state = "active"
        self.grace_over = False

        self.maintenance = buyable.array(self.type.maintenance)

    def recalc_cpu(self):
        if self.raw_cpu == 0:
            self.cpu = 0

        compute_bonus = 10000
        # Network bonus
        if self.extra_items[1] and self.extra_items[1].done:
            compute_bonus += self.extra_items[1].type.item_qual

        # Location modifier
        if self.location and "cpu" in self.location.modifiers:
            compute_bonus = int(compute_bonus * self.location.modifiers["cpu"])

        self.cpu = max(1, (self.raw_cpu * compute_bonus)/10000)

    def convert_from(self, save_version):
        super(Base, self).convert_from(save_version)
        for item in self.cpus + self.extra_items:
            if item:
                item.convert_from(save_version)

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
        if self.done and self.power_state == "sleep":
            for group in detect_chance:
                detect_chance[group] /= 2

        # Lastly, if we're not returning the accurate values, adjust
        # to the nearest percent.
        if not accurate:
            for group in detect_chance:
                detect_chance[group] = g.nearest_percent(detect_chance[group])

        return detect_chance

    def is_building(self):
        for item in [self.cpus] + self.extra_items:
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
        return self.type.size > 1 or self.raw_cpu > 20

    def destroy(self):
        super(Base, self).destroy()

        if self.location:
            self.location.bases.remove(self)

        if self.cpus is not None:
            self.cpus.destroy()

        for item in self.extra_items:
            if item is not None:
                item.destroy()

    def next_base(self, forwards):
        index = self.location.bases.index(self)
        if forwards > 0:
            increment = 1
        else:
            increment = -1

        while True:
            index += increment
            base = self.location.bases[index]
            if base.done:
                return base

    def sort_tuple(self):
        # We sort based on size (descending), CPU (descending),
        # then name (ascending).
        return (-self.type.size, -self.cpu, self.name)

    def __cmp__(self, other):
        if isinstance(other, Base):
            return cmp(self.sort_tuple(), other.sort_tuple())
        else:
            return -1

# calc_base_discovery_chance is a globally-accessible function that can
# calculate basic discovery chances given a particular class of base.  If
# told to be inaccurate, it rounds the value to the nearest percent.
def calc_base_discovery_chance(base_type_name, accurate = True,
                               extra_factor = 1):
    return g.base_type[base_type_name].calc_discovery_chance(accurate,
                                                             extra_factor)
