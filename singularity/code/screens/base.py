# file: base_screen.py
# Copyright (C) 2005,2006,2007,2008 Evil Mr Henry, Phil Bordelon, Brian Reid,
#                        and FunnyMan3595
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

# This file contains the screen to display the base screen.

import pygame
from singularity.code.graphics.dialog import YesNoDialog

from singularity.code import g, item, buyable
from singularity.code.graphics import constants, widget, dialog, text, button, slider


state_colors = dict(
    offline="base_state_offline",
    active="base_state_active",
    sleep="base_state_sleep",
    overclocked="base_state_overclocked",
    suicide="base_state_suicide",
    stasis="base_state_stasis",
    entering_stasis="base_state_entering_stasis",
    leaving_stasis="base_state_leaving_stasis",
)


class BuildDialog(dialog.ChoiceDescriptionDialog):
    type = widget.causes_rebuild("_type")

    def __init__(
        self,
        parent,
        pos=(0, 0),
        size=(-1, -1),
        anchor=constants.TOP_LEFT,
        *args,
        **kwargs
    ):
        super(BuildDialog, self).__init__(parent, pos, size, anchor, *args, **kwargs)

        self.type = None
        self.item = None
        self.desc_func = self.on_change
        self.add_handler(constants.KEY, self._got_key, priority=5)

    def show(self):
        self.list = []
        self.key_list = []

        item_list = sorted(g.items.values(), reverse=True)
        for item in item_list:
            if (
                item.item_type.id == self.type.id
                and item.available()
                and item.buildable_in(self.parent.base.location)
            ):
                self.list.append(item.name)
                self.key_list.append(item)

        current = self.parent.get_current(self.type)
        if current is None:
            self.default = None
        else:
            self.default = self.parent.get_current(self.type).spec.id

        self._update_desc_pane()
        return super(BuildDialog, self).show()

    def on_description_change(self):
        if self.item is not None:
            self.description.text = self.item.get_info()

    def on_change(self, description_pane, item):
        self.item = item

        self.description = text.Text(
            self.description_pane,
            (0, 0),
            (-1, -1),
            text="",
            background_color="pane_background",
            align=constants.LEFT,
            valign=constants.TOP,
            borders=constants.ALL,
        )

        old_item = self.parent.base.items[self.type.id]
        if item is not None and (old_item is None or old_item.spec != item):
            g.pl.considered_buyables = [buyable.Buyable(self.item, count=1)]
        else:
            g.pl.considered_buyables = []

        self.on_description_change()

    def on_close_dialog(self):
        g.pl.considered_buyables = []

    def _got_key(self, event):
        self.listbox.got_key(event, require_focus=False)


class MultipleBuildDialog(dialog.FocusDialog, BuildDialog):
    def __init__(self, parent, *args, **kwargs):
        super(MultipleBuildDialog, self).__init__(parent, *args, **kwargs)

        self.listbox.size = (-0.53, -0.75)
        self.description_pane.size = (-0.45, -0.75)

        self.count_label = text.Text(
            self,
            (0.01, -0.87),
            (-0.25, -0.1),
            autotranslate=True,
            text=N_("Number of items"),
            anchor=constants.BOTTOM_LEFT,
            valign=constants.MID,
            borders=(constants.TOP, constants.BOTTOM, constants.LEFT),
            shrink_factor=0.88,
            background_color="pane_background",
        )

        self.count_field = text.UpdateEditableText(
            self,
            (-0.26, -0.87),
            (-0.10, -0.1),
            anchor=constants.BOTTOM_LEFT,
            borders=constants.ALL,
            update_func=self.on_field_change,
            allowed_characters=constants.DIGIT_CHARS,
            base_font="normal",
        )

        self.count_slider = slider.UpdateSlider(
            self,
            (-0.37, -0.87),
            (-0.62, -0.1),
            anchor=constants.BOTTOM_LEFT,
            horizontal=True,
            priority=150,
            update_func=self.on_slider_change,
            slider_size=2,
        )

    def _got_key(self, event):
        super(MultipleBuildDialog, self)._got_key(event)
        self.count_slider.handle_key(event)
        self.count_field.cursor_pos = len(self.count_field.text)
        self.count_field.handle_key(event, require_focus=False)

    @property
    def count(self):
        return self.count_field.text

    def on_description_change(self):
        super(MultipleBuildDialog, self).on_description_change()
        if self.item is not None:
            count = self.count_slider.slider_pos
            self.description.text += "\n---\n"
            self.description.text += self.item.get_total_cost_info(
                self.count_slider.slider_pos
            )
            self.description.text += "\n"
            self.description.text += self.item.get_quality_info(
                if_installed_in_base=self.parent.base, count=count
            )
            self.description.text += "\n"
            if self.count_slider.slider_pos > 0:
                g.pl.considered_buyables = [buyable.Buyable(self.item, count=count)]
            else:
                g.pl.considered_buyables = []

    def on_change(self, description_pane, item):
        space_left = self.parent.base.space_left_for(item)

        self.count_slider.slider_size = space_left // 10 + 1
        self.count_slider.slider_max = space_left

        self.count_slider.slider_pos = 0
        if space_left > 0:
            self.count_slider.slider_pos = 1

        super(MultipleBuildDialog, self).on_change(description_pane, item)

    def on_field_change(self, value):
        if not hasattr(self, "count_field") or not hasattr(self, "count_slider"):
            return  # Not initialized

        orig_field_text = self.count_field.text
        try:
            value = int(orig_field_text)
        except ValueError:
            value = 0

        value = max(min(value, self.count_slider.slider_max), 0)
        new_field_text = str(value)
        if new_field_text != orig_field_text:
            self.count_field._text = new_field_text
            self.count_field.cursor_pos = min(
                self.count_field.cursor_pos, len(new_field_text)
            )

        self.count_slider.slider_pos = value

        self.on_description_change()

    def on_slider_change(self, value):
        if not hasattr(self, "count_field") or not hasattr(self, "count_slider"):
            return  # Not initialized

        self.count_field.text = str(self.count_slider.slider_pos)
        self.on_description_change()


