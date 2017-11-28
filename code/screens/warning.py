#file: warning.py
#Copyright (C) 2005,2006,2008 Evil Mr Henry, Phil Bordelon, FunnyMan3595,
#and Anne M. Archibald.
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

#This file is used to display warning.

from code import g
from code.graphics import g as gg
from code.graphics import dialog, constants

from code.buyable import labor

class WarningDialogs(object):

    def __init__(self, screen):
        self.screen = screen
        self.simple_warning_dialog = dialog.YesNoDialog(screen,
                                                        text_size=20,
                                                        yes_type="continue",
                                                        no_type="back")

    def show_dialog(self):
        warnings = self.refresh_warnings()

        if (len(warnings) == 0):
            return

        self.simple_warning_dialog.text = g.strings[warnings[0].message]
        ret = dialog.call_dialog(self.simple_warning_dialog, self.screen)

        # Pause game
        if (not ret):
            g.pl.pause_game()
            return True

        # Continue
        return False

    def refresh_warnings(self):
        warnings = []

        cpu_usage = sum(g.pl.cpu_usage.values())
        cpu_available = g.pl.available_cpus[0]

        # Verify the cpu usage (error 1%)
        if (cpu_usage < cpu_available * 0.99):
            warnings.append(Warning("warning_cpu_usage"))

        # Verify I have two base build (or one base will be build next tick)
        # Base must have one cpu build (or one cpu will be build next tick)
        bases = sum(1 for base in g.all_bases() 
                    if (base.done or base.cost_left[labor] <= 1)
                    and base.cpus and base.cpus.count > 0
                    and (base.cpus.done or base.cpus.cost_left[labor]) <= 1)

        if (bases == 1):
            warnings.append(Warning("warning_one_base"))

        return warnings

class Warning(object):
    def __init__(self, message):
        self.message = message

