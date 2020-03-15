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
        self.anchor = constants.MID_CENTER

        self.yes_button.parent = None
        self.no_button.pos = (-.5,-.99)
        self.no_button.anchor = constants.BOTTOM_CENTER
        
        self.filter_log_dialog = FilterLogDialog(self)
        
        self.filter_log = button.FunctionButton(self, (-1., 0.), (-.15, -.08),
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
            message_dialog = dialog.MessageDialog(self, text_size=20)
            message_dialog.text = message.full_message
            message_dialog.color = message.full_message_color
            dialog.call_dialog(message_dialog, self)

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
        super(FilterLogDialog, self).__init__(parent, *args, **kwargs)
        
        self.ok_type = "back"
        
        self.log_class_labels = {}
        self.log_class_toggles = {}
        
        for i, (log_type, log_class) in enumerate(logmessage.SAVEABLE_LOG_MESSAGES.items()):
            y = .01 + i * .06
            
            self.log_class_labels[log_type] = text.Text(self, (-.01, y), (-.70, .05),
                                                        align = constants.LEFT,
                                                        background_color="clear")
            self.log_class_toggles[log_type] = FilterButton(self, (-.71, y), (-.28, .05),
                                                            text_shrink_factor=.75,
                                                            force_underline=-1,
                                                            function=self.toggle_log_class,
                                                            args=(button.WIDGET_SELF, button.TOGGLE_VALUE, log_class))

        self.pos = (-.50, 0)
        self.size = (-.50, (y + .07) / .9)
        self.anchor = constants.TOP_LEFT

    def rebuild(self):
        for log_type, log_class in logmessage.SAVEABLE_LOG_MESSAGES.items():
            self.log_class_labels[log_type].text = log_class.log_name()
            
            if not log_class in filtered_log_class:
                self.log_class_toggles[log_type].text = _("SHOW")
                self.log_class_toggles[log_type].set_active(True)
            else:
                self.log_class_toggles[log_type].text = _("HIDE")
                self.log_class_toggles[log_type].set_active(False)

        super(FilterLogDialog, self).rebuild()

    def toggle_log_class(self, widget, value, log_class):
        if value:
            widget.text = _("SHOW")
        else:
            widget.text = _("HIDE")

        if value:
            filtered_log_class.remove(log_class)
        else:
            filtered_log_class.add(log_class)

class FilterButton(button.ToggleButton, button.FunctionButton):
    pass
