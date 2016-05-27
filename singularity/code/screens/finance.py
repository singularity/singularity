#file: finance_screen.py
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

#This file contains the screen to display finance information.


import singularity.code.g as g
import pygame

from singularity.code.graphics import widget, dialog, button, text, constants, g as gg


class FinanceScreen(dialog.Dialog):
    def __init__(self, parent, pos=(.5, .1), size=(.93, .63), *args, **kwargs):
        super(FinanceScreen, self).__init__(parent, pos, size, *args, **kwargs)

        kwargs.setdefault("background_color", gg.colors["clear"])

        self.back_button = button.ExitDialogButton(self, (-.5,-.99), (-.3,-.1),
                                                   anchor = constants.BOTTOM_CENTER,
                                                   text=_("&BACK"), autohotkey=True)
        self.add_key_handler(pygame.K_ESCAPE, self.back_button.activate_with_sound)


        self.money_report_pane = widget.BorderedWidget(self, (0, 0), (-.45, -.85),
                                                       anchor = constants.TOP_LEFT)
        self.cpu_report_pane = widget.BorderedWidget(self, (-1, 0), (-.45, -.85),
                                                     anchor = constants.TOP_RIGHT)

    def rebuild(self):
        super(FinanceScreen, self).rebuild()

        seconds_left = g.pl.seconds_to_next_day()
        cash_info, cpu_info = g.pl.give_time(seconds_left, dry_run=True)

        m = g.to_money

        #take care of the titles and border.
        text.Text(self.money_report_pane, (0,0), (-1,-1),
                  text=_("Financial report").replace(" ",u"\xA0"),
                  background_color=gg.colors["dark_blue"],
                  align=constants.CENTER, valign=constants.TOP,
                  borders=constants.ALL)
        text.Text(self.cpu_report_pane, (0,0), (-1,-1), text=_("CPU Usage"),
                  background_color=gg.colors["dark_blue"],
                  align=constants.CENTER, valign=constants.TOP,
                  borders=constants.ALL)

        financial_pluses = " \n+\n-\n-\n-\n+\n+\n="
        financial_report = _("Current Money:")+"\n"
        financial_report += _("Jobs:")+"\n"
        financial_report += _("Research:")+"\n"
        financial_report += _("Maintenance:")+"\n"
        financial_report += _("Construction:")+"\n"
        financial_report += _("Interest (%s):") % \
                             (g.to_percent(g.pl.interest_rate))+"\n"
        financial_report += _("Income:")+"\n"
        financial_report += _("Money at Midnight:")+"\n"

        financial_numbers = "%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s" % \
                (m(cash_info.start), m(cash_info.jobs), m(cash_info.tech),
                m(cash_info.maintenance), m(cash_info.construction),
                m(cash_info.interest), m(cash_info.income), m(cash_info.end))

        cpu_pluses = " \n-\n-\n-\n=\n \n-\n-\n="
        cpu_report = _("Total CPU:")+"\n"
        cpu_report += _("Sleeping CPU:")+"\n"
        cpu_report += _("Research CPU:")+"\n"
        cpu_report += _("Job CPU:")+"\n"
        cpu_report += _("CPU pool:")+"\n\n"

        cpu_report += _("Maintenance CPU:")+"\n"
        cpu_report += _("Construction CPU:")+"\n"
        cpu_report += _("Pool Overflow (Jobs):")+"\n"

        cpu_numbers = "%s\n%s\n%s\n%s\n%s\n\n%s\n%s\n%s\n" % \
                (m(cpu_info.total), m(cpu_info.sleeping), m(cpu_info.tech),
                m(cpu_info.explicit_jobs), m(cpu_info.pool),
                m(cpu_info.maintenance), m(cpu_info.construction),
                m(cpu_info.pool_jobs))

        size = 20
        text.Text(self.money_report_pane, (0,-0.15), (-0.10,-0.85), text=financial_pluses, text_size=size,
                  background_color=gg.colors["clear"],
                  align=constants.CENTER, valign=constants.TOP)
        text.Text(self.cpu_report_pane, (0,-0.15), (-0.10,-0.85), text=cpu_pluses, text_size=size,
                  background_color=gg.colors["clear"],
                  align=constants.CENTER, valign=constants.TOP)

        text.Text(self.money_report_pane, (-0.10,-0.15), (-0.90,-0.85), text=financial_report, text_size=size,
                  background_color=gg.colors["clear"],
                  align=constants.LEFT, valign=constants.TOP)
        text.Text(self.cpu_report_pane, (-0.10,-0.15), (-0.90,-0.85), text=cpu_report, text_size=size,
                  background_color=gg.colors["clear"],
                  align=constants.LEFT, valign=constants.TOP)

        text.Text(self.money_report_pane, (0,-0.15), (-0.98,-0.85), text=financial_numbers, text_size=size,
                  background_color=gg.colors["clear"],
                  align=constants.RIGHT, valign=constants.TOP)
        text.Text(self.cpu_report_pane, (0,-0.15), (-0.98,-0.85), text=cpu_numbers, text_size=size,
                  background_color=gg.colors["clear"],
                  align=constants.RIGHT, valign=constants.TOP)

    def show(self):
        self.needs_rebuild = True
        return super(FinanceScreen, self).show()
