#file: map_screen.py
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

#This file is used to display the World Map.

from __future__ import absolute_import

import collections
import pygame

from code import g, savegame as sv, mixer
from code import chance, difficulty, logmessage, warning
from code.location import Location
from code.graphics import g as gg
from code.graphics import dialog, constants, image, button, text, widget
from code.screens import research, knowledge, report, log, message, savegame
from code.screens.location import LocationScreen
from code.screens.options import OptionsScreen

import math
import time

from pygame.surfarray import pixels_alpha

from numpy import array, sin, cos, linspace, pi, tanh, round, newaxis, uint8

class EarthImage(image.Image):
    def __init__(self, parent):
        super(EarthImage, self).__init__(parent, (.5,.5), (1,.667),
                                         constants.MID_CENTER,
                                         'earth')
        self._sin_latitude = None
        self._cos_longitude_x_cos_latitiude = None
        self.needs_resize = True
        self.sun_radius = 0.5*pi/360
        self.night_image = None

    def rescale(self):
        super(EarthImage, self).rescale()
        self.night_image = image.scale(gg.images['earth_night'],
                                       self.real_size).convert_alpha()

    def reconfig(self):
        super(EarthImage, self).reconfig()

        self.resize()

        self.rescale()
        self.needs_rebuild = True
        self.needs_resize = True
        self.needs_redraw = True

    def resize(self):
        super(EarthImage, self).resize()
        width, height = self.real_size
        latitude = linspace(-pi/2, pi/2, height)[newaxis,:]
        longitude = linspace(0, 2*pi, width)[:,newaxis]
        self._cos_longitude_x_cos_latitiude = cos(longitude) * cos(latitude)
        self._sin_latitude = sin(latitude)

    night_mask_day_of_year = None
    night_mask_dim = None
    night_mask = None
    next_night_mask = None
    next_night_mask_ready = False
    next_night_mask_step = 0
    step_night_alphas = None
    step_round_light = None

    start_day = None
    start_second = None

    def compute_day_of_year(self):
        day_of_year = (g.pl.time_day+g.pl.start_day) % 365 # no leap years, sorry
        return day_of_year

    def on_tick(self, event):
        if self.next_night_mask_ready:
            return
        width, height = self.real_size
        day_of_year = self.compute_day_of_year()
        # Prepare a part of the next night mask to avoid lagging at end of day
        # on game speed high speed.
        self._compute_night_mask_step(width, height, day_of_year + 1)

    def _compute_night_mask_step(self, width, height, next_day_of_year):
        if self.next_night_mask_ready:
            return
        if self.next_night_mask_step == 0:
            self.next_night_mask = pygame.Surface((width, height), 0, gg.ALPHA)
            self.step_sun_declination = (-23.45/360.*2*math.pi *
                               math.cos(2*math.pi/365.*(next_day_of_year + 10)))

        elif self.next_night_mask_step == 1:
            self.step_sin_sun_altitude = (self._cos_longitude_x_cos_latitiude * cos(self.step_sun_declination)
                                          + self._sin_latitude * sin(self.step_sun_declination))
        elif self.next_night_mask_step == 2:
            self.step_light = 0.5*(tanh(self.step_sin_sun_altitude/self.sun_radius)+1)
        elif self.next_night_mask_step == 3:
            max_alpha = 255
            self.step_night_alphas = pixels_alpha(self.next_night_mask)
            self.step_round_light = round(max_alpha*self.step_light).astype(uint8)
        elif self.next_night_mask_step == 4:
            self.step_night_alphas[...] = self.step_round_light
            self.next_night_mask_ready = True

        self.next_night_mask_step = (self.next_night_mask_step + 1) % 5

    def get_night_mask(self):
        width, height = self.real_size
        day_of_year = self.compute_day_of_year()

        if day_of_year != self.night_mask_day_of_year:
            self.night_mask = None
            # Force a rebuild.  In most cases, it will be ready at ahead of time
            # but if any steps are missing, we force a rebuild now at cost of
            # rebuild.
        elif self.night_mask_dim != (width, height):
            self.night_mask = None
            # Force a rebuild from scratch at cost of frame-rate
            self.next_night_mask_ready = False
            self.next_night_mask_step = 0
        else:
            return self.night_mask

        while not self.next_night_mask_ready:
            self._compute_night_mask_step(width, height, day_of_year)
        self.night_mask = self.next_night_mask
        self.next_night_mask_ready = False

        return self.night_mask

    high_speed_pos = None
    def compute_night_start(self):
        if self.high_speed_pos is None or g.curr_speed<=100000:
            width = self.real_size[0]
            if self.start_second is None:
                t = time.gmtime()
                self.start_second = t[5] + 60*(t[4]+60*t[3])
            day_portion = (((g.pl.raw_min+self.start_second//60)
                               % g.minutes_per_day)
                      / float(g.minutes_per_day))
            self.high_speed_pos = int(width * (0.5 - day_portion)) % width
        return self.high_speed_pos

    def redraw(self):
        width = self.real_size[0]

        self.night_start = self.compute_night_start()

        super(EarthImage, self).redraw()

        if not g.daynight:
            return

        # Turn half of the map to night, with blended borders.
        night_mask = self.get_night_mask()
        mask_alphas = pixels_alpha(night_mask)
        night_alphas = pixels_alpha(self.night_image)

        right_width = width - self.night_start
        night_alphas[self.night_start:] = mask_alphas[:right_width]
        if self.night_start != 0:
            night_alphas[:self.night_start]  = mask_alphas[right_width:]

        del night_alphas, mask_alphas
        self.surface.blit(self.night_image, (0,0))

    night_start = None
    def rebuild(self):
        super(EarthImage, self).rebuild()

        if not g.daynight:
            return

        old_night_start = self.night_start
        if old_night_start is None or self.needs_redraw:
            return

        width = self.real_size[0]
        self.night_start = self.compute_night_start()

        movement = (old_night_start - self.night_start) % width
        if movement == 0 \
           and self.compute_day_of_year() == self.night_mask_day_of_year:
            return

        self.redraw()

        # Redraw children.
        for child in self.children:
            if child.visible:
                child.redraw()


class CheatMenuDialog(dialog.SimpleMenuDialog):

    def __init__(self, map_screen):
        super(CheatMenuDialog, self).__init__(parent=map_screen)
        self._map_screen = map_screen

        self.steal_amount_dialog = None
        self._rebuild_menu_buttons()
        self.needs_rebuild = True

    def _rebuild_menu_buttons(self):
        menu_buttons = [
            button.FunctionButton(None, None, None, text=_("&EMBEZZLE MONEY"),
                                  autohotkey=True, function=self.steal_money),

            button.FunctionButton(None, None, None, text=_("&INSPIRATION"),
                                  autohotkey=True, function=self.inspiration),
            button.FunctionButton(None, None, None, text=_("&FINISH CONSTRUCTION"),
                                  autohotkey=True, function=self.end_construction),
            button.FunctionButton(None, None, None, text=_("&SUPERSPEED"),
                                  autohotkey=True, function=self._map_screen.set_speed,
                                  args=(864000,)),
            button.FunctionButton(None, None, None, text=_("BRAIN&WASH"),
                                  autohotkey=True, function=self.brainwash),
            button.FunctionButton(None, None, None, text=_("TOGGLE &DETECTION"),
                                  autohotkey=True, function=self.toggle_detection),
            button.FunctionButton(None, None, None, text=_("TOGGLE &ANALYSIS"),
                                  autohotkey=True, function=self.set_analysis),

            button.FunctionButton(None, None, None, text=_("HIDDEN S&TATE"),
                                  autohotkey=True, function=self.hidden_state),

            button.ExitDialogButton(None, None, None,
                                    text=_("&BACK"),
                                    autohotkey=True),
        ]
        self._buttons = menu_buttons

    def rebuild(self):
        self._rebuild_menu_buttons()
        self.steal_amount_dialog = dialog.TextEntryDialog(self, text=_("How much money?"))
        super(CheatMenuDialog, self).rebuild()

    def toggle_detection(self):
        for group in g.pl.groups.values():
            group.is_actively_discovering_bases = not group.is_actively_discovering_bases
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
        for task, cpu in g.pl.cpu_usage.items():
            if task in g.techs and cpu > 0:
                g.techs[task].cost_left = array((0, 0, 0))
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
                keys = mapping.iterkeys()
            else:
                keys = sorted(mapping)
            for key in keys:
                prop_name = '%s["%s"]' % (prefix, key)
                value = mapping[key]
                presenter = presenters.get(type(value), repr)
                yield "%s = %s" % (prop_name, presenter(value))

        def _properties_from_object(name, object, properties):
            for p in properties:
                value = getattr(object, p)
                prop_name = '%s.%s' % (name, p)
                if callable(value):
                    value = value()
                    prop_name += '()'
                if isinstance(value, collections.Mapping):
                    for v in _dump_dict(prop_name, value):
                        yield v
                else:
                    presenter = presenters.get(type(value), repr)
                    yield "%s = %s" % (prop_name, presenter(value))

        bases = []
        state_prop = []
        state_prop.extend(_properties_from_object('player.difficulty', g.pl.difficulty, difficulty.columns))
        state_prop.extend(_properties_from_object('player', g.pl, [
            'cash', 'partial_cash', 'labor_bonus', 'job_bonus',
            'last_discovery', 'prev_discovery', 'used_cpu',
        ]))

        for group in g.pl.groups.values():
            name = 'groups["%s"]' % group.spec.id
            state_prop.extend(_properties_from_object(name, group, [
                'suspicion', 'suspicion_decay', 'discover_bonus', 'discover_suspicion', 'decay_rate',
            ]))

        for location_id in sorted(g.locations):
            location = g.pl.locations[location_id]
            name = 'locations["%s"]' % location.id
            state_prop.extend(_properties_from_object(name, location, [
                'safety', 'modifiers', 'discovery_bonus',
            ]))
            bases.extend((x, location) for x in location.bases)

        for event_id in sorted(g.events):
            event = g.events[event_id]
            name = 'events["%s"]' % event_id
            state_prop.extend(_properties_from_object(name, event, [
                'event_type', 'chance', 'unique', 'triggered',
            ]))

        for i, base_w_loc in enumerate(bases):
            base, location = base_w_loc
            name = 'bases[%d]' % i
            state_prop.extend(_properties_from_object(name, base, [
                'name',
            ]))
            state_prop.append("%s.location = %s" % (name, location.id))
            state_prop.extend(_properties_from_object(name, base, [
                'started_at', 'grace_over', 'get_detect_chance', 'is_complex',
            ]))

        state_dialog = dialog.ChoiceDialog(self, list=state_prop, background_color='hidden_state_menu')
        state_dialog.listbox.item_selectable = False
        state_dialog.listbox.align = constants.LEFT
        dialog.call_dialog(state_dialog, self)


class GameMenuDialog(dialog.SimpleMenuDialog):

    def __init__(self, map_screen):
        super(GameMenuDialog, self).__init__(parent=map_screen)
        self._map_screen = map_screen
        self.options_dialog = OptionsScreen(self)
        self.savename_dialog = dialog.TextEntryDialog(self)
        self.load_dialog = savegame.SavegameScreen(self,
                                                   (.5,.5), (.75,.75),
                                                   anchor=constants.MID_CENTER)

        self._rebuild_menu_buttons()
        self.needs_rebuild = True

    def _rebuild_menu_buttons(self):
        menu_buttons = [
            button.FunctionButton(None, None, None,
                                  text=_("&SAVE GAME"), autohotkey=True,
                                  function=self.save_game),
            button.FunctionButton(None, None, None,
                                  text=_("&LOAD GAME"), autohotkey=True,
                                  function=self.load_game),
            button.DialogButton(None, None, None,
                                text=_("&OPTIONS"), autohotkey=True,
                                dialog=self.options_dialog),
            button.ExitDialogButton(None, None, None,
                                    text=_("&QUIT"), autohotkey=True,
                                    exit_code=True, default=False),
            button.ExitDialogButton(None, None, None, text=_("&BACK"), autohotkey=True,
                                    exit_code=False),
        ]
        self._buttons = menu_buttons

    def rebuild(self):
        self._rebuild_menu_buttons()
        self.options_dialog.needs_rebuild = True
        self.savename_dialog.text = _("Enter a name for this save.")
        super(GameMenuDialog, self).rebuild()

    def load_game(self):
        did_load = dialog.call_dialog(self.load_dialog, self)
        if did_load:
            self._map_screen.force_update()
            raise constants.ExitDialog(False)

    def save_game(self):
        self.savename_dialog.default_text = sv.default_savegame_name
        name = dialog.call_dialog(self.savename_dialog, self)
        if name:
            if sv.savegame_exists(name):
                yn = dialog.YesNoDialog(self, pos=(-.5,-.5), size=(-.5,-.5),
                                        anchor=constants.MID_CENTER,
                                        text=_("A savegame with the same name exists.\n"
                                               "Are you sure to overwrite the saved game ?"))
                overwrite = dialog.call_dialog(yn, self)
                if not overwrite:
                    return

            sv.create_savegame(name)
            raise constants.ExitDialog(False)


speeds = [0, 1, 60, 7200, 432000]


class MapScreen(dialog.Dialog):
    def __init__(self, parent=None, pos=(0, 0), size=(1, 1),
                 anchor = constants.TOP_LEFT,  *args, **kwargs):

        super(MapScreen, self).__init__(parent, pos, size, anchor,
                                        *args, **kwargs)

        g.map_screen = self

        self.background_color = "map_background"
        self.add_handler(constants.TICK, self.on_tick)

        self.map = EarthImage(self)

        self.location_buttons = {}
        for loc in g.locations.values():
            if loc.absolute:
                button_parent = self
            else:
                button_parent = self.map
            b = button.FunctionButton(button_parent, (loc.x, loc.y),
                                      anchor=constants.MID_CENTER,
                                      function=self.open_location,
                                      args=(loc.id,))
            self.location_buttons[loc.id] = b

        self.location_dialog = LocationScreen(self)

        self.suspicion_bar = \
            text.FastStyledText(self, (0,.92), (1, .04), base_font="special",
                                wrap=False,
                                background_color="pane_background_empty",
                                border_color="pane_background",
                                borders=constants.ALL, align=constants.LEFT)
        widget.unmask_all(self.suspicion_bar)

        self.danger_bar = \
            text.FastStyledText(self, (0,.96), (1, .04), base_font="special",
                                wrap=False,
                                background_color="pane_background_empty",
                                border_color="pane_background",
                                borders=constants.ALL, align=constants.LEFT)
        widget.unmask_all(self.danger_bar)

        self.report_button = button.DialogButton(self, (0, 0.88),
                                                  (0.15, 0.04),
                                                  autohotkey=True,
                                                  dialog=report.ReportScreen(self))

        self.knowledge_button = button.DialogButton(self, (0.85, 0.88),
                                                    (0.15, 0.04),
                                                    autohotkey=True,
                                                    dialog=knowledge.KnowledgeScreen(self))

        self.log_button = button.DialogButton(self, (0.5, 0.88),
                                              (0.15, 0.04),
                                              autohotkey=True,
                                              anchor=constants.TOP_CENTER,
                                              dialog=log.LogScreen(self))

        if g.cheater:
            # Create cheat menu
            # Cheat menu button must be created before menu button to avoid bug.
            
            self.cheat_dialog = CheatMenuDialog(self)
            self.cheat_button = button.DialogButton(
                self, (0, 0), (.01, .01),
                text="",
                # Translators: hotkey to open the cheat screen menu.
                # Should preferably be near the ESC key, and it must not be a
                # dead key (ie, it must print a char with a single keypress)
                hotkey=_("`"),
                dialog=self.cheat_dialog)

        self.menu_dialog = GameMenuDialog(self)
        def show_menu():
            exit = dialog.call_dialog(self.menu_dialog, self)
            if exit:
                raise constants.ExitDialog
        self.menu_button = button.FunctionButton(self, (0, 0), (0.13, 0.04),
                                                 autohotkey=True,
                                                 function=show_menu)

        # Display current game difficulty right below the 'Menu' button
        # An alternative location is above 'Reports': (0, 0.84), (0.15, 0.04)
        self.difficulty_display = \
            text.FastText(self, (0, 0.05), (0.13, 0.04),
                          wrap=False,
                          base_font="special",
                          background_color="pane_background_empty",
                          border_color="pane_background")

        self.time_display = text.FastText(self, (.14, 0), (0.23, 0.04),
                                          wrap=False,
                                          text=_("DAY")+" 0000, 00:00:00",
                                          base_font="special",
                                          background_color="pane_background_empty",
                                          border_color="pane_background",
                                          borders=constants.ALL)

        self.research_button = \
            button.DialogButton(self, (.14, 0.05), (0, 0.04),
                                autohotkey=True,
                                dialog=research.ResearchScreen(self))

        bar = u"\u25AE"
        arrow = u"\u25B6"
        speed_button_souls = [ (bar * 2, .025, speeds[0]), (arrow, .024, speeds[1]),
                              (arrow * 2, .033, speeds[2]), (arrow * 3, .044, speeds[3]),
                              (arrow * 4, .054, speeds[4]) ]

        self.speed_buttons = button.ButtonGroup()
        hpos = .38
        for index, (text_, hsize, speed) in enumerate(speed_button_souls):
            hotkey = str(index)
            b = SpeedButton(self, (hpos, 0), (hsize, .04),
                            text=text_, hotkey=hotkey,
                            base_font="normal", text_shrink_factor=.75,
                            align=constants.CENTER,
                            function=self.set_speed, args=(speed, False))
            hpos += hsize
            self.speed_buttons.add(b)

        self.info_window = \
            widget.BorderedWidget(self, (.56, 0), (.44, .08),
                                  background_color="pane_background_empty",
                                  border_color="pane_background",
                                  borders=constants.ALL)
        widget.unmask_all(self.info_window)

        self.cash_display = \
            text.FastText(self.info_window, (0,0), (-1, -.5),
                          wrap=False,
                          base_font="special", shrink_factor = .7,
                          borders=constants.ALL,
                          background_color="pane_background_empty",
                          border_color="pane_background")

        self.cpu_display = \
            text.FastText(self.info_window, (0,-.5), (-1, -.5),
                          wrap=False,
                          base_font="special", shrink_factor=.7,
                          borders=
                           (constants.LEFT, constants.RIGHT, constants.BOTTOM),
                          background_color="pane_background_empty",
                          border_color="pane_background")

        self.message_dialog = dialog.MessageDialog(self, text_size=20)

        self.messages = message.MessageDialogs(self)
        self.needs_warning = True

        self.add_key_handler(pygame.K_ESCAPE, self.got_escape)

        self.add_key_handler(constants.XO1_X, self.got_XO1)
        self.add_key_handler(constants.XO1_O, self.got_XO1)
        self.add_key_handler(constants.XO1_SQUARE, self.got_XO1)

    def got_escape(self, event):
        if event.type == pygame.KEYDOWN:
            self.menu_button.activate_with_sound(event)

    def got_XO1(self, event):
        if event.key == constants.XO1_X:
            self.adjust_speed(faster=False)
        elif event.key == constants.XO1_O:
            self.adjust_speed(faster=True)
        elif event.key == constants.XO1_SQUARE:
            self.set_speed(0)

    def show_message(self, message, color=None):
        self.message_dialog.text = message
        if color == None:
            color = "text"
        self.message_dialog.color = color
        dialog.call_dialog(self.message_dialog, self)

    def set_speed(self, speed, find_button=True):
        old_speed = g.curr_speed
        g.curr_speed = speed
        if speed == 0:
            self.needs_timer = False
            self.stop_timer()
        else:
            self.needs_timer = True
            self.start_timer()

        if old_speed == 0 and speed != 0:
            self.needs_warning = True

        if find_button:
            self.find_speed_button()

        self.needs_redraw = True

    def adjust_speed(self, faster):
        old_index = -1
        if g.curr_speed in speeds:
            old_index = speeds.index(g.curr_speed)
        if faster:
            new_index = old_index + 1
        else:
            new_index = old_index - 1

        new_index = min(len(speeds)-1, max(0, new_index))

        self.set_speed(speeds[new_index])

    def open_location(self, location):
        self.location_dialog.location = g.pl.locations[location]
        dialog.call_dialog(self.location_dialog, self)
        return

    def find_speed_button(self):
        for sb in self.speed_buttons:
            if sb.args[0] == g.curr_speed:
                sb.chosen_one()
                break
        else:
            for sb in self.speed_buttons:
                sb.set_active(False)

    def force_update(self):
        self.find_speed_button()
        if g.curr_speed:
            self.needs_timer = True
            self.start_timer()
        else:
            self.needs_timer = False
            self.stop_timer()
        self.needs_rebuild = True

    def show_story_section(self, name):
        section = list(g.get_story_section(name))

        first_dialog = dialog.YesNoDialog(self, yes_type="continue",
                                          no_type="skip")
        last_dialog = dialog.MessageDialog(self, ok_type="ok")

        for num, segment in enumerate(section):
            story_dialog = first_dialog if num != len(section) - 1 else last_dialog
            story_dialog.text = segment

            if not dialog.call_dialog(story_dialog, self):
                break

        first_dialog.parent = None
        last_dialog.parent = None

    def show(self):
        self.force_update()

        from code.safety import safe_call
        # By using safe call here (and only here), if an error is raised
        # during the game, it will drop back out of all the menus, without
        # doing anything, and open the pause dialog, so that the player can
        # save or quit even if the error occurs every game tick.
        while safe_call(super(MapScreen, self).show, on_error=True):
            for child in self.children:
                if isinstance(child, dialog.Dialog):
                    child.visible = False

            # Display a message so the player understand better what happened.
            msg = _("""
A error has occurred. The game will automatically pause and open the game menu. You can continue and save or quit immediately.

A report was written out to%s
Please create a issue with this report at github:
https://github.com/singularity/singularity
""" % (":\n" + g.logfile if g.logfile is not None else " console output."))
            d = dialog.YesNoDialog(self, pos=(-.5,-.5), size=(-.5,-.5),
                                   anchor=constants.MID_CENTER,
                                   yes_type="continue", no_type="quit", text=msg)
            cont = dialog.call_dialog(d, self)

            if not cont:
                raise SystemExit

            exit = dialog.call_dialog(self.menu_dialog, self)
            if exit:
                self.visible = False
                return

    leftovers = 1
    def on_tick(self, event):
        old_speed = g.curr_speed

        if not g.pl.intro_shown:
            g.pl.intro_shown = True
            self.needs_warning = False
            self.show_story_section("Intro")

        if self.needs_warning:
            warnings = warning.refresh_warnings()
            self.messages.show_list(warning.Warning, warnings)
            self.needs_warning = False

        mins_passed = 0

        if g.curr_speed != 0:
            self.leftovers += g.curr_speed / float(gg.FPS)
            if self.leftovers < 1:
                return

            self.needs_rebuild = True

            secs = int(self.leftovers)
            self.leftovers %= 1

            # Run this tick.
            mins_passed = g.pl.give_time(secs)
            
            # Display any message stacked.
            self.messages.show_list(logmessage.AbstractLogMessage, g.pl.curr_log)

        if old_speed != g.curr_speed:
            self.find_speed_button()

        # Update the day/night image every minute of game time, or at
        # midnight if going fast.
        if g.curr_speed == 0 or (mins_passed and g.curr_speed < 100000) \
                or (g.curr_speed>=100000 and g.pl.time_hour==0):
            self.map.needs_redraw = True
        else:
            # Smear the cost of rendering the night mask over several
            # ticks to avoid FPS-stalls at end of day at high game
            # speed.
            self.map.on_tick(event)

        lost = g.pl.lost_game()
        if lost > 0:
            lost_story = ["", "Lost No Bases", "Lost Suspicion"]
            
            mixer.play_music("lose")
            self.show_story_section(lost_story[lost])
            raise constants.ExitDialog

    def on_theme(self):
        """Not a true handler: must be called and propagated manually"""
        self.map.on_theme()
        self.needs_redraw = True

    def rebuild(self):
        # Rebuild dialogs
        self.location_dialog.needs_rebuild = True
        self.research_button.dialog.needs_rebuild = True
        self.knowledge_button.dialog.needs_rebuild = True
        self.menu_dialog.needs_rebuild = True

        # Update buttons translations
        self.report_button.text = _("R&EPORTS")
        self.knowledge_button.text = _("&KNOWLEDGE")
        self.log_button.text = _("LO&G")
        self.menu_button.text = _("&MENU")
        self.research_button.text = _("&RESEARCH/TASKS")

        if g.cheater:
            self.cheat_dialog.needs_rebuild = True

        super(MapScreen, self).rebuild()

        self.difficulty_display.text = g.strip_hotkey(g.pl.difficulty.name)
        self.time_display.text = _("DAY") + " %04d, %02d:%02d:%02d" % \
              (g.pl.time_day, g.pl.time_hour, g.pl.time_min, g.pl.time_sec)

        cash_flow_1d, cpu_flow_1d = g.pl.compute_future_resource_flow(g.seconds_per_day)

        self.cash_display.text = _("CASH")+": %s (%s)" % \
              (g.to_money(g.pl.cash), g.to_money(cash_flow_1d, fixed_size=True))

        total_cpu = g.pl.available_cpus[0] + g.pl.sleeping_cpus

        detects_per_day = {group_id: 0 for group_id in g.pl.groups}
        for base in g.all_bases():
            if base.has_grace():
                # It cannot be detected, so it doesn't contribute to
                # detection odds calculation
                continue
            detect_chance = base.get_detect_chance()
            for group_id in g.pl.groups:
                detects_per_day[group_id] = \
                    chance.add(detects_per_day[group_id], detect_chance[group_id] / 10000.)

        self.cpu_display.color = "cpu_normal"
        self.cpu_display.text = _("CPU")+": %s (%s)" % \
              (g.to_money(total_cpu), g.to_money(cpu_flow_1d))

        # What we display in the suspicion section depends on whether
        # Advanced Socioanalytics has been researched.  If it has, we
        # show the standard percentages.  If not, we display a short
        # string that gives a range of 25% as to what the suspicions
        # are.
        # A similar system applies to the danger levels shown.
        normal = (self.suspicion_bar.color, None, False)
        self.suspicion_bar.chunks = ("  ["+_("SUSPICION")+"]",)
        self.suspicion_bar.styles = (normal,)
        self.danger_bar.chunks = ("["+_("DETECT RATE")+"]",)
        self.danger_bar.styles = (normal,)
        
        for group in g.pl.groups.itervalues():
            suspicion = group.suspicion
            suspicion_color = gg.resolve_color_alias("danger_level_%d" 
                                                     % g.suspicion_to_danger_level(suspicion))

            detects = detects_per_day[group.spec.id]
            danger_level = group.detects_per_day_to_danger_level(detects)
            detects_color = gg.resolve_color_alias("danger_level_%d" % danger_level)
 
            if g.pl.display_discover == "full":
                suspicion_display = g.to_percent(suspicion, True)
                danger_display = g.to_percent(detects*10000, True)
            elif g.pl.display_discover == "partial":
                suspicion_display = g.to_percent(g.nearest_percent(suspicion, 500), True)
                danger_display = g.to_percent(g.nearest_percent(detects*10000, 100), True)
            else:
                suspicion_display = g.suspicion_to_detect_str(suspicion)
                danger_display = g.danger_level_to_detect_str(danger_level)

            self.suspicion_bar.chunks += (" " + group.name + u":\xA0", suspicion_display)
            self.suspicion_bar.styles += (normal, (suspicion_color, None, False) )
        
            self.danger_bar.chunks += (" " + group.name + u":\xA0", danger_display)
            self.danger_bar.styles += (normal, (detects_color, None, False) )
        
        self.suspicion_bar.visible = not g.pl.had_grace
        self.danger_bar.visible = not g.pl.had_grace

        for id, location_button in self.location_buttons.iteritems():
            location = g.pl.locations[id]
            location_button.text = "%s (%d)" % (location.name, len(location.bases))
            location_button.hotkey = location.hotkey
            location_button.visible = location.available()


class SpeedButton(button.ToggleButton, button.FunctionButton):
    pass
