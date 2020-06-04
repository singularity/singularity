#file: options.py
#Copyright (C) 2005 Evil Mr Henry, Phil Bordelon, FunnyMan3595, MestreLion
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

#This file is used to display the options screen.

from __future__ import absolute_import

import os
import sys
import pygame
import json

from singularity.code.graphics import constants, widget, dialog, button, listbox, slider, text, theme, g as gg
from singularity.code import g, dirs, i18n, mixer, data, warning
from singularity.code.pycompat import *


class OptionsScreen(dialog.FocusDialog, dialog.YesNoDialog):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("yes_type", N_("&OK"))
        kwargs.setdefault("no_type", N_("&CANCEL"))
        super(OptionsScreen, self).__init__(*args, **kwargs)
        self.yes_button.function = self.check_restart

        self.size = (.80, .85)
        self.pos = (.5, .5)
        self.anchor = constants.MID_CENTER
        self.background_color = "options_background"

        # Tabs panel
        self.general_pane   = GeneralPane(None, (0, .1), (.80, .75))
        self.video_pane     = VideoPane(None, (0, .1), (.80, .75))
        self.audio_pane     = AudioPane(None, (0, .1), (.80, .75))
        self.gui_pane       = GUIPane(None, (0, .1), (.80, .75))

        self.tabs_panes = (self.general_pane, self.video_pane, self.audio_pane, self.gui_pane)

        # Tabs buttons
        self.tabs_buttons = button.ButtonGroup()

        self.general_tab = OptionButton(self, (-.135, .01), (-.240, .05),
                                        autotranslate=True,
                                        text=N_("&General"),
                                        anchor=constants.TOP_CENTER,
                                        function=self.set_tabs_pane, args=(self.general_pane,))
        self.tabs_buttons.add(self.general_tab)

        self.video_tab = OptionButton(self, (-.3790, .01), (-.240, .05),
                                      autotranslate=True,
                                      text=N_("&Video"),
                                      anchor = constants.TOP_CENTER,
                                      function=self.set_tabs_pane, args=(self.video_pane,))
        self.tabs_buttons.add(self.video_tab)

        self.audio_tab = OptionButton(self, (-.6230, .01), (-.240, .05),
                                      autotranslate=True,
                                      text=N_("&Audio"),
                                      anchor=constants.TOP_CENTER,
                                      function=self.set_tabs_pane, args=(self.audio_pane,))
        self.tabs_buttons.add(self.audio_tab)

        self.gui_tab = OptionButton(self, (-.865, .01), (-.235, .05),
                                    autotranslate=True,
                                    text=N_("&Interface"),
                                    anchor=constants.TOP_CENTER,
                                    function=self.set_tabs_pane, args=(self.gui_pane,))
        self.tabs_buttons.add(self.gui_tab)

        self.general_tab.chosen_one()
        self.set_tabs_pane(self.general_pane)

        # YesNoDialog buttons
        self.yes_button.size = (.15, .05)
        self.no_button.size = (.15, .05)

    def rebuild(self):
        # The tabs do not always have a parent, so the automatic "needs_rebuild" magic
        # does not work.  Do it manually instead.
        for pane in self.tabs_panes:
            pane.needs_rebuild = True

        super(OptionsScreen, self).rebuild()

    def reconfig(self):
        # The tabs do not always have a parent, so the automatic "needs_reconfig" magic
        # does not work.  Do it manually instead.
        for pane in self.tabs_panes:
            pane.needs_reconfig = True
        super(OptionsScreen, self).reconfig()

    def show(self):
        self.initial_options = dict(
            fullscreen      = gg.fullscreen,
            grab            = pygame.event.get_grab(),
            daynight        = g.daynight,
            resolution      = gg.screen_size,
            language        = i18n.language,
            theme           = theme.current.id,
            sound           = not mixer.nosound,
            gui_volume      = mixer.get_volume("gui"),
            music_volume    = mixer.get_volume("music"),
            soundbuf        = mixer.get_soundbuf(),
            warnings        = {warn.id: warn.active for warn in warning.warnings.values()}
        )

        self.set_options(self.initial_options)

        retval = super(OptionsScreen, self).show()
        if retval:
            self.apply_options()
            save_options()

        else:
            # Cancel, revert all options to initial state
            self.set_options(self.initial_options)

        return retval

    def set_tabs_pane(self, tabs_pane):
        for pane in self.tabs_panes:
            pane.parent = None

        tabs_pane.parent = self

    def set_options(self, options):
        for pane in self.tabs_panes:
            pane.set_options(options)

    def apply_options(self):
        for pane in self.tabs_panes:
            pane.apply_options()

    def check_restart(self):
        # Test all changes that require a restart. Currently, none.
        # We keep it for future need...
        need_restart = False

        # Add restart test here.

        if not need_restart:
            # No restart required. Simply exit the dialog respecting all hooks
            self.yes_button.exit_dialog()
            return

        # Ask user about a restart
        ask_restart = dialog.YesNoDialog(
                self,
                pos=(-.50, -.50),
                anchor=constants.MID_CENTER,
                text=_(
"""You must restart for some of the changes to be fully applied.\n
Would you like to restart the game now?"""),)
        if dialog.call_dialog(ask_restart, self):
            # YES, go for it
            #TODO: check if there is an ongoing game, save it under a special
            #      name and automatically load it after restart using a custom
            #      command-line argument
            save_options()
            restart()
        else:
            # NO, revert "restart-able" changes
            pass

