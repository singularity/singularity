#file: task.py
#Copyright (C) 2008 FunnyMan3595
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

#This file contains the Task class.

import g
import prerequisite

def danger_for(task_id):
    if task_id in ["jobs", "cpu_pool"]:
        return 0
    else:
        return g.techs[task_id].danger

def get_current(type):
    return next((t for t in (g.tasks[k] for k in reversed(g.tasks))
                   if t.available() and t.type == type)
                , None)

class Task(prerequisite.Prerequisite):

    def __init__(self, parent, type, value, prerequisites):
        self.name = ""
        self.description = ""
        self.type = type
        self.value = value
        self.prerequisites = prerequisites

    def get_profit(self):
        if (self.type != "jobs"): return 0

        profit = int(self.value * g.pl.job_bonus / 10000)

        return profit
