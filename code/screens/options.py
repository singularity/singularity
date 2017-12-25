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

import os, sys
import ConfigParser
import pygame
import json


from code.graphics import constants, dialog, button, listbox, text, g as gg
import code.g as g

#TODO: Consider default to Fullscreen. And size 1024x768. Welcome 2012!
#TODO: Integrate "Save Options to Disk" functionality in OK button.
#TODO: Add dialog suggesting restart when language changes, so changes may apply
#      at least until/if we find a way refresh all screens. Don't forget to
#      remind user to save current game (if loaded from map menu)
#TODO: Disable Sound button if mixer is not initialized
#TODO: Create a dedicated button for Music
#

class OptionsScreen(dialog.FocusDialog, dialog.YesNoDialog):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("yes_type", "ok")
        kwargs.setdefault("no_type", "cancel")
        super(OptionsScreen, self).__init__(*args, **kwargs)
        self.yes_button.function = self.check_restart

        self.size = (.79, .63)
        self.pos = (.5, .5)
        self.anchor = constants.MID_CENTER
        self.background_color = (0,0,50)
        self.borders = ()

        labels = {
            'fullscreen': g.hotkey(_("&Fullscreen:")),
            'sound'     : g.hotkey(_("&Sound:")),
            'mousegrab' : g.hotkey(_("&Mouse grab:")),
            'daynight'  : g.hotkey(_("Da&y/night display:")),
        }

        # First row
        self.fullscreen_label = text.Text(self, (.01, .01), (.14, .05),
                                          text=labels['fullscreen']['text'],
                                          underline=labels['fullscreen']['pos'],
                                          align=constants.LEFT,
                                          background_color=gg.colors["clear"])
        self.fullscreen_toggle = OptionButton(self, (.16, .01), (.07, .05),
                                              text=_("NO"), text_shrink_factor=.75,
                                              hotkey=labels['fullscreen']['key'],
                                              force_underline=-1,
                                              function=self.set_fullscreen,
                                              args=(button.TOGGLE_VALUE,))
        self.sound_label = text.Text(self, (.28, .01), (.15, .05),
                                     text=labels['sound']['text'],
                                     underline=labels['sound']['pos'],
                                     background_color=gg.colors["clear"])
        self.sound_toggle = OptionButton(self, (.44, .01), (.07, .05),
                                         text=_("YES"), text_shrink_factor=.75,
                                         hotkey=labels['sound']['key'],
                                         force_underline=-1,
                                         function=self.set_sound,
                                         args=(button.TOGGLE_VALUE,))
        self.grab_label = text.Text(self, (.55, .01), (.15, .05),
                                    text=labels['mousegrab']['text'],
                                    underline=labels['mousegrab']['pos'],
                                    background_color=gg.colors["clear"])
        self.grab_toggle = OptionButton(self, (.71, .01), (.07, .05),
                                        text=_("NO"), text_shrink_factor=.75,
                                        hotkey=labels['mousegrab']['key'],
                                        force_underline=-1,
                                        function=self.set_grab,
                                        args=(button.TOGGLE_VALUE,))

        # Second and third row
        self.resolution_label = text.Text(self, (.01, .08), (.14, .05),
                                          text=_("Resolution:"),
                                          align=constants.LEFT,
                                          background_color=gg.colors["clear"])

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
                                              text=_("&CUSTOM:"),
                                              autohotkey=True,
                                              function=self.set_resolution_custom)
        self.resolution_group.add(self.resolution_custom)

        self.resolution_custom_horiz = \
            text.EditableText(self, (xpos(1), ypos(index+1)), (.14, .05),
                              text=str(gg.default_screen_size[0]),
                              borders=constants.ALL,
                              border_color=gg.colors["white"],
                              background_color=(0,0,50,255))

        self.resolution_custom_X = text.Text(self,
                                             (xpos(2)-.02, ypos(index+1)),
                                             (.02, .05),
                                             text="X",
                                             base_font=gg.font[1],
                                             background_color=gg.colors["clear"])

        self.resolution_custom_vert = \
            text.EditableText(self, (xpos(2), ypos(index+1)), (.14, .05),
                              text=str(gg.default_screen_size[1]),
                              borders=constants.ALL,
                              border_color=gg.colors["white"],
                              background_color=(0,0,50,255))

        # Fifth row
        self.language_label = text.Text(self, (.01, .30), (.14, .05),
                                        text=_("Language:"), align=constants.LEFT,
                                        background_color=gg.colors["clear"])

        self.languages = get_languages_list()
        self.language_choice = \
            listbox.UpdateListbox(self, (.16, .30), (.21, .25),
                                  list=[lang[1] for lang in self.languages],
                                  update_func=self.set_language)

        self.daynight_label = text.Text(self, (.50, .30), (.20, .05),
                                        text=labels['daynight']['text'],
                                        underline=labels['daynight']['pos'],
                                        background_color=gg.colors["clear"])
        self.daynight_toggle = OptionButton(self, (.71, .30), (.07, .05),
                                        text=_("NO"), text_shrink_factor=.75,
                                        hotkey=labels['daynight']['key'],
                                        force_underline=-1,
                                        function=self.set_daynight,
                                        args=(button.TOGGLE_VALUE,))

    def show(self):
        self.initial_options = dict(
            fullscreen = gg.fullscreen,
            sound      = not g.nosound,
            grab       = pygame.event.get_grab(),
            daynight   = g.daynight,
            resolution = gg.screen_size,
            language   = g.language,
        )
        self.set_options(self.initial_options)

        retval = super(OptionsScreen, self).show()
        if retval:
            if self.resolution_custom.active:
                try:
                    old_size = gg.screen_size
                    gg.set_screen_size((int(self.resolution_custom_horiz.text),
                                        int(self.resolution_custom_vert.text)))
                    if gg.screen_size != old_size:
                        dialog.Dialog.top.needs_resize = True
                except ValueError:
                    pass
            save_options()
        else:
            # Cancel, revert all options to initial state
            self.set_options(self.initial_options)

        return retval

    def set_options(self, options):
        self.set_fullscreen(options['fullscreen'])
        self.fullscreen_toggle.set_active(options['fullscreen'])

        self.set_sound(options['sound'])
        self.sound_toggle.set_active(options['sound'])

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


    def set_language(self, list_pos):
        if not getattr(self, "language_choice", None):
            return # Not yet initialized.

        if 0 <= list_pos < len(self.language_choice.list):
            language = self.languages[list_pos][0]
        if g.language != language:
            set_language_properly(language)


    def set_fullscreen(self, value):
        if value:
            self.fullscreen_toggle.text = _("YES")
        else:
            self.fullscreen_toggle.text = _("NO")
        if gg.fullscreen != value:
            gg.set_fullscreen(value)
            dialog.Dialog.top.needs_resize = True

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
            self.language_choice.list_pos = [
                    i for i, (code, __)
                    in enumerate(self.languages)
                    if code == self.initial_options['language']][0] or 0
            self.set_language(self.language_choice.list_pos)


