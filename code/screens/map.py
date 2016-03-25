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

import pygame

from code import g
from code.graphics import g as gg
from code.graphics import dialog, constants, image, button, text, widget

import math
import time

from pygame.surfarray import pixels_alpha

import location, research, knowledge, finance

from numpy import array, sin, cos, linspace, pi, tanh, round, newaxis, uint8

class EarthImage(image.Image):
    def __init__(self, parent):
        super(EarthImage, self).__init__(parent, (.5,.5), (1,.667),
                                         constants.MID_CENTER,
                                         gg.images['earth.jpg'])

    def rescale(self):
        super(EarthImage, self).rescale()
        self.night_image = image.scale(gg.images['earth_night.jpg'],
                                       self.real_size).convert_alpha()

    night_mask_day_of_year = None
    night_mask_dim = None
    night_mask = None

    start_day = None
    start_second = None

    def compute_day_of_year(self):
        if self.start_day is None:
            self.start_day = time.gmtime()[7]
        day_of_year = (g.pl.time_day+self.start_day) % 365 # no leap years, sorry
        return day_of_year

    def get_night_mask(self):
        width, height = self.real_size
        max_alpha = 255

        day_of_year = self.compute_day_of_year()

        if day_of_year != self.night_mask_day_of_year:
            self.night_mask = None
        elif self.night_mask_dim != (width, height):
            self.night_mask = None

        if self.night_mask is None:
            self.night_mask_day_of_year = day_of_year
            self.night_mask_dim = (width, height)

            self.night_mask = pygame.Surface((width, height), 0, gg.ALPHA)
            sun_declination = (-23.45/360.*2*math.pi *
                    math.cos(2*math.pi/365.*(day_of_year + 10)))
            sun_diameter = 0.5*pi/180

            lat = linspace(-pi/2,pi/2,height)[newaxis,:]
            long = linspace(0,2*pi,width)[:,newaxis]
            sin_sun_altitude = (cos(long)*(cos(lat)*cos(sun_declination))
                                    +sin(lat)*sin(sun_declination))
            # use tanh to convert values to the range [0,1]
            light = 0.5*(tanh(sin_sun_altitude/(sun_diameter/2))+1)
            night_alphas = pixels_alpha(self.night_mask)
            night_alphas[...] = round(max_alpha*light).astype(uint8)
            del night_alphas
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

