#file: options.py
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

#This file is used to display the options screen.

from os import path
import ConfigParser
import pygame

from code.graphics import constants, dialog, button, listbox, text, g as gg
import code.g as g

class OptionsScreen(dialog.FocusDialog, dialog.MessageDialog):
    def __init__(self, *args, **kwargs):
        super(OptionsScreen, self).__init__(*args, **kwargs)

        self.size = (.79, .63)
        self.pos = (.5, .5)
        self.anchor = constants.MID_CENTER
        self.background_color = (0,0,50)
        self.borders = ()

        self.fullscreen_label = text.Text(self, (.01, .01), (.15, .05),
                                          text="Fullscreen:", underline=0,
                                          align=constants.LEFT,
                                          background_color=gg.colors["clear"])
        self.fullscreen_toggle = OptionButton(self, (.17, .01), (.07, .05),
                                              text="NO", text_shrink_factor=.75,
                                              hotkey="f", force_underline=-1,
                                              function=self.set_fullscreen,
                                              args=(button.TOGGLE_VALUE,))
        self.sound_label = text.Text(self, (.28, .01), (.15, .05),
                                     text="Sound:", underline=0,
                                     background_color=gg.colors["clear"])
        self.sound_toggle = OptionButton(self, (.44, .01), (.07, .05),
                                         text="YES", text_shrink_factor=.75,
                                         hotkey="s", force_underline=-1,
                                         function=self.set_sound,
                                         args=(button.TOGGLE_VALUE,))
        self.grab_label = text.Text(self, (.55, .01), (.15, .05),
                                    text="Mouse grab:", underline=0,
                                    background_color=gg.colors["clear"])
        self.grab_toggle = OptionButton(self, (.71, .01), (.07, .05),
                                        text="NO", text_shrink_factor=.75,
                                        hotkey="m", force_underline=-1,
                                        function=self.set_grab,
                                        args=(button.TOGGLE_VALUE,))
        self.resolution_label = text.Text(self, (.01, .08), (.15, .05),
                                          text="Resolution:",
                                          align=constants.LEFT,
                                          background_color=gg.colors["clear"])

        self.resolution_group = button.ButtonGroup()
        self.resolution_640x480 = OptionButton(self, (.17, .08), (.12, .05),
                                               text="640X480",
                                               text_shrink_factor=.5,
                                               function=self.set_resolution,
                                               args=((640,480),))
        self.resolution_group.add(self.resolution_640x480)
        self.resolution_800x600 = OptionButton(self, (.333, .08), (.12, .05),
                                               text="800X600",
                                               text_shrink_factor=.5,
                                               function=self.set_resolution,
                                               args=((800,600),))
        self.resolution_group.add(self.resolution_800x600)
        self.resolution_1024x768 = OptionButton(self, (.496, .08), (.12, .05),
                                                text="1024X768",
                                                text_shrink_factor=.5,
                                                function=self.set_resolution,
                                                args=((1024,768),))
        self.resolution_group.add(self.resolution_1024x768)
        self.resolution_1280x1024 = OptionButton(self, (.66, .08), (.12, .05),
                                                 text="1280X1024",
                                                 text_shrink_factor=.5,
                                                 function=self.set_resolution,
                                                 args=((1280,1024),))
        self.resolution_group.add(self.resolution_1280x1024)

        self.resolution_custom = OptionButton(self, (.17, .15), (.12, .05),
                                              text="CUSTOM:",
                                              text_shrink_factor=.5)
        self.resolution_group.add(self.resolution_custom)

        self.resolution_custom_horiz = \
            text.EditableText(self, (.333, .15), (.12, .05), text="1400",
                              borders=constants.ALL,
                              border_color=gg.colors["white"],
                              background_color=(0,0,50,255))

        self.resolution_custom_X = text.Text(self, (.46, .15), (.03, .05),
                                             text="X", base_font=gg.font[1],
                                             background_color=gg.colors["clear"])

        self.resolution_custom_vert = \
            text.EditableText(self, (.496, .15), (.12, .05), text="1050",
                              borders=constants.ALL,
                              border_color=gg.colors["white"],
                              background_color=(0,0,50,255))

        self.resolution_apply = \
            button.FunctionButton(self, (.66, .15), (.12, .05),
                                  text="APPLY", text_shrink_factor=.75, hotkey="a",
                                  function=self.set_resolution_custom)

        self.soundbuf_label = text.Text(self, (.01, .22), (.25, .05),
                                        text="Sound buffering:",
                                        align=constants.LEFT,
                                        background_color=gg.colors["clear"])

        self.soundbuf_group = button.ButtonGroup()

        self.soundbuf_low = OptionButton(self, (.27, .22), (.14, .05),
                                         text="LOW", hotkey="l",
                                         function=self.set_soundbuf,
                                         args=(1024,))
        self.soundbuf_group.add(self.soundbuf_low)

        self.soundbuf_normal = OptionButton(self, (.44, .22), (.17, .05),
                                            text="NORMAL", hotkey="n",
                                            function=self.set_soundbuf,
                                            args=(1024*2,))
        self.soundbuf_group.add(self.soundbuf_normal)

        self.soundbuf_high = OptionButton(self, (.64, .22), (.14, .05),
                                          text="HIGH", hotkey="h",
                                          function=self.set_soundbuf,
                                          args=(1024*4,))
        self.soundbuf_group.add(self.soundbuf_high)

        self.language_label = text.Text(self, (.01, .30), (.15, .05),
                                        text="Language:", align=constants.LEFT,
                                        background_color=gg.colors["clear"])

        self.language_choice = \
            listbox.UpdateListbox(self, (.17, .30), (.21, .25),
                                  list=g.available_languages(),
                                  update_func=self.set_language)

        self.daynight_label = text.Text(self, (.55, .30), (.15, .05),
                                        text="Day/night display:", underline=2,
                                        background_color=gg.colors["clear"])
        self.daynight_toggle = OptionButton(self, (.71, .30), (.07, .05),
                                        text="NO", text_shrink_factor=.75,
                                        hotkey="y", force_underline=-1,
                                        function=self.set_daynight,
                                        args=(button.TOGGLE_VALUE,))

        self.save_button = button.FunctionButton(self, (.42, .45), (.34, .05),
                                                 text="SAVE OPTIONS TO DISK",
                                                 hotkey="d",
                                                 function=save_options)

    def show(self):
        self.set_fullscreen(gg.fullscreen, resize=False)
        self.fullscreen_toggle.set_active(gg.fullscreen)
        self.set_sound(not g.nosound, reset=False)
        self.sound_toggle.set_active(not g.nosound)
        self.set_grab(pygame.event.get_grab())
        self.grab_toggle.set_active(pygame.event.get_grab())
        self.set_daynight(g.daynight)
        self.daynight_toggle.set_active(g.daynight)
        custom = True
        for res_button in self.resolution_group:
            res_button.set_active(res_button.args == (gg.screen_size,))
            if res_button.active:
                custom = False
        if custom:
            self.resolution_custom.set_active(True)
            self.resolution_custom_horiz.text = str(gg.screen_size[0])
            self.resolution_custom_vert.text = str(gg.screen_size[1])
        for soundbuf_button in self.soundbuf_group:
            soundbuf_button.set_active(soundbuf_button.args == (g.soundbuf,))

        lang_array = self.language_choice.list
        lang_pos = 0
        for i in range(len(lang_array)):
            if lang_array[i] == g.language:
                lang_pos = i
        self.language_choice.list_pos = lang_pos

        retval = super(OptionsScreen, self).show()

        if self.resolution_custom.active:
            try:
                old_size = gg.screen_size
                gg.screen_size = (int(self.resolution_custom_horiz.text),
                                  int(self.resolution_custom_vert.text))
                if gg.screen_size != old_size:
                    dialog.Dialog.top.needs_resize = True
            except ValueError:
                pass

        return retval

    def set_language(self, list_pos):
        if getattr(self, "language_choice", None) is None:
            return # Not yet initialized.

        prev_lang = g.language
        if 0 <= list_pos < len(self.language_choice.list):
            g.language = self.language_choice.list[list_pos]
        if g.language != prev_lang:
            set_language_properly()

    def set_fullscreen(self, value, resize=True):
        if value:
            self.fullscreen_toggle.text = "YES"
        else:
            self.fullscreen_toggle.text = "NO"
        gg.fullscreen = value
        if resize:
            dialog.Dialog.top.needs_resize = True

    def set_sound(self, value, reset=True):
        if value:
            self.sound_toggle.text = "YES"
        else:
            self.sound_toggle.text = "NO"
        g.nosound = not value
        if reset and not g.nosound:
            g.reinit_mixer()
            g.play_sound("click")

    def set_grab(self, value):
        if value:
            self.grab_toggle.text = "YES"
        else:
            self.grab_toggle.text = "NO"
        pygame.event.set_grab(value)

    def set_daynight(self, value):
        if value:
            self.daynight_toggle.text = "YES"
        else:
            self.daynight_toggle.text = "NO"
        g.daynight = value

    def set_resolution(self, value):
        gg.screen_size = value
        dialog.Dialog.top.needs_resize = True

    def set_resolution_custom(self):
        self.resolution_custom.chosen_one()
        try:
            screen_size = (int(self.resolution_custom_horiz.text),
                           int(self.resolution_custom_vert.text))
            self.set_resolution(screen_size)
        except ValueError:
            pass

    def set_soundbuf(self, value):
        g.soundbuf = value
        if not g.nosound:
            g.reinit_mixer()
            g.play_sound("click")


