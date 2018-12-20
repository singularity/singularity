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

import os, sys
import ConfigParser
import pygame
import json

from code.graphics import constants, widget, dialog, button, listbox, slider, text, theme, g as gg
import code.g as g, code.dirs as dirs, code.i18n as i18n

#TODO: Consider default to Fullscreen. And size 1024x768. Welcome 2012!
#TODO: Integrate "Save Options to Disk" functionality in OK button.
#TODO: Add dialog suggesting restart when language changes, so changes may apply
#      at least until/if we find a way refresh all screens. Don't forget to
#      remind user to save current game (if loaded from map menu)
#TODO: Disable Sound pane if mixer is not initialized
#TODO: Create a dedicated button for Music
#
class OptionsScreen(dialog.FocusDialog, dialog.YesNoDialog):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("yes_type", "ok")
        kwargs.setdefault("no_type", "cancel")
        super(OptionsScreen, self).__init__(*args, **kwargs)
        self.yes_button.function = self.check_restart

        self.size = (.80, .85)
        self.pos = (.5, .5)
        self.anchor = constants.MID_CENTER
        self.background_color = (0,0,50)
        self.borders = ()

        # Tabs panel
        self.general_pane   = GeneralPane(None, (0, .1), (.80, .75))
        self.audio_pane     = AudioPane(None, (0, .1), (.80, .75))

        self.tabs_panes = (self.general_pane, self.audio_pane)

        # Tabs buttons
        self.tabs_buttons = button.ButtonGroup()

        self.general_tab = OptionButton(self, (-.5, .01), (.15, .05),
                                         anchor = constants.TOP_RIGHT,
                                         autohotkey=True,
                                         function=self.set_tabs_pane, args=(self.general_pane,))
        self.tabs_buttons.add(self.general_tab)

        self.audio_tab = OptionButton(self, (-.5, .01), (.15, .05),
                                       anchor = constants.TOP_LEFT,
                                       autohotkey=True,
                                       function=self.set_tabs_pane, args=(self.audio_pane,))
        self.tabs_buttons.add(self.audio_tab)

        self.general_tab.chosen_one()
        self.set_tabs_pane(self.general_pane)

        # YesNoDialog buttons
        self.yes_button.size = (.15, .05)
        self.no_button.size = (.15, .05)

    def rebuild(self):
        self.general_tab.text               = _("&General")
        self.audio_tab.text                 = _("&Audio")

        self.general_pane.needs_rebuild     = True
        self.audio_pane.needs_rebuild       = True

        super(OptionsScreen, self).rebuild()

    def show(self):
        self.initial_options = dict(
            fullscreen      = gg.fullscreen,
            grab            = pygame.event.get_grab(),
            daynight        = g.daynight,
            resolution      = gg.screen_size,
            language        = i18n.language,
            sound           = not g.nosound,
            gui_volume      = int(g.soundvolumes["gui"] * 100.0),
            music_volume    = int(g.soundvolumes["music"] * 100.0),
            soundbuf        = g.soundbuf
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
        self.general_pane.set_options(options)
        self.audio_pane.set_options(options)

    def apply_options(self):
        self.general_pane.apply_options()
        self.audio_pane.apply_options()

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

        # First row
        self.fullscreen_label = button.HotkeyText(self, (.01, .01), (.14, .05),
                                                  autohotkey=True,
                                                  align=constants.LEFT,
                                                  background_color="clear")
        self.fullscreen_toggle = OptionButton(self, (.16, .01), (.07, .05),
                                              text_shrink_factor=.75,
                                              force_underline=-1,
                                              function=self.set_fullscreen,
                                              args=(button.TOGGLE_VALUE,))
        self.fullscreen_label.hotkey_target = self.fullscreen_toggle

        self.daynight_label = button.HotkeyText(self, (.25, .01), (.20, .05),
                                                autohotkey=True,
                                                background_color="clear")
        self.daynight_toggle = OptionButton(self, (.46, .01), (.07, .05),
                                        text_shrink_factor=.75,
                                        force_underline=-1,
                                        function=self.set_daynight,
                                        args=(button.TOGGLE_VALUE,))
        self.daynight_label.hotkey_target = self.daynight_toggle

        self.grab_label = button.HotkeyText(self, (.55, .01), (.15, .05),
                                            autohotkey=True,
                                            background_color="clear")
        self.grab_toggle = OptionButton(self, (.71, .01), (.07, .05),
                                        text_shrink_factor=.75,
                                        force_underline=-1,
                                        function=self.set_grab,
                                        args=(button.TOGGLE_VALUE,))
        self.grab_label.hotkey_target = self.grab_toggle

        # Second and third row
        self.resolution_label = text.Text(self, (.01, .08), (.14, .05),
                                          align=constants.LEFT,
                                          background_color="clear")

        self.resolution_group = button.ButtonGroup()

        rows = 2
        cols = 4
        def xpos(i): return .16 + .16 *    (i%cols)
        def ypos(i): return .08 + .07 * int(i/cols)

        for index, (xres,yres) in enumerate(sorted(gg.resolutions[0:rows*cols])):
            self.resolution_group.add(OptionButton(self,
                                                   (xpos(index), ypos(index)),
                                                   (.14, .05),
                                                   text="%sx%s" % (xres, yres),
                                                   function=self.set_resolution,
                                                   args=((xres,yres),)))
        # Adjust index to full row
        index += cols - (index % cols) - 1

        # Forth row
        self.resolution_custom = OptionButton(self,
                                              (xpos(0),ypos(index+1)),
                                              (.14, .05),
                                              autohotkey=True,
                                              function=self.set_resolution_custom)
        self.resolution_group.add(self.resolution_custom)

        self.resolution_custom_horiz = \
            text.EditableText(self, (xpos(1), ypos(index+1)), (.14, .05),
                              text=str(gg.default_screen_size[0]),
                              borders=constants.ALL,
                              border_color="widget_border",
                              background_color=(0,0,50,255))

        self.resolution_custom_X = text.Text(self,
                                             (xpos(2)-.02, ypos(index+1)),
                                             (.02, .05),
                                             text="X",
                                             base_font="special",
                                             background_color="clear")

        self.resolution_custom_vert = \
            text.EditableText(self, (xpos(2), ypos(index+1)), (.14, .05),
                              text=str(gg.default_screen_size[1]),
                              borders=constants.ALL,
                              border_color="widget_border",
                              background_color=(0,0,50,255))

        # Fifth row
        self.language_label = text.Text(self, (.01, .30), (.14, .05),
                                        align=constants.LEFT,
                                        background_color="clear")

        self.languages = get_languages_list()
        self.language_choice = \
            listbox.UpdateListbox(self, (.16, .30), (.20, .25),
                                  list=[lang[1] for lang in self.languages],
                                  update_func=self.set_language)

        self.theme_label = text.Text(self, (.37, .30), (.09, .05),
                                     text=_("Theme:"), align=constants.LEFT,
                                     background_color="clear")

        self.theme_choice = \
            listbox.UpdateListbox(self, (.47, .30), (.12, .25),
                                  update_func=theme.set_theme,
                                  list_pos=theme.get_theme_pos())

    def rebuild(self):
        self.fullscreen_label.text          = _("&Fullscreen:")
        self.grab_label.text                = _("&Mouse grab:")
        self.daynight_label.text            = _("Da&y/night display:")
        self.language_label.text            = _("Language:")
        self.resolution_label.text          = _("Resolution:")
        self.resolution_custom.text         = _("&CUSTOM:")

        self.theme_choice.list = theme.get_theme_list()

        if gg.fullscreen:
            self.fullscreen_toggle.text = _("YES")
        else:
            self.fullscreen_toggle.text = _("NO")

        if pygame.event.get_grab():
            self.grab_toggle.text = _("YES")
        else:
            self.grab_toggle.text = _("NO")

        super(GeneralPane, self).rebuild()

    def set_options(self, options):
        self.set_fullscreen(options['fullscreen'])
        self.fullscreen_toggle.set_active(options['fullscreen'])

        self.set_grab(options['grab'])
        self.grab_toggle.set_active(options['grab'])

        self.set_daynight(options['daynight'])
        self.daynight_toggle.set_active(options['daynight'])

        custom = True
        for res_button in self.resolution_group:
            res_button.set_active(res_button.args == (options['resolution'],))
            if res_button.active:
                custom = False
        if custom:
            self.resolution_custom.set_active(True)
            self.resolution_custom_horiz.text = str(options['resolution'][0])
            self.resolution_custom_vert.text = str(options['resolution'][1])
        self.set_resolution(options['resolution'])

        self.language_choice.list_pos = [i for i, (code, __)
                                         in enumerate(self.languages)
                                         if code == options['language']][0] or 0
        self.set_language(self.language_choice.list_pos)

        self.theme_choice.list_pos = theme.get_theme_pos()

    def apply_options(self):
        if self.resolution_custom.active:
            try:
                old_size = gg.screen_size
                gg.set_screen_size((int(self.resolution_custom_horiz.text),
                                    int(self.resolution_custom_vert.text)))
                if gg.screen_size != old_size:
                    dialog.Dialog.top.needs_resize = True
            except ValueError:
                pass

    def set_language(self, list_pos):
        if not getattr(self, "language_choice", None):
            return # Not yet initialized.

        if 0 <= list_pos < len(self.language_choice.list):
            language = self.languages[list_pos][0]
        if i18n.language != language:
            set_language_properly(language)


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
            dialog.Dialog.top.needs_resize = True

    def set_resolution_custom(self):
        self.resolution_custom.chosen_one()
        try:
            screen_size = (int(self.resolution_custom_horiz.text),
                           int(self.resolution_custom_vert.text))
            self.set_resolution(screen_size)
        except ValueError:
            pass

class AudioPane(widget.Widget):
    def __init__(self, *args, **kwargs):
        super(AudioPane, self).__init__(*args, **kwargs)

        self.sound_label = button.HotkeyText(self, (-.49, .01), (.10, .05),
                                             anchor = constants.TOP_RIGHT,
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
                                     anchor = constants.TOP_LEFT,
                                     align=constants.LEFT,
                                     background_color="clear")
        self.gui_slider = slider.UpdateSlider(self, (.24, .08), (.53, .05),
                                              anchor = constants.TOP_LEFT,
                                              horizontal=True, priority=150,
                                              slider_max=100, slider_size=5)
        self.gui_slider.update_func = self.on_gui_volume_change

        self.music_label = text.Text(self, (.01, .15), (.22, .05),
                                     anchor = constants.TOP_LEFT,
                                     align=constants.LEFT,
                                     background_color="clear")
        self.music_slider = slider.UpdateSlider(self, (.24, .15), (.53, .05),
                                                anchor = constants.TOP_LEFT,
                                                horizontal=True, priority=150,
                                                slider_max=100, slider_size=5)
        self.music_slider.update_func = self.on_music_volume_change

        self.soundbuf_label = text.Text(self, (.01, .22), (.25, .05),
                                        text=_("Sound buffering:"),
                                        align=constants.LEFT,
                                        background_color="clear")
        self.soundbuf_group = button.ButtonGroup()

        self.soundbuf_low = OptionButton(self, (.24, .22), (.14, .05),
                                         text=_("&LOW"), autohotkey=True,
                                         function=self.set_soundbuf,
                                         args=(1024,))
        self.soundbuf_group.add(self.soundbuf_low)

        self.soundbuf_normal = OptionButton(self, (.42, .22), (.17, .05),
                                            text=_("&NORMAL"), autohotkey=True,
                                            function=self.set_soundbuf,
                                            args=(1024*2,))
        self.soundbuf_group.add(self.soundbuf_normal)

        self.soundbuf_high = OptionButton(self, (.63, .22), (.14, .05),
                                          text=_("&HIGH"), autohotkey=True,
                                          function=self.set_soundbuf,
                                          args=(1024*4,))
        self.soundbuf_group.add(self.soundbuf_high)

    def rebuild(self):
        self.sound_label.text = _("&Sound:")
        self.gui_label.text = _("GUI Volume:")
        self.music_label.text = _("Music Volume:")

        if not g.nosound:
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

        if g.nosound == (not value):
            # No transition requested, bail out
            return

        g.nosound = not value
        if g.nosound:
            if g.mixerinit:
                pygame.mixer.music.stop()
        else:
            g.play_sound("click")
            g.play_music(g.music_class)  # force music switch at same dir

    def on_gui_volume_change(self, value):
        g.soundvolumes["gui"] = value / float(100)

    def on_music_volume_change(self, value):
        g.soundvolumes["music"] = value / float(100)
        if g.mixerinit:
            pygame.mixer.music.set_volume(g.soundvolumes["music"])

    #TODO: Show a 2-second "Please wait" dialog when reinitializing mixer,
    #      otherwise its huge lag might confuse users
    def set_soundbuf(self, value):
        old_soundbuf = g.soundbuf
        g.soundbuf = value

        if g.mixerinit and g.soundbuf != old_soundbuf:
            g.reinit_mixer()

class OptionButton(button.ToggleButton, button.FunctionButton):
    pass

def set_language_properly(language):
    i18n.set_language(language)
    g.load_strings()
    g.load_knowledge_defs()
    g.load_difficulty_defs()
    g.load_base_defs()
    g.load_tech_defs()
    g.load_item_defs()
    g.load_event_defs()
    g.load_task_defs()
    g.load_location_defs()

    theme.current.update()
    dialog.Dialog.top.needs_reconfig = True
    dialog.Dialog.top.needs_rebuild = True
    dialog.Dialog.top.needs_redraw = True

def save_options():
    # Build a ConfigParser for writing the various preferences out.
    prefs = ConfigParser.SafeConfigParser()
    prefs.add_section("Preferences")
    prefs.set("Preferences", "fullscreen",   str(bool(gg.fullscreen)))
    prefs.set("Preferences", "nosound",      str(bool(g.nosound)))
    prefs.set("Preferences", "grab",         str(bool(pygame.event.get_grab())))
    prefs.set("Preferences", "daynight",     str(bool(g.daynight)))
    prefs.set("Preferences", "xres",         str(int(gg.screen_size[0])))
    prefs.set("Preferences", "yres",         str(int(gg.screen_size[1])))
    prefs.set("Preferences", "soundbuf",     str(int(g.soundbuf)))
    prefs.set("Preferences", "lang",         str(i18n.language))
    prefs.set("Preferences", "theme",        str(theme.current.id))

    for name, value in g.soundvolumes.iteritems():
        prefs.set("Preferences", name + "_volume", str(value))

    # Actually write the preferences out.
    save_loc = dirs.get_writable_file_in_dirs("prefs.dat", "pref")
    savefile = open(save_loc, 'w')
    prefs.write(savefile)
    savefile.close()

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

    return sorted(output)
