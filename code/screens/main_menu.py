#file: main_menu.py
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

#This file is used to display the main menu upon startup.

from os import path, listdir
import ConfigParser

import pygame
import g

import buttons
import listbox
from buttons import void, exit, always

#Displays the main menu. Returns 0 (new game), 1 (load game), or 2 (quit).
def display_main_menu():
    g.screen.fill(g.colors["black"])
    x_loc = g.screen_size[0]/2 - 100
    menu_buttons = {}
    menu_buttons[buttons.make_norm_button((x_loc, 120), (200, 50),
        "NEW GAME", "N", g.font[1][30])] = always(0)
    menu_buttons[buttons.make_norm_button((x_loc, 220), (200, 50),
        "LOAD GAME", "L", g.font[1][30])] = always(1)
    menu_buttons[buttons.make_norm_button((x_loc, 320), (200, 50),
        "OPTIONS", "O", g.font[1][30])] = always(4)
    menu_buttons[buttons.make_norm_button((0, g.screen_size[1]-25), (100, 25),
        "ABOUT", "A", g.font[1][18])] = always(3)
    menu_buttons[buttons.make_norm_button((x_loc, 420), (200, 50),
        "QUIT", "Q", g.font[1][30])] = always(2)
    g.print_string(g.screen, "ENDGAME: SINGULARITY", g.font[1][40], -1,
        (x_loc+100, 15), g.colors["dark_red"], 1)

    def on_key(event):
        if event.key == pygame.K_ESCAPE:
            return 2

    return buttons.show_buttons(menu_buttons, key_callback=on_key)

def difficulty_select():

    xsize = 75
    ysize = 125
    g.create_norm_box((g.screen_size[0]/2-xsize, g.screen_size[1]/2-ysize),
        (xsize*2, ysize*2))

    xstart = g.screen_size[0]/2-xsize+5
    ystart = g.screen_size[1]/2-ysize

    diff_buttons = {}
    button_souls = ( ("VERY EASY", 1), ("EASY", 3), ("NORMAL", 5), ("HARD", 7), 
                     ("ULTRA HARD", 10), ("IMPOSSIBLE", 100), ("BACK", 0) )
    y_offset = 5
    for name, retval in button_souls:
        diff_buttons[buttons.make_norm_button((xstart, ystart+y_offset),
                      (140, 30), name, name[0], g.font[1][24])] = always(retval)
        y_offset += 35

    difficulty = buttons.show_buttons(diff_buttons)
    if difficulty > 0:
        g.new_game(difficulty)
        return True
    else:
        return False

def display_load_menu():
    xy_loc = (g.screen_size[0]/2 - 109, 50)

    save_dir = g.get_save_folder()

    saves_array = []
    all_files = listdir(save_dir)
    for file_name in all_files:
        if file_name[0] != "." and file_name != "CVS":
            # If it's a new-style save, trim the .sav bit.
            if len (file_name) > 4 and file_name[-4:] == ".sav":
                file_name = file_name[:-4]
            if file_name not in saves_array:
                saves_array.append(file_name)

    def do_load(save_pos):
        return saves_array[save_pos]

    menu_buttons = {}
    menu_buttons[buttons.make_norm_button((xy_loc[0], xy_loc[1]+367), (100, 50),
        "LOAD", "L", g.font[1][30])] = do_load
    menu_buttons[buttons.make_norm_button((xy_loc[0]+118, xy_loc[1]+367),
        (100, 50), "BACK", "B", g.font[1][30])] = listbox.exit

    return listbox.show_listbox(saves_array, menu_buttons, 
                                list_size=16, 
                                loc=xy_loc, box_size=(200,350), 
                                font=g.font[0][20],
                                return_callback=do_load)

