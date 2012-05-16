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
#TODO: Show a 2-or-so-seconds "Please wait" dialog when changing sound options,
#      because huge lag when applying them might confuse users
#TODO: Integrate "Save Options to Disk" functionality in OK button.
#TODO: Add dialog suggesting restart when language changes, so changes may apply
#      at least until/if we find a way refresh all screens. Don't forget to
#      remind user to save current game (if loaded from map menu)
#TODO: Add enable/disable Music
#

class OptionsScreen(dialog.FocusDialog, dialog.MessageDialog):
    def __init__(self, *args, **kwargs):
        super(OptionsScreen, self).__init__(*args, **kwargs)

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

        def xpos(i): return .16 + .16 *    (i%4)
        def ypos(i): return .08 + .07 * int(i/4)

        for i, (xres,yres) in enumerate(gg.resolutions):
            self.resolution_group.add(OptionButton(self,
                                                   (xpos(i), ypos(i)),
                                                   (.14, .05),
                                                   text="%sx%s" % (xres, yres),
                                                   function=self.set_resolution,
                                                   args=((xres,yres),)))

        # Forth row
        self.resolution_custom = OptionButton(self,
                                              (xpos(0),ypos(i+1)),
                                              (.14, .05),
                                              text=_("&CUSTOM:"),
                                              autohotkey=True,
                                              function=self.set_resolution_custom)
        self.resolution_group.add(self.resolution_custom)

        self.resolution_custom_horiz = \
            text.EditableText(self, (xpos(1), ypos(i+1)), (.14, .05),
                              text=str(gg.default_screen_size[0]),
                              borders=constants.ALL,
                              border_color=gg.colors["white"],
                              background_color=(0,0,50,255))

        self.resolution_custom_X = text.Text(self,
                                             (xpos(2)-.02, ypos(i+1)),
                                             (.02, .05),
                                             text="X",
                                             base_font=gg.font[1],
                                             background_color=gg.colors["clear"])

        self.resolution_custom_vert = \
            text.EditableText(self, (xpos(2), ypos(i+1)), (.14, .05),
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

        self.daynight_label = text.Text(self, (.55, .30), (.15, .05),
                                        text=labels['daynight']['text'],
                                        underline=labels['daynight']['pos'],
                                        background_color=gg.colors["clear"])
        self.daynight_toggle = OptionButton(self, (.71, .30), (.07, .05),
                                        text=_("NO"), text_shrink_factor=.75,
                                        hotkey=labels['daynight']['key'],
                                        force_underline=-1,
                                        function=self.set_daynight,
                                        args=(button.TOGGLE_VALUE,))

        self.save_button = button.FunctionButton(self, (.42, .45), (.34, .05),
                                                 text=_("SAVE OPTIONS TO &DISK"),
                                                 autohotkey=True,
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

        self.language_choice.list_pos = [i for i, (code, _)
                                         in enumerate(self.languages)
                                         if code == g.language][0] or 0

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
        if not getattr(self, "language_choice", None):
            return # Not yet initialized.

        prev_lang = g.language
        if 0 <= list_pos < len(self.language_choice.list):
            g.language = self.languages[list_pos][0]
        if g.language != prev_lang:
            set_language_properly()

    def set_fullscreen(self, value, resize=True):
        if value:
            self.fullscreen_toggle.text = _("YES")
        else:
            self.fullscreen_toggle.text = _("NO")
        gg.fullscreen = value
        if resize:
            dialog.Dialog.top.needs_resize = True

    def set_sound(self, value, reset=True):
        if value:
            self.sound_toggle.text = _("YES")
        else:
            self.sound_toggle.text = _("NO")
        g.nosound = not value
        if reset and not g.nosound:
            g.reinit_mixer()
            g.play_sound("click")

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
        return super(OptionsScreen, self).show()


class OptionButton(button.ToggleButton, button.FunctionButton):
    pass


def set_language_properly():
    g.set_language()
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
    save_loc = os.path.join(save_dir, "prefs.dat")
    savefile = open(save_loc, 'w')
    prefs.write(savefile)
    savefile.close()

def restart():
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