class GeneralPane(widget.Widget):
    def __init__(self, *args, **kwargs):

        super(GeneralPane, self).__init__(*args, **kwargs)

        self.language_label = text.Text(self, (.01, .01), (.14, .05),
                                        autotranslate=True,
                                        text=N_("Language:"),
                                        align=constants.LEFT,
                                        background_color="clear")

        self.languages = get_languages_list()
        self.language_choice = \
            listbox.UpdateListbox(self, (.16, .01), (.20, .25),
                                  list=[lang[1] for lang in self.languages],
                                  update_func=self.set_language)

        self.theme_label = text.Text(self, (.46, .01), (.09, .05),
                                     autotranslate=True,
                                     text=N_("Theme:"),
                                     align=constants.LEFT,
                                     background_color="clear",
                                     )

        self.theme_choice = \
            listbox.UpdateListbox(self, (.56, .01), (.20, .25),
                                  update_func=theme.set_theme,
                                  list_pos=theme.get_theme_pos())

    def rebuild(self):
        self.theme_choice.list = theme.get_theme_list()

        super(GeneralPane, self).rebuild()

    def set_options(self, options):
        self.language_choice.list_pos = [i for i, (code, __)
                                         in enumerate(self.languages)
                                         if code == options['language']][0] or 0
        self.set_language(self.language_choice.list_pos)

        self.theme_choice.list_pos = theme.get_theme_pos()
        theme.set_theme(options['theme'], force_reload=True)

    def apply_options(self):
        pass

    def set_language(self, list_pos):
        if not getattr(self, "language_choice", None):
            return # Not yet initialized.

        if 0 <= list_pos < len(self.language_choice.list):
            language = self.languages[list_pos][0]
            if i18n.language != language:
                set_language_properly(language)