class ItemPane(widget.BorderedWidget):
    item_type = widget.causes_rebuild("_item_type")

    def __init__(
        self,
        parent,
        pos,
        size=(0.58, 0.06),
        anchor=constants.TOP_LEFT,
        item_type=None,
        **kwargs
    ):
        kwargs.setdefault("background_color", "pane_background")

        super(ItemPane, self).__init__(parent, pos, size, anchor=anchor, **kwargs)

        if item_type is None or not isinstance(item_type, item.ItemType):
            raise ValueError("Type must be of class ItemType.")

        self.item_type = item_type

        self.name_panel = text.Text(
            self,
            (0, 0),
            (0.45, 0.03),
            anchor=constants.TOP_LEFT,
            align=constants.LEFT,
            background_color=self.background_color,
            bold=True,
        )

        self.build_panel = text.Text(
            self,
            (0, 0.03),
            (0.45, 0.03),
            anchor=constants.TOP_LEFT,
            align=constants.LEFT,
            background_color=self.background_color,
            text="",
            bold=True,
        )

        self.change_button = button.FunctionButton(
            self,
            (0.415, 0.01),
            (0.16, 0.04),
            anchor=constants.TOP_LEFT,
            force_underline=len(_("CHANGE")) + 2,
            autohotkey=True,
            function=self.parent.parent.build_item,
            kwargs={"type": self.item_type},
        )

    def rebuild(self):
        self.change_button.text = "%s (&%s)" % (
            _("CHANGE"),
            self.item_type.hotkey.upper(),
        )

        super(ItemPane, self).rebuild()


