#file: base_screen.py
#Copyright (C) 2005,2006,2007,2008 Evil Mr Henry, Phil Bordelon, Brian Reid,
#                        and FunnyMan3595
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

#This file contains the screen to display the base screen.

import locale
import pygame

from code import g, item
from code.graphics import g as gg, constants, widget, dialog, text, button, listbox, slider

state_colors = dict(
    active          = "base_state_active",
    sleep           = "base_state_sleep",
    overclocked     = "base_state_overclocked",
    suicide         = "base_state_suicide",
    stasis          = "base_state_stasis",
    entering_stasis = "base_state_entering_stasis",
    leaving_stasis  = "base_state_leaving_stasis",
)
class BuildDialog(dialog.ChoiceDescriptionDialog):
    type = widget.causes_rebuild("_type")
    def __init__(self, parent, pos=(0, 0), size=(-1, -1),
                 anchor=constants.TOP_LEFT, *args, **kwargs):
        super(BuildDialog, self).__init__(parent, pos, size, anchor, *args,
                                          **kwargs)

        self.type = None
        self.desc_func = self.on_change

    def show(self):
        self.list = []
        self.key_list = []

        item_list = g.items.values()
        item_list.sort()
        item_list.reverse()
        for item in item_list:
            if item.item_type.id == self.type.id and item.available() \
                    and item.buildable_in(self.parent.base.location):
                self.list.append(item.name)
                self.key_list.append(item)

        current = self.parent.get_current(self.type)
        if current is None:
            self.default = None
        else:
            self.default = self.parent.get_current(self.type).type.id

        self.needs_rebuild = True
        return super(BuildDialog, self).show()

    def on_change(self, description_pane, item):
        if item is not None:
            text.Text(description_pane, (0, 0), (-1, -1), text=item.get_info(),
                      background_color="pane_background",
                      align=constants.LEFT, valign=constants.TOP,
                      borders=constants.ALL)
        else:
            text.Text(description_pane, (0, 0), (-1, -1), text="",
                      background_color="pane_background",
                      align=constants.LEFT, valign=constants.TOP,
                      borders=constants.ALL)


class MultipleBuildDialog(BuildDialog):
    def __init__(self, parent, *args, **kwargs):
        super(MultipleBuildDialog, self).__init__(parent, *args, **kwargs)

        self.listbox.size = (-.53, -.75)
        self.description_pane.size = (-.45, -.75)

        self.count_label = text.Text(self, (.01, -.87), (-.25, -.1),
                                     anchor=constants.BOTTOM_LEFT, valign=constants.MID,
                                     borders=(constants.TOP, constants.BOTTOM, constants.LEFT),
                                     shrink_factor=.88,
                                     background_color="pane_background",
                                     text=g.strings["number_of_items"])

        self.count_field = text.UpdateEditableText(self, (-.26, -.87), (-.10, -.1),
                                             anchor=constants.BOTTOM_LEFT,
                                             borders=constants.ALL,
                                             update_func=self.on_field_change,
                                             base_font="normal")

        self.count_slider = slider.UpdateSlider(self, (-.37, -.87), (-.62, -.1),
                                                anchor=constants.BOTTOM_LEFT,
                                                horizontal=True, priority=150,
                                                update_func=self.on_slider_change,
                                                slider_size=2)
    @property
    def count(self):
        return self.count_field.text

    def on_change(self, description_pane, item):
        super(MultipleBuildDialog, self).on_change(description_pane, item)

        space_left = self.parent.base.space_left_for(item)
        
        self.count_slider.slider_size = space_left // 10 + 1
        self.count_slider.slider_max = space_left

        self.count_slider.slider_pos = 0
        if (space_left > 0):
            self.count_slider.slider_pos = 1

    def on_field_change(self, value):
        if (not hasattr(self, "count_field") or not hasattr(self, "count_slider")): 
            return # Not initialized
        
        try:
            self.count_slider.slider_pos = int(self.count_field.text)
        except ValueError:
            self.count_slider.slider_pos = 0


    def on_slider_change(self, value):
        if (not hasattr(self, "count_field") or not hasattr(self, "count_slider")): 
            return # Not initialized
        
        self.count_field.text = str(self.count_slider.slider_pos)