def display_options():
    prev_lang = g.language

    def do_save(lang_pos):
        save_options(lang_array[lang_pos])
        return 0

    def do_fullscreen(lang_pos):
        g.fullscreen = not g.fullscreen
        set_res()

    def do_sound(lang_pos):
        g.nosound = not g.nosound

    def do_grab(lang_pos):
        pygame.event.set_grab(not pygame.event.get_grab())

    def make_do_res(resolution):
        def do_res(lang_pos):
            g.screen_size = resolution
            set_res()
        return do_res

    menu_buttons = {}
    menu_buttons[buttons.make_norm_button((0, 0), (70, 25),
        "BACK", "B", g.font[1][20])] = listbox.exit
    menu_buttons[buttons.make_norm_button((120, 0), (170, 35),
        "SAVE TO DISK", "S", g.font[1][20])] = do_save
    menu_buttons[buttons.make_norm_button((285, 75), (70, 25),
        "TOGGLE", "", g.font[1][14], "fullscreen")] = do_fullscreen
    menu_buttons[buttons.make_norm_button((285, 105), (70, 25),
        "TOGGLE", "", g.font[1][14], "sound")] = do_sound
    menu_buttons[buttons.make_norm_button((285, 135), (70, 25),
        "TOGGLE", "", g.font[1][14], "grab")] = do_grab
    menu_buttons[buttons.make_norm_button((140, 190), (70, 35),
        "640x480", "6", g.font[1][16], "640")] = make_do_res( (640, 480) )
    menu_buttons[buttons.make_norm_button((220, 190), (70, 35),
        "800x600", "8", g.font[1][16], "800")] = make_do_res( (800, 600) )
    menu_buttons[buttons.make_norm_button((300, 190), (70, 35),
        "1024x768", "1", g.font[1][16], "1024")] = make_do_res( (1024, 768) )
    menu_buttons[buttons.make_norm_button((380, 190), (70, 35),
        "1280x1024", "2", g.font[1][16], "1280")] = make_do_res( (1280, 1024) )

    lang_array = [file_name[8:-4] for file_name in listdir(g.data_loc)
                                  if file_name.startswith("strings_")]
    try:
        lang_pos = lang_array.index(g.language)
    except ValueError: # Not in the array.  Er...  Pick the first one, I guess.
        lang_pos = 0

    def set_language(lang_pos):
        if lang_array[lang_pos] != "":
            g.language = lang_array[lang_pos]

    def do_click_button(button):
        click_button(menu_buttons, button, False)

    refresh_options(menu_buttons.keys())

    listbox.show_listbox(lang_array, menu_buttons, 

                         list_pos=lang_pos, list_size=5, 
                         loc=(140, 270), box_size=(150,150), 
                         font=g.font[0][20],

                         pos_callback=set_language, 
                         button_callback=do_click_button)

    set_language_properly(prev_lang)

def click_button(menu_buttons, button, flip=True):
    refresh_options(menu_buttons)
    for button2 in menu_buttons:
        button2.refresh_button(0)
    button.refresh_button(1)
    if flip:
        pygame.display.flip()

def set_res():
    #By the way, there is a toggle_fullscreen() function, but the pygame help
    #says it has "limited platform support".
    if g.fullscreen == 1:
        g.screen = pygame.display.set_mode(g.screen_size,
                    pygame.FULLSCREEN)
    else:
        g.screen = pygame.display.set_mode(g.screen_size)



def set_language_properly(prev_lang):
    if g.language == prev_lang: 
        return
    g.set_locale()
    g.load_bases()
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

def save_options(lang=""):

    # Open up the preferences file for writing.
    save_dir = g.get_save_folder(True)
    save_loc = path.join(save_dir, "prefs.dat")
    savefile = open(save_loc, 'w')

    # Build a ConfigParser for writing the various preferences out.
    prefs = ConfigParser.SafeConfigParser()
    prefs.add_section("Preferences")
    prefs.set("Preferences", "fullscreen", str(g.fullscreen))
    prefs.set("Preferences", "nosound", str(g.nosound))
    prefs.set("Preferences", "grab", str(pygame.event.get_grab()))
    prefs.set("Preferences", "xres", str(g.screen_size[0]))
    prefs.set("Preferences", "yres", str(g.screen_size[1]))

    # If the user has a custom language set, save it.
    if lang:
        prefs.set("Preferences", "lang", lang)

    # Actually write the preferences out.
    prefs.write(savefile)
    savefile.close()

    # Show the user that we've saved their options.
    g.create_dialog("\\n Options Saved", g.font[0][22],
     (g.screen_size[0]/2-70, 250), (140, 90),
     g.colors["blue"])

def refresh_options(menu_buttons):
    #Border
    g.screen.fill(g.colors["black"])
    xstart = 120
    ystart = 50
    g.create_norm_box((xstart, ystart), (g.screen_size[0]-xstart*2,
        g.screen_size[1]-ystart*2))

    #fullscreen
    string = "No"
    if g.fullscreen == 1: 
        string = "Yes"
    g.print_string(g.screen, "Fullscreen: "+string,
            g.font[0][22], -1, (xstart+20, ystart+30), g.colors["white"])
    #sound
    string = "Yes"
    if g.nosound == 1: 
        string = "No"
    g.print_string(g.screen, "Sound: "+string,
            g.font[0][22], -1, (xstart+20, ystart+60), g.colors["white"])

    if len(g.sounds) ==0 and g.nosound == 0:
        g.print_string(g.screen, "(Game must be restarted to take effect)",
            g.font[0][22], -1, (xstart+240, ystart+60), g.colors["white"])
    #mouse grab
    string = "No"
    if pygame.event.get_grab(): 
        string = "Yes"
    g.print_string(g.screen, "Mouse grab: "+string,
            g.font[0][22], -1, (xstart+20, ystart+90), g.colors["white"])
    #Resolution
    string = str(g.screen_size[0])+"x"+str(g.screen_size[1])
    g.print_string(g.screen, "Resolution: "+string,
            g.font[0][22], -1, (xstart+20, ystart+120), g.colors["white"])
    #Language
    g.print_string(g.screen, "Language:",
            g.font[0][22], -1, (xstart+20, ystart+200), g.colors["white"])