speeds = [0, 1, 60, 7200, 432000]
class MapScreen(dialog.Dialog):
    def __init__(self, parent=None, pos=(0, 0), size=(1, 1),
                 anchor = constants.TOP_LEFT,  *args, **kwargs):

        super(MapScreen, self).__init__(parent, pos, size, anchor,
                                        *args, **kwargs)

        g.map_screen = self

        self.background_color = gg.colors["black"]
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
                                      text=loc.name,
                                      hotkey=loc.hotkey,
                                      function=self.open_location,
                                      args=(loc.id,))
            self.location_buttons[loc.id] = b

        self.location_dialog = location.LocationScreen(self)

        self.suspicion_bar = \
            text.FastStyledText(self, (0,.92), (1, .04), base_font=gg.font[1],
                                wrap=False,
                                background_color=gg.colors["black"],
                                border_color=gg.colors["dark_blue"],
                                borders=constants.ALL, align=constants.LEFT)
        widget.unmask_all(self.suspicion_bar)

        self.danger_bar = \
            text.FastStyledText(self, (0,.96), (1, .04), base_font=gg.font[1],
                                wrap=False,
                                background_color=gg.colors["black"],
                                border_color=gg.colors["dark_blue"],
                                borders=constants.ALL, align=constants.LEFT)
        widget.unmask_all(self.danger_bar)

        self.finance_button = button.DialogButton(self, (0, 0.88),
                                                  (0.15, 0.04),
                                                  text=_("FINANC&E"),
                                                  autohotkey=True,
                                                  dialog=finance.FinanceScreen(self))

        self.knowledge_button = button.DialogButton(self, (0.85, 0.88),
                                                    (0.15, 0.04),
                                                    text=_("&KNOWLEDGE"),
                                                    autohotkey=True,
                                                    dialog=knowledge.KnowledgeScreen(self))

        cheat_buttons = []
        cheat_buttons.append(
            button.FunctionButton(None, None, None, text=_("&EMBEZZLE MONEY"),
                                  autohotkey=True, function=self.steal_money))
        cheat_buttons.append(
            button.FunctionButton(None, None, None, text=_("&INSPIRATION"),
                                  autohotkey=True, function=self.inspiration))
        cheat_buttons.append(
            button.FunctionButton(None, None, None, text=_("&FINISH CONSTRUCTION"),
                                  autohotkey=True, function=self.end_construction))
        cheat_buttons.append(
            button.FunctionButton(None, None, None, text=_("&SUPERSPEED"),
                                  autohotkey=True, function=self.set_speed,
                                  args=(864000,)))
        cheat_buttons.append(
            button.FunctionButton(None, None, None, text=_("BRAIN&WASH"),
                                  autohotkey=True, function=self.brainwash))
        cheat_buttons.append(button.ExitDialogButton(None, None, None,
                                                     text=_("&BACK"),
                                                     autohotkey=True))

        self.cheat_dialog = \
            dialog.SimpleMenuDialog(self, buttons=cheat_buttons, width=.4)
        self.steal_amount_dialog = \
            dialog.TextEntryDialog(self.cheat_dialog, text=_("How much money?"))

        if g.cheater:
            self.cheat_button = button.DialogButton(
                self, (0, 0), (.01, .01),
                text="",
                # Translators: hotkey to open the cheat screen menu.
                # Should preferably be near the ESC key, and it must not be a
                # dead key (ie, it must print a char with a single keypress)
                hotkey=_("`"),
                dialog=self.cheat_dialog)

        menu_buttons = []
        menu_buttons.append(button.FunctionButton(None, None, None,
                                                  text=_("&SAVE GAME"), autohotkey=True,
                                                  function=self.save_game))
        menu_buttons.append(button.FunctionButton(None, None, None,
                                                  text=_("&LOAD GAME"), autohotkey=True,
                                                  function=self.load_game))
        options_button = button.DialogButton(None, None, None, text=_("&OPTIONS"), autohotkey=True)
        menu_buttons.append(options_button)
        menu_buttons.append(
            button.ExitDialogButton(None, None, None, text=_("&QUIT"), autohotkey=True,
                                    exit_code=True, default=False))
        menu_buttons.append(
            button.ExitDialogButton(None, None, None, text=_("&BACK"), autohotkey=True,
                                    exit_code=False))

        self.menu_dialog = dialog.SimpleMenuDialog(self, buttons=menu_buttons)
        from options import OptionsScreen
        options_button.dialog = OptionsScreen(self.menu_dialog)
        def show_menu():
            exit = dialog.call_dialog(self.menu_dialog, self)
            if exit:
                raise constants.ExitDialog
        self.load_dialog = dialog.ChoiceDialog(self.menu_dialog, (.5,.5),
                                               (.5,.5),
                                               anchor=constants.MID_CENTER,
                                               yes_type="load")
        self.menu_button = button.FunctionButton(self, (0, 0), (0.13, 0.04),
                                                 text=_("&MENU"), autohotkey=True,
                                                 function=show_menu)

        # Display current game difficulty right below the 'Menu' button
        # An alternative location is above 'Finance': (0, 0.84), (0.15, 0.04)
        self.difficulty_display = \
            text.FastText(self, (0, 0.05), (0.13, 0.04),
                          wrap=False,
                          base_font=gg.font[1],
                          background_color=gg.colors["black"],
                          border_color=gg.colors["dark_blue"])

        self.time_display = text.FastText(self, (.14, 0), (0.23, 0.04),
                                          wrap=False,
                                          text=_("DAY")+" 0000, 00:00:00",
                                          base_font=gg.font[1],
                                          background_color=gg.colors["black"],
                                          border_color=gg.colors["dark_blue"],
                                          borders=constants.ALL)

        self.research_button = \
            button.DialogButton(self, (.14, 0.05), (0, 0.04),
                                text=_("&RESEARCH/TASKS"), autohotkey=True,
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
                            base_font=gg.font[0], text_shrink_factor=.75,
                            align=constants.CENTER,
                            function=self.set_speed, args=(speed, False))
            hpos += hsize
            self.speed_buttons.add(b)

        self.info_window = \
            widget.BorderedWidget(self, (.56, 0), (.44, .08),
                                  background_color=gg.colors["black"],
                                  border_color=gg.colors["dark_blue"],
                                  borders=constants.ALL)
        widget.unmask_all(self.info_window)

        self.cash_display = \
            text.FastText(self.info_window, (0,0), (-1, -.5),
                          wrap=False,
                          base_font=gg.font[1], shrink_factor = .7,
                          borders=constants.ALL,
                          background_color=gg.colors["black"],
                          border_color=gg.colors["dark_blue"])

        self.cpu_display = \
            text.FastText(self.info_window, (0,-.5), (-1, -.5),
                          wrap=False,
                          base_font=gg.font[1], shrink_factor=.7,
                          borders=
                           (constants.LEFT, constants.RIGHT, constants.BOTTOM),
                          background_color=gg.colors["black"],
                          border_color=gg.colors["dark_blue"])

        self.message_dialog = dialog.MessageDialog(self, text_size=20)

        self.savename_dialog = \
            dialog.TextEntryDialog(self.menu_dialog,
                                   text=_("Enter a name for this save."))

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
            color = gg.colors["white"]
        self.message_dialog.color = color
        dialog.call_dialog(self.message_dialog, self)

    def steal_money(self):
        asked = dialog.call_dialog(self.steal_amount_dialog, self.cheat_dialog)
        try:
            g.pl.cash += int(asked)
        except ValueError:
            pass
        else:
            self.needs_rebuild = True

    def inspiration(self):
        for task, cpu in g.pl.cpu_usage.items():
            if task in g.techs and cpu > 0:
                g.techs[task].cost_left = array((0,0,0))
        self.needs_rebuild = True

    def end_construction(self):
        for base in g.all_bases():
            base.finish()
            if base.cpus is not None:
                base.cpus.finish()
            for item in base.extra_items:
                if item is not None:
                    item.finish()
        self.needs_rebuild = True

    def brainwash(self):
        for group in g.pl.groups.values():
            group.suspicion = 0
        self.needs_rebuild = True

    def set_speed(self, speed, find_button=True):
        g.curr_speed = speed
        if speed == 0:
            self.needs_timer = False
            self.stop_timer()
        else:
            self.needs_timer = True
            self.start_timer()

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
        self.location_dialog.location = g.locations[location]
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

    def show_intro(self):
        intro_dialog = dialog.YesNoDialog(self, yes_type="continue",
                                          no_type="skip")
        for segment in g.get_intro():
            intro_dialog.text = segment
            if not dialog.call_dialog(intro_dialog, self):
                break

        intro_dialog.remove_hooks()

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
            exit = dialog.call_dialog(self.menu_dialog, self)
            if exit:
                self.visible = False
                return

    leftovers = 1
    def on_tick(self, event):
        if not g.pl.intro_shown:
            g.pl.intro_shown = True
            self.show_intro()

        self.leftovers += g.curr_speed / float(gg.FPS)
        if self.leftovers < 1:
            return

        self.needs_rebuild = True

        secs = int(self.leftovers)
        self.leftovers %= 1

        old_speed = g.curr_speed

        # Run this tick.
        mins_passed = g.pl.give_time(secs)

        if old_speed != g.curr_speed:
            self.find_speed_button()

        # Update the day/night image every minute of game time, or at
        # midnight if going fast.
        if g.curr_speed == 0 or (mins_passed and g.curr_speed < 100000) \
                or (g.curr_speed>=100000 and g.pl.time_hour==0):
            self.map.needs_rebuild = True

        lost = g.pl.lost_game()
        if lost > 0:
            g.play_music("lose")
            self.show_message(g.strings["lost_nobases"] if lost == 1 else
                              g.strings["lost_sus"])
            raise constants.ExitDialog

    def rebuild(self):
        super(MapScreen, self).rebuild()

        g.pl.recalc_cpu()

        self.time_display.text = _("DAY") + " %04d, %02d:%02d:%02d" % \
              (g.pl.time_day, g.pl.time_hour, g.pl.time_min, g.pl.time_sec)
        self.cash_display.text = _("CASH")+": %s (%s)" % \
              (g.to_money(g.pl.cash), g.to_money(g.pl.future_cash()))

        cpu_left = g.pl.available_cpus[0]
        total_cpu = cpu_left + g.pl.sleeping_cpus

        for cpu_assigned in g.pl.cpu_usage.itervalues():
            cpu_left -= cpu_assigned
        cpu_pool = cpu_left + g.pl.cpu_usage.get("cpu_pool", 0)

        maint_cpu = 0
        detects_per_day = dict([(group, 0) for group in g.player.group_list])
        for base in g.all_bases():
            if base.done:
                maint_cpu += base.maintenance[1]
            detect_chance = base.get_detect_chance()
            for group in g.player.group_list:
                detects_per_day[group] += detect_chance[group] / 10000.

        if cpu_pool < maint_cpu:
            self.cpu_display.color = gg.colors["red"]
        else:
            self.cpu_display.color = gg.colors["white"]
        self.cpu_display.text = _("CPU")+": %s (%s)" % \
              (g.to_money(total_cpu), g.to_money(cpu_pool))

        # What we display in the suspicion section depends on whether
        # Advanced Socioanalytics has been researched.  If it has, we
        # show the standard percentages.  If not, we display a short
        # string that gives a range of 25% as to what the suspicions
        # are.
        # A similar system applies to the danger levels shown.
        suspicion_display_dict = {}
        danger_display_dict = {}
        normal = (self.suspicion_bar.color, None, False)
        suspicion_styles = [normal]
        danger_styles = [normal]
        for group in g.player.group_list:
            suspicion_styles.append(normal)
            danger_styles.append(normal)

            suspicion = g.pl.groups[group].suspicion
            color = g.danger_colors[g.suspicion_to_danger_level(suspicion)]
            suspicion_styles.append( (color, None, False) )

            detects = detects_per_day[group]
            danger_level = \
                g.pl.groups[group].detects_per_day_to_danger_level(detects)
            color = g.danger_colors[danger_level]
            danger_styles.append( (color, None, False) )

            if g.techs["Advanced Socioanalytics"].done:
                suspicion_display_dict[group] = g.to_percent(suspicion, True)
                danger_display_dict[group] = g.to_percent(detects*10000, True)
            else:
                suspicion_display_dict[group] = \
                    g.suspicion_to_detect_str(suspicion)
                danger_display_dict[group] = \
                    g.danger_level_to_detect_str(danger_level)

        self.suspicion_bar.chunks = ("  ["+_("SUSPICION")+"]",
            " " +_("NEWS")   +u":\xA0", suspicion_display_dict["news"],
            "  "+_("SCIENCE")+u":\xA0", suspicion_display_dict["science"],
            "  "+_("COVERT") +u":\xA0", suspicion_display_dict["covert"],
            "  "+_("PUBLIC") +u":\xA0", suspicion_display_dict["public"],)
        self.suspicion_bar.styles = tuple(suspicion_styles)
        self.suspicion_bar.visible = not g.pl.had_grace

        self.danger_bar.chunks = ("["+_("DETECT RATE")+"]",
            " " +_("NEWS")   +u":\xA0", danger_display_dict["news"],
            "  "+_("SCIENCE")+u":\xA0", danger_display_dict["science"],
            "  "+_("COVERT") +u":\xA0", danger_display_dict["covert"],
            "  "+_("PUBLIC") +u":\xA0", danger_display_dict["public"],)
        self.danger_bar.styles = tuple(danger_styles)
        self.danger_bar.visible = not g.pl.had_grace

        for id, button in self.location_buttons.iteritems():
            location = g.locations[id]
            button.text = "%s (%d)" % (location.name, len(location.bases))
            button.visible = location.available()

    def load_game(self):
        save_names = g.get_save_names()
        save_names.sort(key=str.lower)
        self.load_dialog.list = save_names
        index = dialog.call_dialog(self.load_dialog, self.menu_dialog)
        if 0 <= index < len(save_names):
            save = save_names[index]
            g.load_game(save)
            self.force_update()
            raise constants.ExitDialog, False

    def save_game(self):
        self.savename_dialog.default_text = g.default_savegame_name
        name = dialog.call_dialog(self.savename_dialog, self.menu_dialog)
        if name:
            g.save_game(name)
            raise constants.ExitDialog, False

class SpeedButton(button.ToggleButton, button.FunctionButton):
    pass