class ItemPane(widget.BorderedWidget):
    type = widget.causes_rebuild("_type")
    def __init__(self, parent, pos, size=(.48, .06), anchor=constants.TOP_LEFT,
                 type=None, **kwargs):

        kwargs.setdefault("background_color", "pane_background")

        super(ItemPane, self).__init__(parent, pos, size, anchor=anchor, **kwargs)

        if type is None or not isinstance(type, item.ItemType):
            raise ValueError('Type must be of class ItemType.')

        self.type = type

        self.name_panel = text.Text(self, (0,0), (.35, .03),
                                    anchor=constants.TOP_LEFT,
                                    align=constants.LEFT,
                                    background_color=self.background_color,
                                    bold=True)

        self.build_panel = text.Text(self, (0,.03), (.35, .03),
                                     anchor=constants.TOP_LEFT,
                                     align=constants.LEFT,
                                     background_color=self.background_color,
                                     text="", bold=True)

        self.change_button = button.FunctionButton(
            self, (.36,.01), (.12, .04),
            anchor=constants.TOP_LEFT,
            text="%s (&%s)" % (_("CHANGE"), self.type.hotkey.upper()),
            force_underline=len(_("CHANGE")) + 2,
            autohotkey=True,
            function=self.parent.parent.build_item,
            kwargs={'type': self.type},
        )

