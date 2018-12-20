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


import g
import buyable
from buyable import cash, cpu, labor


#TODO: Use this list and convert Base.power_state to a property to enforce this
#TODO: Consider converting to dict, so it can have colors and names and modifiers
#      (Base.power_state would need to be a property, with setter and getter)
#This list only applies to 'Base' class, not 'BaseClass'
#Changes to this list should also be reflected in Base.power_state_name property
power_states = ['active','sleep']
#power_states.extend(['overclocked','suicide','stasis','entering_stasis','leaving_stasis'])


class BaseClass(buyable.BuyableClass):
    """Base as a buyable item (New Base in Location menu)"""

    def __init__(self, name, description, size, force_cpu, regions,
                        detect_chance, cost, prerequisites, maintenance):
        super(BaseClass, self).__init__(name, description, cost, prerequisites,
                                         type="base")
        self.size = size
        self.force_cpu = force_cpu
        self.regions = regions

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
        if g.pl.display_discover == "none":
            return g.strings["detect_chance_unknown_base"].replace(" ", u"\xA0")

        accurate = bool(g.pl.display_discover == "full")
        detect_modifier = 1 / location.modifiers.get("stealth", 1)
        chance = self.calc_discovery_chance(accurate, detect_modifier)
        detect_template = _("Detection chance:") + "\n" + \
                          _("NEWS")    + u":\xA0%s\n"   + \
                          _("SCIENCE") + u":\xA0%s\n"   + \
                          _("COVERT")  + u":\xA0%s\n"   + \
                          _("PUBLIC")  + u":\xA0%s"
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
        # describe_cost() expects CPU-seconds, not CPU-days
        raw_maintenance[cpu] *= g.seconds_per_day
        maint = self.describe_cost(raw_maintenance, True)

        detect = self.get_detect_info(location)

        size = ""
        if self.size > 1:
            size = "\n" + _("Has space for %d computers.") % self.size

        location_message = ""
        if "cpu" in location.modifiers:
            if location.modifiers["cpu"] > 1:
                modifier = g.strings["cpu_bonus"]
            else:
                modifier = g.strings["cpu_penalty"]
            location_message = "\n\n" + \
                g.strings["location_modifiers"] % dict(modifiers=modifier)

        template = "%s\n" + _("Build cost:").replace(" ",u"\xA0") + u"\xA0%s\n" + \
                   _("Maintenance:") + u"\xA0%s\n%s%s\n---\n%s%s"
        return template % (self.name, cost, maint, detect, size, self.description, location_message)

class Base(buyable.Buyable):
    """A Player's Base in a Location (Open Base in Location menu)"""

    def __init__(self, name, type, built=False):
        super(Base, self).__init__(type)

        self.name = name
        self.started_at = g.pl.raw_min

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

        self.maintenance = buyable.array(self.type.maintenance, long)

    @property
    def power_state_name(self):
        """A read-only i18'zable version of power_state attribute, suitable for
        printing labels, captions, etc"""
        if self.power_state == "active"         : return _("Active")
        if self.power_state == "sleep"          : return _("Sleep")
        if self.power_state == "overclocked"    : return _("Overclocked")
        if self.power_state == "suicide"        : return _("Suicide")
        if self.power_state == "stasis"         : return _("Stasis")
        if self.power_state == "entering_stasis": return _("Entering Stasis")
        if self.power_state == "leaving_stasis" : return _("Leaving Stasis")
        return ""

    def space_left_for(self, item_type):
        space_left = self.type.size

        # Different cpus will replace the previous one, so these take full space.
        if self.cpus is not None \
                and self.cpus.type == item_type:
            space_left -= self.cpus.count
            
        return space_left

    def check_power(self):
        if self.power_state == "sleep":
            if self.done:
                for item in [self.cpus,] + self.extra_items:
                    if item is not None and not item.done:
                        self.power_state = "active"
            else:
                self.power_state = "active"

    def recalc_cpu(self):
        if self.raw_cpu == 0:
            self.cpu = 0
            return

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
        if save_version < 4.91: # < r5_pre
            for cpu in self.cpus:
                if cpu:
                    cpu.convert_from(save_version)
                    cpu.base = self
            for index in range(len(self.extra_items)):
                if self.extra_items[index]:
                    self.extra_items[index].convert_from(save_version)
                else:
                    self.extra_items[index] = None

            self.raw_cpu = 0
            if self.cpus[0]:
                for cpu in self.cpus[1:]:
                    self.cpus[0] += cpu

                if len(self.cpus) == 1 and self.cpus[0].done:
                    # Force it to report its CPU.
                    self.cpus[0].finish()

                self.cpus = self.cpus[0]
            else:
                self.cpus = None

            self.recalc_cpu()

            self.power_state = self.power_state.lower()

            # Update CPU usage.
            if self.studying in g.techs:
                g.pl.cpu_usage[self.studying] = \
                    g.pl.cpu_usage.get(self.studying, 0) + self.cpu
            elif "Jobs" in self.studying:
                g.pl.cpu_usage["jobs"] = \
                    g.pl.cpu_usage.get("jobs", 0) + self.cpu
            elif self.studying == "CPU Pool":
                g.pl.cpu_usage["cpu_pool"] = \
                    g.pl.cpu_usage.get("cpu_pool", 0) + self.cpu

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
        grace_time = (self.total_cost[buyable.labor] * g.pl.grace_multiplier) / 10000
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
            index %= len(self.location.bases)
            base = self.location.bases[index]
            if base.done:
                return base

    def sort_tuple(self):
        # We sort based on size (descending), CPU (descending),
        # then name (ascending).
        # id(self) is thrown in at the end to make sure identical-looking
        # bases aren't considered equal.
        return (-self.type.size, -self.cpu, self.name, id(self))

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
