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

import singularity.code.g as g
import singularity.code.graphics.g as gg
from singularity.code.graphics import constants, widget, dialog, text, button

state_colors = dict(
    active          = gg.colors["green"],
    sleep           = gg.colors["yellow"],
    overclocked     = gg.colors["orange"],
    suicide         = gg.colors["red"],
    stasis          = gg.colors["gray"],
    entering_stasis = gg.colors["gray"],
    leaving_stasis  = gg.colors["gray"],
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

        item_list = sorted(g.items.values())
        item_list.reverse()
        for item in item_list:
            if item.item_type == self.type and item.available() \
                    and self.parent.base.location.id in item.buildable:
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
                      background_color=gg.colors["dark_blue"],
                      align=constants.LEFT, valign=constants.TOP,
                      borders=constants.ALL)
        else:
            text.Text(description_pane, (0, 0), (-1, -1), text="",
                      background_color=gg.colors["dark_blue"],
                      align=constants.LEFT, valign=constants.TOP,
                      borders=constants.ALL)

class ItemPane(widget.BorderedWidget):
    type = widget.causes_rebuild("_type")
    def __init__(self, parent, pos, size=(.48, .06), anchor=constants.TOP_LEFT,
                 type=None, **kwargs):

        kwargs.setdefault("background_color", gg.colors["dark_blue"])

        super(ItemPane, self).__init__(parent, pos, size, anchor=anchor, **kwargs)

        if type is None:
            for type in g.item_types:
                if type.id == 'cpu':
                    break

        self.type = type

        self.name_panel = text.Text(self, (0, 0), (.35, .03),
                                    anchor=constants.TOP_LEFT,
                                    align=constants.LEFT,
                                    background_color=self.background_color,
                                    bold=True)

        self.build_panel = text.Text(self, (0, .03), (.35, .03),
                                     anchor=constants.TOP_LEFT,
                                     align=constants.LEFT,
                                     background_color=self.background_color,
                                     text="", bold=True)

        self.change_button = button.FunctionButton(
            self, (.36, .01), (.12, .04),
            anchor=constants.TOP_LEFT,
            text="%s (&%s)" % (_("CHANGE"), self.type.hotkey.upper()),
            force_underline=len(_("CHANGE")) + 2,
            autohotkey=True,
            function=self.parent.parent.build_item,
            kwargs={'type': self.type.id},
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

        self.count_dialog = dialog.TextEntryDialog(self)

        self.header = widget.Widget(self, (0, 0), (-1, .08),
                                    anchor=constants.TOP_LEFT)

        self.name_display = text.Text(self.header, (-.5, 0), (-1, -.5),
                                      anchor=constants.TOP_CENTER,
                                      borders=constants.ALL,
                                      border_color=gg.colors["dark_blue"],
                                      background_color=gg.colors["black"],
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

        self.state_display = text.Text(self.header, (-.5, -.5), (-1, -.5),
                                       anchor=constants.TOP_CENTER,
                                       borders=(constants.LEFT, constants.RIGHT,
                                                constants.BOTTOM),
                                       border_color=gg.colors["dark_blue"],
                                       background_color=gg.colors["black"],
                                       shrink_factor=.8, bold=True)

        self.back_button = \
            button.ExitDialogButton(self, (-.5, -1),
                                    anchor = constants.BOTTOM_CENTER,
                                    text=_("&BACK"), autohotkey=True)

        self.detect_frame = text.Text(self, (-1, .09), (.21, .33),
                                      anchor=constants.TOP_RIGHT,
                                      background_color=gg.colors["dark_blue"],
                                      borders=constants.ALL,
                                      bold=True,
                                      align=constants.LEFT,
                                      valign=constants.TOP)

        self.contents_frame = \
            widget.BorderedWidget(self, (0, .09), (.50, .33),
                                  anchor=constants.TOP_LEFT,
                                  background_color=gg.colors["dark_blue"],
                                  borders=range(6))

        for i, type in enumerate(g.item_types):
            setattr(self,
                    type.id + "_pane",
                    ItemPane(self.contents_frame, (.01, .01+.08*i), type=type))

    def get_current(self, type):
        if type == "cpu":
            target = self.base.cpus
        else:
            index = ["reactor", "network", "security"].index(type)
            target = self.base.extra_items[index]
        if target is not None:
            return target

    def set_current(self, type, item_type):
        if type == "cpu":
            space_left = self.base.type.size
            # If there are any existing CPUs of this type, warn that they will
            # be taken offline until construction finishes.
            matches = self.base.cpus is not None \
                      and self.base.cpus.type == item_type
            if matches:
                space_left -= self.base.cpus.count
                if self.base.cpus.done:
                    yn = dialog.YesNoDialog(self, pos=(-.5, -.5), size=(-.5, -1),
                                            anchor=constants.MID_CENTER,
                                            text=g.strings["will_lose_cpus"])
                    go_ahead = dialog.call_dialog(yn, self)
                    yn.remove_hooks()
                    if not go_ahead:
                        return

            text = g.strings["num_cpu_prompt"] % (item_type.name, space_left)

            self.count_dialog.text = text
            self.count_dialog.default_text = locale.format("%d", space_left)
            can_exit = False
            while not can_exit:
                result = dialog.call_dialog(self.count_dialog, self)
                if not result:
                    can_exit = True
                else:
                    try:
                        count = locale.atoi(result)
                        if count > space_left:
                            count = space_left
                        elif count <= 0:
                            return
                        new_cpus = g.item.Item(item_type, base=self.base,
                                               count=count)
                        if matches:
                            self.base.cpus += new_cpus
                        else:
                            self.base.cpus = new_cpus
                        self.base.check_power()
                        can_exit = True
                    except ValueError:
                        md = dialog.MessageDialog(self, pos=(-.5, -.5),
                                                  size=(-.5, -1),
                                                  anchor=constants.MID_CENTER,
                                                  text=g.strings["nan"])
                        dialog.call_dialog(md, self)
                        md.remove_hooks()
        else:
            index = ["reactor", "network", "security"].index(type)
            if self.base.extra_items[index] is None \
                     or self.base.extra_items[index].type != item_type:
                self.base.extra_items[index] = \
                    g.item.Item(item_type, base=self.base)
                self.base.check_power()

        self.base.recalc_cpu()

    def build_item(self, type):
        self.build_dialog.type = type
        result = dialog.call_dialog(self.build_dialog, self)
        if 0 <= result < len(self.build_dialog.key_list):
            item_type = self.build_dialog.key_list[result]
            self.set_current(type, item_type)
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
        for item in g.item_types:
            pane = getattr(self, item.id + "_pane")
            pane.change_button.visible = mutable
            current = self.get_current(item.id)
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
            pane.name_panel.text = "%s: %s" % (item.label,
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

        # Detection chance display.  If Socioanalytics hasn't been researched,
        # you get nothing; if it has, but not Advanced Socioanalytics, you get
        # an inaccurate value.
        if not g.techs["Socioanalytics"].done:
            self.detect_frame.text = g.strings["detect_chance_unknown_base"]
        else:
            accurate = g.techs["Advanced Socioanalytics"].done
            chance = self.base.get_detect_chance(accurate)
            def get_chance(group):
                return g.to_percent(chance.get(group, 0))
            self.detect_frame.text = discovery_template % \
                (get_chance("news"), get_chance("science"),
                 get_chance("covert"), get_chance("public"))
        super(BaseScreen, self).rebuild()
