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

from code import g, warning
from code.graphics import g as gg
from code.graphics import dialog, constants, text, button

from code.buyable import cash, cpu, labor

class WarningDialogs(object):

    def __init__(self, screen):
        self.screen = screen
        self.warning_dialog = WarningDialog(screen,
                                            yes_type="continue",
                                            no_type="back")

    def show_dialog(self):
        warnings = self.refresh_warnings()

        if (len(warnings) == 0):
            return

        self.warning_dialog.warnings = warnings
        ret = dialog.call_dialog(self.warning_dialog, self.screen)

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
            warnings.append(warning.cpu_usage)

        # Verify I have two base build (or one base will be build next tick)
        # Base must have one cpu build (or one cpu will be build next tick)
        bases = sum(1 for base in g.all_bases() 
                    if (base.done or base.cost_left[labor] <= 1)
                    and base.cpus and base.cpus.count > 0
                    and (base.cpus.done or base.cpus.cost_left[labor]) <= 1)

        if (bases == 1):
            warnings.append(warning.one_base)

        # Verify the cpu pool is not 0 if base or item building need CPU
        building_base = sum(1 for base in g.all_bases()
                    if (not base.done and base.cost_left[cpu] > 0))
        building_item = sum(1 for base in g.all_bases()
                    for item in base.all_items()
                    if item is not None and not item.done
                    and item.cost_left[cpu] > 0)
        if ((building_base + building_item > 0) and g.pl.cpu_usage.get("cpu_pool", 0) == 0):
            warnings.append(warning.cpu_pool_zero)

        # Verify the cpu pool provides the maintenance CPU 
        cpu_maintenance = sum(base.maintenance[1] for base in g.all_bases() if base.done)
        if (g.pl.cpu_usage.get("cpu_pool", 0) < cpu_maintenance):
            warnings.append(warning.cpu_maintenance)

        # TODO: Verify the maintenance cash

        warnings = [w for w in warnings if w.active]

        return warnings

class WarningDialog(dialog.YesNoDialog):

    def __init__(self, *args, **kwargs):
        super(WarningDialog, self).__init__(*args, **kwargs)
        
        self.title = text.Text(self, (-.01, -.01), (-.98, -.1),
                               background_color="clear",
                               anchor=constants.TOP_LEFT,
                               valign=constants.MID, align=constants.LEFT,
                               base_font="special", text_size=28)

        self.body = text.Text(self, (-.01, -.11), (-.98, -.83),
                               background_color="clear",
                               anchor=constants.TOP_LEFT,
                               valign=constants.TOP, align=constants.LEFT,
                               text_size=20)

        self.prev_button = button.FunctionButton(self, (-.78, -.01), (-.2, -.1),
                                                 text=_("&PREV"), autohotkey=True,
                                                 anchor=constants.TOP_RIGHT,
                                                 text_size=28,
                                                 function=self.prev_warning)   

        self.next_button = button.FunctionButton(self, (-.99, -.01), (-.2, -.1),
                                                 text=_("&NEXT"), autohotkey=True,
                                                 anchor=constants.TOP_RIGHT,
                                                 text_size=28,
                                                 function=self.next_warning)            
                               
        # TODO: Add button "Do not show this message again"

    def rebuild(self):
        super(WarningDialog, self).rebuild()

        if (len(self.warnings) == 1):
            self.title.text = _("WARNING")
            self.body.text = g.strings[self.warnings[0].message]
            self.prev_button.visible = False
            self.next_button.visible = False
        else:
            self.title.text = _("WARNING %d/%d") % (self.warning_nb + 1, len(self.warnings))
            self.body.text = g.strings[self.warnings[self.warning_nb].message]
            self.prev_button.visible = True
            self.next_button.visible = True
            

    def prev_warning(self):
        self.warning_nb = max(self.warning_nb - 1, 0)
        self.needs_rebuild = True

    def next_warning(self):
        self.warning_nb = min(self.warning_nb + 1, len(self.warnings) - 1)
        self.needs_rebuild = True
        
    def show(self):
        self.warning_nb = 0
        self.needs_rebuild = True
        return super(WarningDialog, self).show()



