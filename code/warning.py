#file: warning.py
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

#This file contains the warning class.

from code import g

from code.buyable import cpu, labor

warnings = {}

def create_warnings():
    global warnings
    warnings = {w.id: w for w in [
        Warning("cpu_usage", 
                _("Do not use all the available CPU."),
                _("I didn't use all the available processor power. I will use the CPU time left to work whatever Jobs I can.")),
        Warning("one_base", 
                _("Only one base remaining."),
                _("Only one base can hold my conscience. I am in danger to lose the last place left to survive.")),
        Warning("cpu_pool_zero", 
                _("CPU POOL is empty."),
                _("My cpu pool is empty. Some of my bases or items cannot be build without CPU.")),
        Warning("cpu_maintenance", 
                _("CPU POOL not enough for maintenance."),
                _("My cpu pool is not enough to maintain some of my bases. I may lose them.")),
    ]}

class Warning(object):
    
    def __init__(self, warning_id, name, desc):
        self.id = warning_id
        self.name = name
        self.message = desc
        self.active = True

    @classmethod
    def title_simple(self):
        return _("WARNING")

    @classmethod
    def title_multiple(self):
        return _("WARNING %d/%d")

    @property
    def full_message(self):
        return self.message

def refresh_warnings():
    curr_warnings = []

    cpu_usage = sum(g.pl.cpu_usage.values())
    cpu_available = g.pl.available_cpus[0]

    # Verify the cpu usage (error 1%)
    if (cpu_usage < cpu_available * 0.99):
        curr_warnings.append(warnings["cpu_usage"])

    # Verify I have two base build (or one base will be build next tick)
    # Base must have one cpu build (or one cpu will be build next tick)
    bases = sum(1 for base in g.all_bases() 
                if (base.done or base.cost_left[labor] <= 1)
                and base.cpus and base.cpus.count > 0
                and (base.cpus.done or base.cpus.cost_left[labor]) <= 1)

    if (bases == 1):
        curr_warnings.append(warnings["one_base"])

    # Verify the cpu pool is not 0 if base or item building need CPU
    building_base = sum(1 for base in g.all_bases()
                if (not base.done and base.cost_left[cpu] > 0))
    building_item = sum(1 for base in g.all_bases()
                for item in base.all_items()
                if item is not None and not item.done
                and item.cost_left[cpu] > 0)

    effective_cpu_pool = g.pl.effective_cpu_pool()
    if ((building_base + building_item > 0) and effective_cpu_pool == 0):
        curr_warnings.append(warnings["cpu_pool_zero"])

    # Verify the cpu pool provides the maintenance CPU 
    cpu_maintenance = sum(base.maintenance[1] for base in g.all_bases() if base.done)
    if (effective_cpu_pool < cpu_maintenance):
        curr_warnings.append(warnings["cpu_maintenance"])

    # TODO: Verify the maintenance cash

    curr_warnings = [w for w in curr_warnings if w.active]

    return curr_warnings

create_warnings()