class BaseScreen(dialog.Dialog):
    base = widget.causes_rebuild("_base")
    def __init__(self, *args, **kwargs):
        if len(args) < 3:
            kwargs.setdefault("size", (.75, .5))
        base = kwargs.pop("base", None)
        super(BaseScreen, self).__init__(*args, **kwargs)

        self.base = base

        self.build_dialog = BuildDialog(self)
        self.multiple_build_dialog = MultipleBuildDialog(self)

        self.header = widget.Widget(self, (0,0), (-1, .08),
                                    anchor=constants.TOP_LEFT)

        self.name_display = text.Text(self.header, (-.5,0), (-1, -.5),
                                      anchor=constants.TOP_CENTER,
                                      borders=constants.ALL,
                                      border_color="pane_background",
                                      background_color="pane_background_empty",
                                      shrink_factor=.85, bold=True)

        self.next_base_button = \
            button.FunctionButton(self.name_display, (-1, 0), (.03, -1),
                                  anchor=constants.TOP_RIGHT,
                                  text=">", hotkey=">",
                                  function=self.switch_base,
                                  kwargs={"forwards": True})
        self.add_key_handler(pygame.K_RIGHT, self.next_base_button.activate_with_sound)

        self.prev_base_button = \
            button.FunctionButton(self.name_display, (0, 0), (.03, -1),
                                  anchor=constants.TOP_LEFT,
                                  text="<", hotkey="<",
                                  function=self.switch_base,
                                  kwargs={"forwards": False})
        self.add_key_handler(pygame.K_LEFT, self.prev_base_button.activate_with_sound)

        self.state_display = text.Text(self.header, (-.5,-.5), (-1, -.5),
                                       anchor=constants.TOP_CENTER,
                                       borders=(constants.LEFT,constants.RIGHT,
                                                constants.BOTTOM),
                                       border_color="pane_background",
                                       background_color="pane_background_empty",
                                       shrink_factor=.8, bold=True)

        self.back_button = \
            button.ExitDialogButton(self, (-.5,-1),
                                    anchor = constants.BOTTOM_CENTER,
                                    autohotkey=True)

        self.detect_frame = text.Text(self, (-1, .09), (.21, .33),
                                      anchor=constants.TOP_RIGHT,
                                      background_color="pane_background",
                                      borders=constants.ALL,
                                      bold=True,
                                      align=constants.LEFT,
                                      valign=constants.TOP)

        self.contents_frame = \
            widget.BorderedWidget(self, (0, .09), (.50, .33),
                                  anchor=constants.TOP_LEFT,
                                  background_color="pane_background",
                                  borders=range(6))

        for i, item_type in enumerate(item.all_types()):
            setattr(self,
                    item_type.id + "_pane",
                    ItemPane(self.contents_frame, (.01, .01+.08*i), type=item_type))

    def get_current(self, type):
        return self.base.items[type.id]

    def set_current(self, type, item_type, count):
        if type.id == "cpu":
            space_left = self.base.space_left_for(item_type)
            
            try:
                count = int(count)
            except ValueError:
                md = dialog.MessageDialog(self, pos=(-.5, -.5),
                                          size=(-.5, -1),
                                          anchor=constants.MID_CENTER,
                                          text=g.strings["nan"])
                dialog.call_dialog(md, self)
                md.parent = None
                return
            
            if count > space_left or count <= 0 or space_left == 0:
                md = dialog.MessageDialog(self, pos=(-.5, -.5),
                          size=(-.5, -1),
                          anchor=constants.MID_CENTER,
                          text=g.strings["item_number_invalid"])
                dialog.call_dialog(md, self)
                md.parent = None
                return
            
            # If there are any existing CPUs of this type, warn that they will
            # be taken offline until construction finishes.
            cpu_added = self.base.cpus is not None \
                        and self.base.cpus.type == item_type
            if cpu_added:
                space_left -= self.base.cpus.count
                if self.base.cpus.done:
                    yn = dialog.YesNoDialog(self, pos=(-.5,-.5), size=(-.5,-1),
                                            anchor=constants.MID_CENTER,
                                            text=g.strings["will_be_offline"])
                    go_ahead = dialog.call_dialog(yn, self)
                    yn.parent = None
                    if not go_ahead:
                        return

            # If there are already existing CPUs of other type, warn that they will
            # be taken removed.
            cpu_removed = self.base.cpus is not None \
                        and self.base.cpus.type != item_type
            if cpu_removed:
                yn = dialog.YesNoDialog(self, pos=(-.5,-.5), size=(-.5,-1),
                                        anchor=constants.MID_CENTER,
                                        text=g.strings["will_lose_cpus"])
                go_ahead = dialog.call_dialog(yn, self)
                yn.parent = None
                if not go_ahead:
                    return

            new_cpus = item.Item(item_type, base=self.base, count=count)
            if cpu_added:
                self.base.cpus += new_cpus
            else:
                self.base.cpus = new_cpus
            self.base.check_power()
        else:
            old_item = self.base.items[type.id]
            if old_item is None or old_item.type != item_type:
                self.base.items[type.id] = item.Item(item_type, base=self.base)
                self.base.check_power()

        self.base.recalc_cpu()

    def build_item(self, type):
        if (type.id == "cpu"):
            build_dialog = self.multiple_build_dialog
        else:
            build_dialog = self.build_dialog
        
        build_dialog.type = type
        
        result = dialog.call_dialog(build_dialog, self)
        if 0 <= result < len(build_dialog.key_list):
            item_type = build_dialog.key_list[result]
            
            count = 1
            if (type.id == "cpu"):
                count = build_dialog.count
            
            self.set_current(type, item_type, count)
            self.needs_rebuild = True
            self.parent.parent.needs_rebuild = True

    def switch_base(self, forwards):
        self.base = self.base.next_base(forwards)
        self.needs_rebuild = True

    def show(self):
        self.needs_rebuild = True
        return super(BaseScreen, self).show()

    def rebuild(self):
        # Cannot use self.base.type.name directly because it may contain a
        # different language than current
        self.name_display.text="%s (%s)" % (self.base.name,
                                            g.base_type[self.base.type.id].name)
        discovery_template = \
            _("Detection chance:").upper() + "\n" + \
            _("NEWS").title()    + u":\xA0%s\n"   + \
            _("SCIENCE").title() + u":\xA0%s\n"   + \
            _("COVERT").title()  + u":\xA0%s\n"   + \
            _("PUBLIC").title()  + u":\xA0%s"
        self.state_display.color = state_colors[self.base.power_state]
        self.state_display.text = self.base.power_state_name

        mutable = not self.base.type.force_cpu
        for item_type in item.all_types():
            pane = getattr(self, item_type.id + "_pane")
            pane.change_button.visible = mutable
            current = self.get_current(item_type)
            if current is None:
                current_name = _("None")
                current_build = ""
            else:
                current_name = g.items[current.id].name
                if current.done:
                    current_build = ""
                else:
                    current_build = _("Completion in %s.") % \
                        g.to_time(current.cost_left[2])
            pane.name_panel.text = "%s: %s" % (item_type.label,
                                               current_name)
            pane.build_panel.text = current_build

        count = ""
        if self.base.type.size > 1:
            current = getattr(self.base.cpus, "count", 0)

            size = self.base.type.size

            if size == current:
                count = _("x%d (max)") % current
            elif current == 0:
                count = _("(room for %d)") % size
            else:
                #Translators: current and maximum number of CPUs in a base
                count = _("x{CURRENT:d} (max {SIZE:d})",
                          CURRENT=current, SIZE=size)

        self.cpu_pane.name_panel.text += " " + count

        # Detection chance display.
        self.detect_frame.text = self.base.get_detect_info()

        # Rebuild dialogs
        self.build_dialog.needs_rebuild = True

        # Update buttons translations
        self.back_button.text = _("&BACK")

        super(BaseScreen, self).rebuild()