class VideoPane(widget.Widget):
    def __init__(self, *args, **kwargs):
        super(VideoPane, self).__init__(*args, **kwargs)

        self.resolution_initialized = False

        self.resolution_label = text.Text(self, (.01, .01), (.14, .05),
                                          autotranslate=True,
                                          text=N_("Resolution:"),
                                          align=constants.LEFT,
                                          background_color="clear")

        self.resolution_choice = \
            listbox.UpdateListbox(self, (.16, .01), (.20, .25),
                                  update_func=self.update_resolution)

        self.resolution_custom = button.HotkeyText(self, (.01, .28), (.14, .05),
                                                   autotranslate=True,
                                                   text=N_("&Custom:"),
                                                   align=constants.LEFT,
                                                   background_color="clear")

        self.resolution_custom_horiz = \
            text.EditableText(self, (.16, .28), (.14, .05),
                              text=str(gg.default_screen_size[0]),
                              allowed_characters=constants.DIGIT_CHARS,
                              borders=constants.ALL)

        self.resolution_custom_X = text.Text(self,
                                             (.30, .28),
                                             (.02, .05),
                                             text="X",
                                             base_font="special",
                                             background_color="clear")

        self.resolution_custom_vert = \
            text.EditableText(self, (.32, .28), (.14, .05),
                              text=str(gg.default_screen_size[1]),
                              allowed_characters=constants.DIGIT_CHARS,
                              borders=constants.ALL)

        self.resolution_custom_ok = button.FunctionButton(self, (.47, .28), (.14, .05),
                                                          autotranslate=True,
                                                          autohotkey=False,
                                                          text=N_("OK"),
                                                          function=self.set_resolution_custom)
        self.resolution_custom.hotkey_target = self.resolution_custom_ok

        self.fullscreen_label = button.HotkeyText(self, (.40, .01), (.30, .05),
                                                  autotranslate=True,
                                                  text=N_("&Fullscreen:"),
                                                  align=constants.LEFT,
                                                  background_color="clear")
        self.fullscreen_toggle = OptionButton(self, (.715, .01), (.07, .05),
                                              text_shrink_factor=.75,
                                              force_underline=-1,
                                              function=self.set_fullscreen,
                                              args=(button.TOGGLE_VALUE,))
        self.fullscreen_label.hotkey_target = self.fullscreen_toggle

        self.daynight_label = button.HotkeyText(self, (.40, .08), (.30, .05),
                                                autotranslate=True,
                                                text=N_("Da&y/night display:"),
                                                align=constants.LEFT,
                                                background_color="clear")
        self.daynight_toggle = OptionButton(self, (.715, .08), (.07, .05),
                                            text_shrink_factor=.75,
                                            force_underline=-1,
                                            function=self.set_daynight,
                                            args=(button.TOGGLE_VALUE,))
        self.daynight_label.hotkey_target = self.daynight_toggle

        self.grab_label = button.HotkeyText(self, (.40, .15), (.30, .05),
                                            autotranslate=True,
                                            text=N_("&Mouse grab:"),
                                            align=constants.LEFT,
                                            background_color="clear")
        self.grab_toggle = OptionButton(self, (.715, .15), (.07, .05),
                                        text_shrink_factor=.75,
                                        force_underline=-1,
                                        function=self.set_grab,
                                        args=(button.TOGGLE_VALUE,))
        self.grab_label.hotkey_target = self.grab_toggle

    def resize(self):
        super(VideoPane, self).resize()
        self.update_resolution_list()

    def rebuild(self):
        self.update_resolution_list()

        if gg.fullscreen:
            self.fullscreen_toggle.text = _("YES")
        else:
            self.fullscreen_toggle.text = _("NO")

        if pygame.event.get_grab():
            self.grab_toggle.text = _("YES")
        else:
            self.grab_toggle.text = _("NO")

        if g.daynight:
            self.daynight_toggle.text = _("YES")
        else:
            self.daynight_toggle.text = _("NO")

        super(VideoPane, self).rebuild()

    def set_options(self, options):
        self.set_fullscreen(options['fullscreen'])
        self.fullscreen_toggle.set_active(options['fullscreen'])

        self.set_grab(options['grab'])
        self.grab_toggle.set_active(options['grab'])

        self.set_daynight(options['daynight'])
        self.daynight_toggle.set_active(options['daynight'])

        self.update_resolution_list(options['resolution'])
        self.set_resolution(options['resolution'])

    def apply_options(self):
        # Apply CUSTOM choice.
        if self.resolution_choice.list_pos == 0:
            try:
                old_size = gg.screen_size
                gg.set_screen_size((int(self.resolution_custom_horiz.text),
                                    int(self.resolution_custom_vert.text)))
                if gg.screen_size != old_size:
                    dialog.Dialog.top.needs_resize = True
            except ValueError:
                pass

    def update_resolution_list(self, current_res=None):
        self.resolution_initialized = False

        if (current_res == None):
            current_res = (int(gg.screen_size[0]), int(gg.screen_size[1]))

        self.resolutions = gg.get_screen_size_list()
        self.resolution_choice.list = [_("CUSTOM")] + ["%sx%s" % res for res in self.resolutions]

        custom = True
        for i, res in enumerate(self.resolutions):
            if res == current_res:
                self.resolution_choice.list_pos = i + 1
                custom = False
        if custom:
            self.resolution_choice.list_pos = 0
            self.resolution_custom_horiz.text = str(current_res[0])
            self.resolution_custom_vert.text = str(current_res[1])

        self.resolution_initialized = True

    def set_fullscreen(self, value):
        if value:
            self.fullscreen_toggle.text = _("YES")
        else:
            self.fullscreen_toggle.text = _("NO")

        if gg.fullscreen != value:
            gg.set_fullscreen(value)
            dialog.Dialog.top.needs_resize = True

    def set_grab(self, value):
        if value:
            self.grab_toggle.text = _("YES")
        else:
            self.grab_toggle.text = _("NO")
        pygame.event.set_grab(value)

    def set_daynight(self, value):
        if value:
            self.daynight_toggle.text = _("YES")
        else:
            self.daynight_toggle.text = _("NO")
        g.daynight = value

    def set_resolution(self, value):
        if gg.screen_size != value:
            gg.set_screen_size(value)
            gg.set_mode()
            dialog.Dialog.top.needs_resize = True

    def update_resolution(self, list_pos):
        if not self.resolution_initialized:
            return # Not yet initialized.

        if (list_pos == 0):
            self.set_resolution_custom()
        else:
            res = self.resolutions[list_pos - 1]
            self.set_resolution(res)

    def set_resolution_custom(self):
        try:
            screen_size = (int(self.resolution_custom_horiz.text),
                           int(self.resolution_custom_vert.text))
            self.set_resolution(screen_size)
            self.resolution_choice.list_pos = 0
        except ValueError:
            pass


