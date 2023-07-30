# file: report_screen.py
# Copyright (C) 2005,2006,2008 Evil Mr Henry, Phil Bordelon, and FunnyMan3595
# This file is part of Endgame: Singularity.

# Endgame: Singularity is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# Endgame: Singularity is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Endgame: Singularity; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

# This file contains the screen to display information report.

from __future__ import absolute_import

import singularity.code.g as g
import pygame

from singularity.code.graphics import widget, dialog, button, text, constants
from singularity.code.screens import stat


class ReportScreen(dialog.Dialog):
    def __init__(self, parent, pos=(0.5, 0.1), size=(0.93, 0.73), *args, **kwargs):
        super(ReportScreen, self).__init__(parent, pos, size, *args, **kwargs)

        kwargs.setdefault("background_color", "clear")

        self.format_buttons = button.ButtonGroup()

        self.stats_button = button.DialogButton(
            self,
            (-0.49, -0.99),
            (-0.3, -0.1),
            autotranslate=True,
            text=N_("&STATISTICS"),
            anchor=constants.BOTTOM_RIGHT,
            dialog=stat.StatScreen(self),
        )
        self.back_button = button.ExitDialogButton(
            self,
            (-0.51, -0.99),
            (-0.3, -0.1),
            autotranslate=True,
            text=N_("&BACK"),
            anchor=constants.BOTTOM_LEFT,
        )
        self.add_key_handler(pygame.K_ESCAPE, self.back_button.activate_with_sound)

        self.money_report_pane = widget.BorderedWidget(
            self, (0, 0.08), (-0.50, -0.72), anchor=constants.TOP_LEFT
        )
        self.cpu_report_pane = widget.BorderedWidget(
            self, (-1, 0.08), (-0.50, -0.72), anchor=constants.TOP_RIGHT
        )

        self.format_button_midnight = FormatButton(
            self,
            (-0.5, 0),
            (-0.15, -0.08),
            autotranslate=True,
            text=N_("&Midnight"),
            anchor=constants.TOP_RIGHT,
            function=self.format_toggle,
        )
        self.format_button_midnight.args = (self.format_button_midnight, True)
        self.format_buttons.add(self.format_button_midnight)

        self.format_button_24hours = FormatButton(
            self,
            (-0.5, 0),
            (-0.15, -0.08),
            autotranslate=True,
            text=N_("24 &Hours"),
            anchor=constants.TOP_LEFT,
            function=self.format_toggle,
        )
        self.format_button_24hours.args = (self.format_button_24hours, False)
        self.format_buttons.add(self.format_button_24hours)

        self.format_button_midnight.chosen_one()
        self.midnight_stop = True

    def rebuild(self):
        super(ReportScreen, self).rebuild()

        if self.midnight_stop:
            seconds = g.seconds_per_day - (g.pl.raw_sec % g.seconds_per_day)
        else:
            seconds = g.seconds_per_day

        cash_info, cpu_info = g.pl.compute_future_resource_flow(seconds)

        m = g.to_money

        # take care of the titles and border.
        text.Text(
            self.money_report_pane,
            (0, 0),
            (-1, -1),
            text=_("Financial report").replace(" ", "\xA0"),
            background_color="pane_background",
            align=constants.CENTER,
            valign=constants.TOP,
            borders=constants.ALL,
        )
        text.Text(
            self.cpu_report_pane,
            (0, 0),
            (-1, -1),
            text=_("CPU Usage"),
            background_color="pane_background",
            align=constants.CENTER,
            valign=constants.TOP,
            borders=constants.ALL,
        )

        financial_pluses = " \n+\n-\n-\n-\n+\n+\n="
        financial_report = _("Current Money flow") + "\n"
        financial_report += _("Jobs:") + "\n"
        financial_report += _("Research:") + "\n"
        financial_report += _("Maintenance:") + "\n"
        financial_report += _("Construction:") + "\n"
        financial_report += (
            _("Interest (%s):") % (g.to_percent(g.pl.interest_rate)) + "\n"
        )
        financial_report += _("Income:") + "\n"

        if self.midnight_stop:
            financial_report += _("Money flow until Midnight:") + "\n"
        else:
            financial_report += _("Money flow for 24 hours:") + "\n"

        financial_numbers = "\n%s\n%s\n%s\n%s\n%s\n%s\n%s" % (
            m(cash_info.jobs),
            m(cash_info.tech),
            m(cash_info.maintenance_needed),
            m(cash_info.construction_needed),
            m(cash_info.interest),
            m(cash_info.income),
            m(cash_info.difference),
        )

        cpu_pluses = " \n-\n-\n-\n=\n \n-\n-\n="
        cpu_report = _("Total CPU:") + "\n"
        cpu_report += _("Sleeping CPU:") + "\n"
        cpu_report += _("Research CPU:") + "\n"
        cpu_report += _("Job CPU:") + "\n"
        cpu_report += _("CPU pool:") + "\n\n"

        cpu_report += _("Maintenance CPU:") + "\n"
        cpu_report += _("Construction CPU:") + "\n"
        cpu_report += _("Pool difference:") + "\n"

        cpu_numbers = "%s\n%s\n%s\n%s\n%s\n\n%s\n%s\n%s\n" % (
            m(cpu_info.total),
            m(cpu_info.sleeping),
            m(cpu_info.tech),
            m(cpu_info.explicit_jobs),
            m(cpu_info.effective_pool),
            m(cpu_info.maintenance_needed),
            m(cpu_info.construction_needed),
            m(cpu_info.difference),
        )

        size = "report_content"
        text.Text(
            self.money_report_pane,
            (0, -0.15),
            (-0.10, -0.85),
            text=financial_pluses,
            text_size=size,
            background_color="clear",
            align=constants.CENTER,
            valign=constants.TOP,
        )
        text.Text(
            self.cpu_report_pane,
            (0, -0.15),
            (-0.10, -0.85),
            text=cpu_pluses,
            text_size=size,
            background_color="clear",
            align=constants.CENTER,
            valign=constants.TOP,
        )

        text.Text(
            self.money_report_pane,
            (-0.10, -0.15),
            (-0.90, -0.85),
            text=financial_report,
            text_size=size,
            background_color="clear",
            align=constants.LEFT,
            valign=constants.TOP,
        )
        text.Text(
            self.cpu_report_pane,
            (-0.10, -0.15),
            (-0.90, -0.85),
            text=cpu_report,
            text_size=size,
            background_color="clear",
            align=constants.LEFT,
            valign=constants.TOP,
        )

        text.Text(
            self.money_report_pane,
            (0, -0.15),
            (-0.98, -0.85),
            text=financial_numbers,
            text_size=size,
            background_color="clear",
            align=constants.RIGHT,
            valign=constants.TOP,
        )
        text.Text(
            self.cpu_report_pane,
            (0, -0.15),
            (-0.98, -0.85),
            text=cpu_numbers,
            text_size=size,
            background_color="clear",
            align=constants.RIGHT,
            valign=constants.TOP,
        )

    def format_toggle(self, button, midnight_stop):
        self.midnight_stop = midnight_stop
        button.chosen_one()
        self.needs_rebuild = True


class FormatButton(button.ToggleButton, button.FunctionButton):
    pass
