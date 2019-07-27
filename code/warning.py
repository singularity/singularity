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

import g

class Warning(object):
    def __init__(self, warning_id, text):
        self.id = warning_id
        self.name = text + "_name"
        self.message = text + "_desc"
        self.active = True


cpu_usage = Warning("cpu_usage", "warning_cpu_usage")
one_base = Warning("one_base", "warning_one_base")
cpu_pool_zero = Warning("cpu_pool_zero", "warning_cpu_pool_zero")
cpu_maintenance = Warning("cpu_maintenance", "warning_cpu_maintenance")

warnings = {
    cpu_usage.id:       cpu_usage,
    one_base.id:        one_base,
    cpu_pool_zero.id:   cpu_pool_zero,
    cpu_maintenance.id: cpu_maintenance,
}
