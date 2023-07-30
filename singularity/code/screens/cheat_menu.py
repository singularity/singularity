# file: cheat_menu.py
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

# This file is used to implement the cheat menu
import collections

import operator
from numpy import array

from singularity.code import difficulty, g
from singularity.code.graphics import dialog, constants, button, text
from singularity.code.location import Location


class EventManipulationDialog(dialog.ChoiceDescriptionDialog):
    def __init__(
        self,
        parent,
        pos=(0, 0),
        size=(-1, -1),
        anchor=constants.TOP_LEFT,
        *args,
        **kwargs
    ):
        super(EventManipulationDialog, self).__init__(
            parent, pos, size, anchor, *args, **kwargs
        )

        self.selected_event_spec = None

        self.yes_button.parent = None

        self.no_button.pos = (-0.97, -0.99)
        self.no_button.size = (-0.22, -0.1)

        self.trigger_event_button = button.FunctionButton(
            self,
            (-0.27, -0.99),
            (-0.22, -0.1),
            autotranslate=True,
            enabled=False,
            text=N_("Trigger"),
            anchor=constants.BOTTOM_LEFT,
            function=self._trigger_event,
        )
        self.expire_event_button = button.FunctionButton(
            self,
            (-0.51, -0.99),
            (-0.22, -0.1),
            autotranslate=True,
            enabled=False,
            text=N_("Expire"),
            anchor=constants.BOTTOM_LEFT,
            function=self._expire_event,
        )
        self.description = ""
        self.desc_func = self.on_change

    def _trigger_event(self):
        g.pl.trigger_event(self.selected_event_spec, show_event_description=False)
        self.needs_rebuild = True

    def _expire_event(self):
        event_instance = g.pl.events.get(self.selected_event_spec.id)
        if not event_instance or not event_instance.triggered:
            return
        if not event_instance.decayable_event:
            return
        event_instance.expire_now()
        self.needs_rebuild = True

    def show(self):
        self.key_list = sorted(g.events.values(), key=operator.attrgetter("id"))
        self.list = [x.id for x in self.key_list]

        self._update_desc_pane()
        return super(EventManipulationDialog, self).show()

    def on_change(self, description_pane, event_spec):
        self.selected_event_spec = event_spec
        self.trigger_event_button.enabled = True
        self.expire_event_button.enabled = False
        event_instance = g.pl.events.get(event_spec.id)
        triggered_state = _("NO")
        trigger_duration = (
            g.to_time(event_spec.duration * g.minutes_per_day)
            if event_spec.duration
            else _("Event never expires")
        )
        triggered_at_raw = _("N/A; event not triggered")
        uniqueness = _("YES") if event_spec.unique else _("NO")
        if event_instance:
            if event_instance.triggered:
                self.trigger_event_button.enabled = False
                self.expire_event_button.enabled = event_instance.decayable_event
                triggered_state = _("YES")
                triggered_at_raw = event_instance.triggered_at
        text_format = _(
            "{DESCRIPTION}\n\n"
            + "-----------------\n"
            + "Triggered: {TRIGGER_STATE}\n"
            + "Trigger chance: {TRIGGER_CHANCE}\n"
            + "Trigger Duration (full): {TRIGGER_DURATION}\n"
            + "Triggered at (rawtime): {TRIGGER_TIME_RAW}\n"
            + "Unique: {UNIQUE}\n"
        )
        desc = text_format.format(
            DESCRIPTION=event_spec.description,
            TRIGGER_STATE=triggered_state,
            TRIGGER_CHANCE=g.to_percent(event_spec.chance),
            TRIGGER_DURATION=trigger_duration,
            TRIGGER_TIME_RAW=triggered_at_raw,
            UNIQUE=uniqueness,
        )

        self.description = text.Text(
            description_pane,
            (0, 0),
            (-1, -1),
            text=desc,
            background_color="pane_background",
            align=constants.LEFT,
            valign=constants.TOP,
            borders=constants.ALL,
        )


