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

from __future__ import absolute_import

from code import g, prerequisite, tech


current_task_cache = {}


@tech.register_on_tech_reset_handler
@tech.register_on_tech_researched_handler
def _clear_current_task_cache(*args, **kwargs):
    current_task_cache.clear()


def tasks_reset():
    _clear_current_task_cache()


def danger_for(task_id):
    if task_id in ["jobs", "cpu_pool"]:
        return 0
    else:
        return g.pl.techs[task_id].danger


def get_current(task_type):
    try:
        return current_task_cache[task_type]
    except KeyError:
        pass
    for t in reversed(g.tasks_by_type[task_type]):
        if t.available():
            current_task_cache[task_type] = t
            return t
    current_task_cache[task_type] = None
    return None


class Task(prerequisite.Prerequisite):

    def __init__(self, id, type, value, prerequisites):
        super(Task, self).__init__(prerequisites)
        self.id = id
        self.name = id
        self.description = ""
        self.type = type
        self.value = value

    def get_profit(self):
        if (self.type != "jobs"): return 0

        profit = int((self.value * g.pl.job_bonus) // 10000)

        return profit
