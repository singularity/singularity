#file: location.py
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

#This file is used to display the log of player action

from __future__ import absolute_import


from singularity.code import g, logmessage
from singularity.code.graphics import dialog, constants, text, button, listbox


filtered_log_class = set()


class LogScreen(dialog.ChoiceDialog):
    def __init__(self, parent, pos=(.5, .5), size=(.73, .63), *args, **kwargs):
        super(LogScreen, self).__init__(parent, pos, size, *args, **kwargs)
        self.key_list = []
        self.anchor = constants.MID_CENTER

        self.yes_button.parent = None
        self.no_button.pos = (-.5,-.99)
        self.no_button.anchor = constants.BOTTOM_CENTER

        self.filter_log_dialog = FilterLogDialog(self)

        self.filter_log = button.FunctionButton(self, (-1.0, 0.), (-.18, -.08),
                                                autotranslate=True,
                                                text=N_("Filters"),
                                                anchor=constants.TOP_RIGHT,
                                                function=self.show_filters)

    def make_listbox(self):
        return listbox.Listbox(self, (0, -.09), (-1, -.77),
                               list_item_height=0.04, list_item_shrink=1,
                               anchor=constants.TOP_LEFT, align=constants.LEFT,
                               on_double_click_on_item=self.handle_double_click,
                               item_borders=False, item_selectable=True)

    def handle_double_click(self, event):
        if self.listbox.is_over(event.pos) and 0 <= self.listbox.list_pos < len(self.key_list):
            message = self.key_list[self.listbox.list_pos]
            # use the MapScreen (our parent) as parent for the dialog to match
            # how it is originally shown (plus to avoid "cannot fit" warnings
            # when the dialog is larger than the log screen)
            message_dialog = dialog.MessageDialog(self.parent, text_size=20)
            message_dialog.text = message.full_message
            message_dialog.color = message.full_message_color

            # Because we need to use the MapScreen as parent, we need to juggle
            # things manually (as call_dialog works with a different assumption
            # than we need).
            try:
                self.visible = False
                dialog.call_dialog(message_dialog, self.parent)
            finally:
                self.visible = True
                self.needs_rebuild = True
                self.parent.needs_rebuild = True
                self.parent.lost_focus()
                self.regained_focus()

    def rebuild(self):
        self.key_list = [message for message in g.pl.log if not type(message) in filtered_log_class]
        self.list = [self.render_log_message(message) for message in self.key_list]
        self.default = len(self.list) - 1

        self.filter_log_dialog.needs_rebuild = True

        super(LogScreen, self).rebuild()

    def show(self):
        self.listbox.has_focus = True
        return super(LogScreen, self).show()

    def show_filters(self):
        dialog.call_dialog(self.filter_log_dialog, self)
        self.needs_rebuild = True

    def render_log_message(self, message):
        log_emit_time = message.log_emit_time
        log_message = message.log_line
        return "%s -- %s" % (_("DAY") + " %04d, %02d:%02d:%02d" % log_emit_time, log_message)

class FilterLogDialog(dialog.MessageDialog):
    def __init__(self, parent, *args, **kwargs):
        kwargs["ok_type"] = N_("&BACK")
        super(FilterLogDialog, self).__init__(parent, *args, **kwargs)

        self.log_class_labels = {}
        self.log_class_toggles = {}

        for i, (log_type, log_class) in enumerate(logmessage.SAVEABLE_LOG_MESSAGES.items()):
            y = .01 + i * .06

            self.log_class_labels[log_type] = text.Text(self, (-.01, y), (-.70, .05),
                                                        align = constants.LEFT,
                                                        background_color="clear")
            self.log_class_toggles[log_type] = FilterButton(self, (-.71, y), (-.28, .05),
                                                            autotranslate=True,
                                                            autohotkey=False,
                                                            on_text=N_('SHOW'),
                                                            off_text=N_('HIDE'),
                                                            text_shrink_factor=.75,
                                                            force_underline=-1,
                                                            function=self.toggle_log_class,
                                                            args=(button.TOGGLE_VALUE, log_class))

        self.pos = (-.50, 0)
        self.size = (-.50, (y + .07) / .9)
        self.anchor = constants.TOP_LEFT

    def rebuild(self):
        for log_type, log_class in logmessage.SAVEABLE_LOG_MESSAGES.items():
            self.log_class_labels[log_type].text = log_class.log_name()
            self.log_class_toggles[log_type].active = log_class not in filtered_log_class

        super(FilterLogDialog, self).rebuild()

    def toggle_log_class(self, value, log_class):
        if value:
            filtered_log_class.remove(log_class)
        else:
            filtered_log_class.add(log_class)


class FilterButton(button.StickyOnOffButton, button.FunctionButton):
    pass