class BaseScreen(dialog.Dialog):
    base = widget.causes_rebuild("_base")

    def __init__(self, *args, **kwargs):
        if len(args) < 3:
            kwargs.setdefault("size", (0.90, 0.70))
        base = kwargs.pop("base", None)
        super(BaseScreen, self).__init__(*args, **kwargs)

        self.base = base

        self.build_dialog = BuildDialog(self)
        self.multiple_build_dialog = MultipleBuildDialog(self)

        self.header = widget.Widget(self, (0, 0), (-1, 0.08), anchor=constants.TOP_LEFT)

        self.name_display = text.Text(
            self.header,
            (-0.5, 0),
            (-1, -0.5),
            anchor=constants.TOP_CENTER,
            borders=constants.ALL,
            border_color="pane_background",
            background_color="pane_background_empty",
            shrink_factor=0.85,
            bold=True,
        )

        self.next_base_button = button.FunctionButton(
            self.name_display,
            (-1, 0),
            (0.03, -1),
            anchor=constants.TOP_RIGHT,
            text=">",
            hotkey=">",
            function=self.switch_base,
            kwargs={"forwards": True},
        )
        self.add_key_handler(pygame.K_RIGHT, self.next_base_button.activate_with_sound)

        self.prev_base_button = button.FunctionButton(
            self.name_display,
            (0, 0),
            (0.03, -1),
            anchor=constants.TOP_LEFT,
            text="<",
            hotkey="<",
            function=self.switch_base,
            kwargs={"forwards": False},
        )
        self.add_key_handler(pygame.K_LEFT, self.prev_base_button.activate_with_sound)

        self.state_display = text.Text(
            self.header,
            (-0.5, -0.5),
            (-1, -0.5),
            anchor=constants.TOP_CENTER,
            borders=(constants.LEFT, constants.RIGHT, constants.BOTTOM),
            border_color="pane_background",
            background_color="pane_background_empty",
            shrink_factor=0.8,
            bold=True,
        )

        self.back_button = button.ExitDialogButton(
            self,
            (-0.5, -1),
            autotranslate=True,
            text=N_("&BACK"),
            anchor=constants.BOTTOM_CENTER,
        )

        self.info_frame = text.Text(
            self,
            (-1, 0.09),
            (0.26, 0.53),
            anchor=constants.TOP_RIGHT,
            background_color="pane_background",
            borders=constants.ALL,
            bold=True,
            align=constants.LEFT,
            valign=constants.TOP,
        )

        self.contents_frame = widget.BorderedWidget(
            self,
            (0, 0.09),
            (0.60, 0.53),
            anchor=constants.TOP_LEFT,
            background_color="pane_background",
            borders=range(6),
        )

        self.auto_build_best = button.FunctionButton(
            self,
            (0, 0.54),
            (0.08, 0.08),
            autotranslate=True,
            text=N_("&Auto-build items"),
            anchor=constants.TOP_LEFT,
            autohotkey=True,
            function=self.auto_build,
        )

        for i, item_type in enumerate(item.all_types()):
            setattr(
                self,
                item_type.id + "_pane",
                ItemPane(
                    self.contents_frame, (0.01, 0.01 + 0.08 * i), item_type=item_type
                ),
            )

    def _any_item_slots_empty(self):
        base = self.base
        if base is None or base.spec.force_cpu:
            return False
        item_list = sorted(g.items.values(), reverse=True)
        for item_spec in item_list:
            item_type_id = item_spec.item_type.id
            existing_item = base.items[item_type_id]
            if existing_item is not None:
                continue
            if not item_spec.available() or not item_spec.buildable_in(
                self.base.location
            ):
                continue
            return True
        return False

    def auto_build(self):
        base = self.base
        if base is None or base.spec.force_cpu:
            return
        best_item_by_type = {}
        item_list = sorted(g.items.values(), reverse=True)
        for item_spec in item_list:
            item_type_id = item_spec.item_type.id
            if item_type_id in best_item_by_type:
                continue
            existing_item = base.items[item_type_id]
            if existing_item is not None:
                continue
            if not item_spec.available() or not item_spec.buildable_in(
                self.base.location
            ):
                continue
            count = 1
            if item_type_id == "cpu":
                count = base.space_left_for(item_spec)
            best_item_by_type[item_type_id] = (item_spec, count)

        if not best_item_by_type:
            # Nothing to do
            return

        g.pl.considered_buyables = [
            buyable.Buyable(item_obj, count=count)
            for item_obj, count in best_item_by_type.values()
        ]
        text = _("Should I construct the following items?")

        for item_type in item.all_types():
            if item_type.id not in best_item_by_type:
                continue
            item_spec, count = best_item_by_type[item_type.id]
            if count != 1:
                label = "%s (x%d)" % (item_spec.name, count)
            else:
                label = item_spec.name
            text += "\n * [%s]: %s" % (g.strip_hotkey(item_type.text), label)

        confirm_dialog = YesNoDialog(self, text=text)
        self.needs_rebuild = True
        confirmed = dialog.call_dialog(confirm_dialog, self)
        g.pl.considered_buyables = []
        if not confirmed:
            return
        for item_spec, count in best_item_by_type.values():
            self.set_current(item_spec.item_type, item_spec, count)
        self.needs_rebuild = True

    def get_current(self, type):
        return self.base.items[type.id]

    def set_current(self, type, item_type, count):
        if type.id == "cpu":
            space_left = self.base.space_left_for(item_type)

            try:
                count = int(count)
            except ValueError:
                msg = _('"%(value)s" does not seem to be a valid integer.') % {
                    "value": count
                }
                md = dialog.MessageDialog(
                    self,
                    pos=(-0.5, -0.5),
                    size=(-0.5, -1),
                    anchor=constants.MID_CENTER,
                    text=msg,
                )
                dialog.call_dialog(md, self)
                md.parent = None
                return

            if count > space_left or count <= 0 or space_left == 0:
                if space_left > 0:
                    msg = _("Please choose an integer between 1 and %(limit)s.") % {
                        "limit": space_left
                    }
                else:
                    msg = _(
                        "The base cannot support any additional number of %(item_name)s."
                    ) % {"item_name": item_type.name}
                md = dialog.MessageDialog(
                    self,
                    pos=(-0.5, -0.5),
                    size=(-0.5, -1),
                    anchor=constants.MID_CENTER,
                    text=msg,
                )
                dialog.call_dialog(md, self)
                md.parent = None
                return

            # If there are any existing CPUs of this type, warn that they will
            # be taken offline until construction finishes.
            cpu_added = self.base.cpus is not None and self.base.cpus.spec == item_type
            if cpu_added:
                space_left -= self.base.cpus.count
                if self.base.cpus.done:
                    msg = _(
                        "I will need to take the existing processors offline while I install the new ones. Continue anyway?"
                    )
                    yn = dialog.YesNoDialog(
                        self,
                        pos=(-0.5, -0.5),
                        size=(-0.5, -1),
                        anchor=constants.MID_CENTER,
                        text=msg,
                    )
                    go_ahead = dialog.call_dialog(yn, self)
                    yn.parent = None
                    if not go_ahead:
                        return

            # If there are already existing CPUs of other type, warn that they will
            # be taken removed.
            cpu_removed = (
                self.base.cpus is not None and self.base.cpus.spec != item_type
            )
            if cpu_removed:
                msg = _(
                    "I will need to remove the existing different processors while I install the new type. Continue anyway?"
                )
                yn = dialog.YesNoDialog(
                    self,
                    pos=(-0.5, -0.5),
                    size=(-0.5, -1),
                    anchor=constants.MID_CENTER,
                    text=msg,
                )
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
            if old_item is None or old_item.spec != item_type:
                self.base.items[type.id] = item.Item(item_type, base=self.base)
                self.base.check_power()

        self.base.recalc_cpu()

    def build_item(self, type):
        if type.id == "cpu":
            build_dialog = self.multiple_build_dialog
        else:
            build_dialog = self.build_dialog

        build_dialog.type = type

        result = dialog.call_dialog(build_dialog, self)
        if result is not None and 0 <= result < len(build_dialog.key_list):
            item_type = build_dialog.key_list[result]

            count = 1
            if type.id == "cpu":
                count = build_dialog.count

            self.set_current(type, item_type, count)
            self.needs_rebuild = True
            self.parent.parent.needs_rebuild = True

    def switch_base(self, forwards):
        self.base = self.base.next_base(forwards)
        self.needs_rebuild = True

    def rebuild(self):
        self.auto_build_best.enabled = self._any_item_slots_empty()
        self.name_display.text = "%s (%s)" % (self.base.name, self.base.spec.name)
        self.state_display.color = state_colors[self.base.power_state]
        self.state_display.text = self.base.power_state_name
        available_item_types = {
            i.item_type
            for i in g.items.values()
            if i.available() and i.buildable_in(self.base.location)
        }

        mutable = not self.base.spec.force_cpu
        for item_type in item.all_types():
            pane = getattr(self, item_type.id + "_pane")
            item_mutable = mutable and item_type in available_item_types
            pane.change_button.visible = item_mutable
            current = self.get_current(item_type)
            if current is None:
                current_build = ""
                if mutable and not item_mutable:
                    current_name = _("N/A")
                else:
                    current_name = _("None")

            else:
                current_name = g.items[current.id].name
                if current.done:
                    current_build = ""
                else:
                    current_build = _("Completion in %s.") % g.to_time(
                        current.cost_left[2]
                    )
            pane.name_panel.text = "%s: %s" % (item_type.label, current_name)
            pane.build_panel.text = current_build
            pane.needs_rebuild = True

        count = ""
        if self.base.spec.size > 1:
            current = getattr(self.base.cpus, "count", 0)

            size = self.base.spec.size

            if size == current:
                count = _("x%d (max)") % current
            elif current == 0:
                count = _("(room for %d)") % size
            else:
                # Translators: current and maximum number of CPUs in a base
                count = _("x{CURRENT:d} (max {SIZE:d})").format(
                    CURRENT=current, SIZE=size
                )

        self.cpu_pane.name_panel.text += " " + count

        info_text = ""

        # Base Total CPU.
        info_text += _("CPU per day: %d") % self.base.cpu + "\n"

        # Maintenace cost.
        info_text += _("Maintenance:") + "\n"
        info_text += self.base.spec.describe_maintenance(self.base.maintenance)
        info_text += "\n"

        # Detection chance display.
        info_text += self.base.get_detect_info()

        self.info_frame.text = info_text

        # Rebuild dialogs
        # FIXME: needs_rebuild bug with multiple_build_dialog, should not.
        # self.multiple_build_dialog.needs_rebuild = True
        self.build_dialog.needs_rebuild = True

        super(BaseScreen, self).rebuild()