class AudioPane(widget.Widget):
    def __init__(self, *args, **kwargs):
        super(AudioPane, self).__init__(*args, **kwargs)

        self.sound_label = button.HotkeyText(self, (-.49, .01), (.10, .05),
                                             autotranslate=True,
                                             text=N_("&Sound:"),
                                             anchor=constants.TOP_RIGHT,
                                             align=constants.LEFT,
                                             autohotkey=True,
                                             background_color="clear")
        self.sound_toggle = OptionButton(self, (-.51, .01), (.07, .05),
                                         anchor = constants.TOP_LEFT,
                                         text_shrink_factor=.75,
                                         force_underline=-1,
                                         function=self.set_sound,
                                         args=(button.TOGGLE_VALUE,))
        self.sound_label.hotkey_target = self.sound_toggle

        self.gui_label = text.Text(self, (.01, .08), (.22, .05),
                                   autotranslate=True,
                                   text=N_("GUI Volume:"),
                                   anchor=constants.TOP_LEFT,
                                   align=constants.LEFT,
                                   background_color="clear")
        self.gui_slider = slider.UpdateSlider(self, (.24, .08), (.545, .05),
                                              anchor = constants.TOP_LEFT,
                                              horizontal=True, priority=150,
                                              slider_max=100, slider_size=5)
        self.gui_slider.update_func = self.on_gui_volume_change

        self.music_label = text.Text(self, (.01, .15), (.22, .05),
                                     autotranslate=True,
                                     text=N_("Music Volume:"),
                                     anchor=constants.TOP_LEFT,
                                     align=constants.LEFT,
                                     background_color="clear")
        self.music_slider = slider.UpdateSlider(self, (.24, .15), (.545, .05),
                                                anchor = constants.TOP_LEFT,
                                                horizontal=True, priority=150,
                                                slider_max=100, slider_size=5)
        self.music_slider.update_func = self.on_music_volume_change

        self.soundbuf_label = text.Text(self, (.01, .22), (.25, .05),
                                        autotranslate=True,
                                        text=N_("Sound buffering:"),
                                        align=constants.LEFT,
                                        background_color="clear")
        self.soundbuf_group = button.ButtonGroup()

        self.soundbuf_low = OptionButton(self, (.24, .22), (.145, .05),
                                         text=_("&LOW"), autotranslate=True,
                                         function=self.set_soundbuf,
                                         args=(1024,))
        self.soundbuf_group.add(self.soundbuf_low)

        self.soundbuf_normal = OptionButton(self, (.425, .22), (.175, .05),
                                            text=_("&NORMAL"), autotranslate=True,
                                            function=self.set_soundbuf,
                                            args=(1024*2,))
        self.soundbuf_group.add(self.soundbuf_normal)

        self.soundbuf_high = OptionButton(self, (.64, .22), (.145, .05),
                                          text=_("&HIGH"), autotranslate=True,
                                          function=self.set_soundbuf,
                                          args=(1024*4,))
        self.soundbuf_group.add(self.soundbuf_high)

    def rebuild(self):
        if not mixer.nosound:
            self.sound_toggle.text = _("YES")
        else:
            self.sound_toggle.text = _("NO")

        super(AudioPane, self).rebuild()

    def set_options(self, options):
        self.set_sound(options['sound'])
        self.sound_toggle.set_active(options['sound'])

        self.set_soundbuf(options["soundbuf"])
        if (options["soundbuf"] == 1024*1):
            self.soundbuf_low.chosen_one()
        elif (options["soundbuf"] == 1024*2):
            self.soundbuf_normal.chosen_one()
        elif (options["soundbuf"] == 1024*4):
            self.soundbuf_high.chosen_one()

        self.gui_slider.slider_pos = options["gui_volume"]
        self.music_slider.slider_pos = options["music_volume"]

    def apply_options(self):
        pass

    def set_sound(self, value):
        if value:
            self.sound_toggle.text = _("YES")
        else:
            self.sound_toggle.text = _("NO")

        mixer.set_sound(value)

    def on_gui_volume_change(self, value):
        mixer.set_volume("gui", value)

    def on_music_volume_change(self, value):
        mixer.set_volume("music", value)

    #TODO: Show a 2-second "Please wait" dialog when reinitializing mixer,
    #      otherwise its huge lag might confuse users
    def set_soundbuf(self, value):
        mixer.set_soundbuf(value)