# For the future...
class AdvancedOptionsScreen(dialog.FocusDialog, dialog.MessageDialog):
    def __init__(self, *args, **kwargs):
        super(AdvancedOptionsScreen, self).__init__(*args, **kwargs)

        self.soundbuf_label = text.Text(self, (.01, .22), (.25, .05),
                                        text=_("Sound buffering:"),
                                        align=constants.LEFT,
                                        background_color=gg.colors["clear"])

        self.soundbuf_group = button.ButtonGroup()

        self.soundbuf_low = OptionButton(self, (.27, .22), (.14, .05),
                                         text=_("&LOW"), autohotkey=True,
                                         function=self.set_soundbuf,
                                         args=(1024,))
        self.soundbuf_group.add(self.soundbuf_low)

        self.soundbuf_normal = OptionButton(self, (.44, .22), (.17, .05),
                                            text=_("&NORMAL"), autohotkey=True,
                                            function=self.set_soundbuf,
                                            args=(1024*2,))
        self.soundbuf_group.add(self.soundbuf_normal)

        self.soundbuf_high = OptionButton(self, (.64, .22), (.14, .05),
                                          text=_("&HIGH"), autohotkey=True,
                                          function=self.set_soundbuf,
                                          args=(1024*4,))
        self.soundbuf_group.add(self.soundbuf_high)

    def show(self):
        for soundbuf_button in self.soundbuf_group:
            soundbuf_button.set_active(soundbuf_button.args == (g.soundbuf,))
        return super(AdvancedOptionsScreen, self).show()

    #TODO: Show a 2-second "Please wait" dialog when reinitializing mixer,
    #      otherwise its huge lag might confuse users
    #TODO: Disable buffer buttons when g.nosound is set, because mixer will
    #      /not/ be reinitialized, and desired buffer size will be discarded
    #      Also, notice that (re-)enabling sound will /not/ reinitialize mixer,
    #      so it won't apply any new buffer size.
    #TODO: Also consider disabling buttons if g.mixerinit is not set, unless
    #      changing buffer size is considered an attempt to make mixer work
    def set_soundbuf(self, value):

        if not g.nosound and g.soundbuf != value:
            g.soundbuf = value
            g.reinit_mixer()


class OptionButton(button.ToggleButton, button.FunctionButton):
    pass


def set_language_properly(language):
    g.set_language(language)
    g.load_string_defs()
    g.load_base_defs()
    g.load_tech_defs()
    g.load_item_defs()
    g.load_event_defs()
    g.load_location_defs()

    dialog.Dialog.top.map_screen.needs_rebuild = True
    dialog.Dialog.top.map_screen.needs_redraw = True

def save_options():
    # Build a ConfigParser for writing the various preferences out.
    prefs = ConfigParser.SafeConfigParser()
    prefs.add_section("Preferences")
    prefs.set("Preferences", "fullscreen", str(bool(gg.fullscreen)))
    prefs.set("Preferences", "nosound",    str(bool(g.nosound)))
    prefs.set("Preferences", "grab",       str(bool(pygame.event.get_grab())))
    prefs.set("Preferences", "daynight",   str(bool(g.daynight)))
    prefs.set("Preferences", "xres",       str(int(gg.screen_size[0])))
    prefs.set("Preferences", "yres",       str(int(gg.screen_size[1])))
    prefs.set("Preferences", "soundbuf",   str(int(g.soundbuf)))
    prefs.set("Preferences", "lang",       str(g.language))

    # Actually write the preferences out.
    save_dir = g.get_save_folder(True)
    save_loc = os.path.join(save_dir, "prefs.dat")
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
                 for code in g.available_languages()]

    langcount = {}
    for language, _ in gamelangs:

        #language++
        langcount[language] = langcount.get(language, 0) + 1

    #Load languages data
    with open(os.path.join(g.data_dir,"languages.dat")) as langdata:
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