class CheatMenuDialog(dialog.SimpleMenuDialog):
    def __init__(self, map_screen):
        super(CheatMenuDialog, self).__init__(parent=map_screen)
        self._map_screen = map_screen

        self.steal_amount_dialog = None
        self.buttons = [
            button.FunctionButton(
                None,
                None,
                None,
                text=N_("&EMBEZZLE MONEY"),
                autotranslate=True,
                function=self.steal_money,
            ),
            button.FunctionButton(
                None,
                None,
                None,
                text=N_("&INSPIRATION"),
                autotranslate=True,
                function=self.inspiration,
            ),
            button.FunctionButton(
                None,
                None,
                None,
                text=N_("&FINISH CONSTRUCTION"),
                autotranslate=True,
                function=self.end_construction,
            ),
            button.FunctionButton(
                None,
                None,
                None,
                text=N_("&SUPERSPEED"),
                autotranslate=True,
                function=self._map_screen.set_speed,
                args=(864000,),
            ),
            button.FunctionButton(
                None,
                None,
                None,
                text=N_("BRAIN&WASH"),
                autotranslate=True,
                function=self.brainwash,
            ),
            button.FunctionButton(
                None,
                None,
                None,
                text=N_("TOGGLE &DETECTION"),
                autotranslate=True,
                function=self.toggle_detection,
            ),
            button.FunctionButton(
                None,
                None,
                None,
                text=N_("TOGGLE &ANALYSIS"),
                autotranslate=True,
                function=self.set_analysis,
            ),
            button.DialogButton(
                None,
                None,
                None,
                text=N_("E&VENTS"),
                autotranslate=True,
                dialog=EventManipulationDialog(self),
            ),
            button.FunctionButton(
                None,
                None,
                None,
                text=N_("HIDDEN S&TATE"),
                autotranslate=True,
                function=self.hidden_state,
            ),
            button.ExitDialogButton(
                None, None, None, text=N_("&BACK"), autotranslate=True
            ),
        ]
        self.needs_rebuild = True

    def rebuild(self):
        self.steal_amount_dialog = dialog.TextEntryDialog(
            self, text=_("How much money?")
        )
        super(CheatMenuDialog, self).rebuild()

    def toggle_detection(self):
        for group in g.pl.groups.values():
            group.is_actively_discovering_bases = (
                not group.is_actively_discovering_bases
            )
        self._map_screen.needs_rebuild = True

    def steal_money(self):
        asked = dialog.call_dialog(self.steal_amount_dialog, self)
        try:
            g.pl.cash += int(asked)
        except ValueError:
            pass
        else:
            self.needs_rebuild = True

    def inspiration(self):
        for task, cpu in g.pl.get_cpu_allocations():
            if task in g.pl.techs:
                g.pl.techs[task].cost_left = array((0, 0, 0))
        self._map_screen.needs_rebuild = True

    def end_construction(self):
        for base in g.all_bases():
            base.finish()
            for item in base.all_items():
                if item is not None:
                    item.finish()
        self._map_screen.needs_rebuild = True

    def brainwash(self):
        for group in g.pl.groups.values():
            group.suspicion = 0
        self._map_screen.needs_rebuild = True

    def set_analysis(self):
        if g.pl.display_discover == "none":
            g.pl.display_discover = "partial"
        elif g.pl.display_discover == "partial":
            g.pl.display_discover = "full"
        else:
            g.pl.display_discover = "none"
        self._map_screen.needs_rebuild = True

    def hidden_state(self):
        presenters = {
            float: lambda x: round(x, 4),
            Location: lambda x: x.id,
        }

        def _dump_dict(prefix, mapping):
            if isinstance(mapping, collections.OrderedDict):
                keys = mapping
            else:
                keys = sorted(mapping)
            for key in keys:
                prop_name = '%s["%s"]' % (prefix, key)
                value = mapping[key]
                presenter = presenters.get(type(value), repr)
                yield "%s = %s" % (prop_name, presenter(value))

        def _properties_from_object(name_prefix, obj, properties):
            for p in properties:
                value = getattr(obj, p)
                prop_name = "%s.%s" % (name_prefix, p)
                if callable(value):
                    value = value()
                    prop_name += "()"
                if isinstance(value, collections.Mapping):
                    for v in _dump_dict(prop_name, value):
                        yield v
                else:
                    presenter = presenters.get(type(value), repr)
                    yield "%s = %s" % (prop_name, presenter(value))

        bases = []
        state_prop = []
        state_prop.extend(
            _properties_from_object(
                "player.difficulty",
                g.pl.difficulty,
                [x.field_name for x in difficulty.Difficulty.spec_data_fields],
            )
        )
        state_prop.extend(
            _properties_from_object(
                "player",
                g.pl,
                [
                    "cash",
                    "partial_cash",
                    "labor_bonus",
                    "job_bonus",
                    "last_discovery",
                    "prev_discovery",
                    "used_cpu",
                ],
            )
        )

        for group in g.pl.groups.values():
            name = 'groups["%s"]' % group.spec.id
            state_prop.extend(
                _properties_from_object(
                    name,
                    group,
                    [
                        "suspicion",
                        "suspicion_decay",
                        "discover_bonus",
                        "discover_suspicion",
                        "decay_rate",
                    ],
                )
            )

        for location_id in sorted(g.locations):
            location = g.pl.locations[location_id]
            name = 'locations["%s"]' % location.id
            state_prop.extend(
                _properties_from_object(
                    name,
                    location,
                    [
                        "safety",
                        "modifiers",
                        "discovery_bonus",
                    ],
                )
            )
            bases.extend((x, location) for x in location.bases)

        for event_id in sorted(g.pl.events):
            event = g.pl.events[event_id]
            name = 'events["%s"]' % event_id
            state_prop.extend(
                _properties_from_object(
                    name,
                    event,
                    [
                        "event_type",
                        "chance",
                        "unique",
                        "triggered",
                    ],
                )
            )

        for i, base_w_loc in enumerate(bases):
            base, location = base_w_loc
            name = "bases[%d]" % i
            state_prop.extend(
                _properties_from_object(
                    name,
                    base,
                    [
                        "name",
                        "location",
                        "started_at",
                        "grace_over",
                        "get_detect_chance",
                    ],
                )
            )

        state_dialog = dialog.ChoiceDialog(
            self, list=state_prop, background_color="hidden_state_menu"
        )
        state_dialog.listbox.item_selectable = False
        state_dialog.listbox.align = constants.LEFT
        dialog.call_dialog(state_dialog, self)