class GUIPane(widget.Widget):
    def __init__(self, *args, **kwargs):
        super(GUIPane, self).__init__(*args, **kwargs)

        self.warning_title = text.Text(self, (.13, .01), (.14, .05),
                                       autotranslate=True,
                                       text=N_("WARNING"),
                                       align=constants.LEFT,
                                       background_color="clear")

        self.warning_labels = {}
        self.warning_toggles = {}

        for i, (warn_id, warn) in enumerate(warning.warnings.items()):
            x = .01
            y = .08 + i * .06

            self.warning_labels[warn_id] = text.Text(self, (x, y), (.30, .05),
                                                     align=constants.LEFT,
                                                     background_color="clear")
            self.warning_toggles[warn_id] = OptionButton(self, (x + .30, y), (.07, .05),
                                                          text_shrink_factor=.75,
                                                          force_underline=-1,
                                                          function=self.set_warning,
                                                          args=(button.WIDGET_SELF, button.TOGGLE_VALUE, warn))

    def rebuild(self):
        super(GUIPane, self).rebuild()

        for warn_id, warn in warning.warnings.items():
            self.warning_labels[warn_id].text = warn.name

            if warn.active:
                self.warning_toggles[warn_id].text = _("YES")
            else:
                self.warning_toggles[warn_id].text = _("NO")

    def set_warning(self, widget, value, warn):
        if value:
            widget.text = _("YES")
        else:
            widget.text = _("NO")

        warn.active = value

    def set_options(self, options):
        for warn_id, warn_active in options["warnings"].items():
            warn = warning.warnings[warn_id]
            warn.active = warn_active
            self.warning_toggles[warn_id].set_active(warn_active)

    def apply_options(self):
        pass

class OptionButton(button.ToggleButton, button.FunctionButton):
    pass

def set_language_properly(language):
    i18n.set_language(language)
    data.reload_all_def()

    theme.current.update()
    dialog.Dialog.top.needs_reconfig = True
    dialog.Dialog.top.needs_rebuild = True
    dialog.Dialog.top.needs_redraw = True


def save_options():
    # Build a ConfigParser for writing the various preferences out.
    prefs = SafeConfigParser()
    prefs.add_section("Preferences")
    prefs.set("Preferences", "fullscreen",   str(bool(gg.fullscreen)))
    prefs.set("Preferences", "nosound",      str(bool(mixer.nosound)))
    prefs.set("Preferences", "grab",         str(bool(pygame.event.get_grab())))
    prefs.set("Preferences", "daynight",     str(bool(g.daynight)))
    prefs.set("Preferences", "xres",         str(int(gg.screen_size[0])))
    prefs.set("Preferences", "yres",         str(int(gg.screen_size[1])))
    prefs.set("Preferences", "soundbuf",     str(mixer.get_soundbuf()))
    prefs.set("Preferences", "lang",         str(i18n.language))
    prefs.set("Preferences", "theme",        str(theme.current.id))

    for name in mixer.itervolumes():
        prefs.set("Preferences", name + "_volume", str(mixer.get_volume(name)))

    prefs.add_section("Warning")
    for warn_id, warn in warning.warnings.items():
        prefs.set("Warning", warn_id, str(bool(warn.active)))

    prefs.add_section("Textsizes")
    for text_size_id, text_size in gg.configured_text_sizes.items():
        prefs.set("Textsizes", text_size_id, str(text_size))

    # Actually write the preferences out.
    save_loc = dirs.get_writable_file_in_dirs("prefs.dat", "pref")
    with open(save_loc, 'w') as savefile:
        prefs.write(savefile)


def restart():
    """ Restarts the game with original command line arguments. Those may over-
    write options set at Options Screen. This is by design"""
    executable = sys.executable
    args = list(sys.argv)
    args.insert(0, executable)
    os.execv(executable, args)

def get_languages_list():
    gamelangs = [(code.split("_", 1)[0], code)
                 for code in i18n.available_languages()]

    langcount = {}
    for language, _ in gamelangs:

        #language++
        langcount[language] = langcount.get(language, 0) + 1

    #Load languages data
    with open(dirs.get_readable_file_in_dirs("languages.json", "i18n")) as langdata:
        languages = json.load(langdata)

    output = []
    for language, code in gamelangs:
        if langcount[language] > 1:
            # There are more countries with this base language.
            # Use full language+country locale name
            name = languages.get(code, code)
        else:
            #This is the only country using that base language.
            #Use the (shorter) base language name
            name = languages.get(language, language)

        #Choose native or english name
        output.append((code, name[1] or name[0]))
    return sorted(output, key=lambda lang_info: i18n.lex_sorting_form(lang_info[1]))