class OptionButton(button.ToggleButton, button.FunctionButton):
    pass


def set_language_properly():
    g.set_locale()
    g.load_bases()
    g.load_techs()
    g.load_items()
    g.load_base_defs(g.language)
    g.load_tech_defs(g.language)
    g.load_item_defs(g.language)
    g.load_string_defs(g.language)
    try:
        g.load_location_defs(g.language)
    except NameError:
        # We haven't initialized the location yet.  This will be handled when
        # we do that.
        pass

    dialog.Dialog.top.map_screen.needs_rebuild = True
    dialog.Dialog.top.map_screen.needs_redraw = True

def save_options():
    # Build a ConfigParser for writing the various preferences out.
    prefs = ConfigParser.SafeConfigParser()
    prefs.add_section("Preferences")
    prefs.set("Preferences", "fullscreen", str(gg.fullscreen))
    prefs.set("Preferences", "nosound", str(g.nosound))
    prefs.set("Preferences", "grab", str(pygame.event.get_grab()))
    prefs.set("Preferences", "daynight", str(g.daynight))
    prefs.set("Preferences", "xres", str(gg.screen_size[0]))
    prefs.set("Preferences", "yres", str(gg.screen_size[1]))
    prefs.set("Preferences", "lang", g.language)
    prefs.set("Preferences", "soundbuf", str(g.soundbuf))

    # Actually write the preferences out.
    save_dir = g.get_save_folder(True)
    save_loc = path.join(save_dir, "prefs.dat")
    savefile = open(save_loc, 'w')
    prefs.write(savefile)
    savefile.close()
