#! /usr/bin/env python
#file: singularity.py
#Copyright (C) 2005, 2006, 2007 Evil Mr Henry, Phil Bordelon, and Brian Reid
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

#This file is the starting file for the game. Run it to start the game.

import ConfigParser
import pygame
import sys
import os.path

import g, graphics.g
from screens import main_menu, map

pygame.init()
pygame.font.init()
pygame.key.set_repeat(1000, 50)

#load prefs from file:
save_dir = g.get_save_folder(True)
save_loc = os.path.join(save_dir, "prefs.dat")
if os.path.exists(save_loc):

    prefs = ConfigParser.SafeConfigParser()
    savefile = open(save_loc, "r")
    try:
        prefs.readfp(savefile)
    except Exception, reason:
        sys.stderr.write("Cannot load preferences file %s! (%s)\n" % (save_loc, reason))
        sys.exit(1)

    if prefs.has_section("Preferences"):
        try:
            if prefs.getboolean("Preferences", "fullscreen"):
                graphics.g.fullscreen = pygame.FULLSCREEN
        except:
            sys.stderr.write("Invalid 'fullscreen' setting in preferences.\n")

        try:
            g.nosound = prefs.getboolean("Preferences", "nosound")
        except:
            sys.stderr.write("Invalid 'nosound' setting in preferences.\n")

        try:
            pygame.event.set_grab(prefs.getint("Preferences", "grab"))
        except:
            sys.stderr.write("Invalid 'grab' setting in preferences.\n")

        try:
            graphics.g.screen_size = (prefs.getint("Preferences", "xres"),
            graphics.g.screen_size[1])
        except:
            sys.stderr.write("Invalid 'xres' resolution in preferences.\n")

        try:
            graphics.g.screen_size = (graphics.g.screen_size[0],
            prefs.getint("Preferences", "yres"))
        except:
            sys.stderr.write("Invalid 'yres' resolution in preferences.\n")

        #If language is unset, default to English.
        try: desired_language = prefs.get("Preferences", "lang")
        except: desired_language = "en_US"
        try:
            if os.path.exists(g.data_loc + "strings_" + desired_language + ".dat"):
                g.language = desired_language
                g.set_locale()
        except:
            sys.stderr.write("Cannot find language files for language '%s'.\n" % desired_language)

#Handle the program arguments.
sys.argv.pop(0)
arg_modifier = ""
for argument in sys.argv:
    if arg_modifier == "language":
        #I'm not quite sure if this can be used as an attack, but stripping
        #these characters should annoy any potential attacks.
        argument = argument.replace(os.path.sep, "")
        argument = argument.replace(os.path.pathsep, "")
        argument = argument.replace("/", "")
        argument = argument.replace("\\", "")
        argument = argument.replace(".", "")
        g.language = argument
        g.set_locale()
        arg_modifier = ""
        continue
    if argument.lower().startswith("-psn_"):
        # OSX passses this when starting the py2app .app.
        # Keep it from giving an "unknown arg" warning.
        continue
    elif argument.lower() == "-fullscreen":
        graphics.g.fullscreen = pygame.FULLSCREEN
    elif argument.lower() == "-640":
        g.screen_size = (640, 480)
    elif argument.lower() == "-800":
        g.screen_size = (800, 600)
    elif argument.lower() == "-1024":
        g.screen_size = (1024, 768)
    elif argument.lower() == "-1280":
        g.screen_size = (1280, 1024)
    elif argument.lower() == "-cheater":
        g.cheater = 1
    elif argument.lower() == "-nosound":
        g.nosound = 1
    elif argument.lower() == "-debug":
        g.debug = 1
    elif argument.lower() == "-grab":
        pygame.event.set_grab(1)
    elif argument.lower() == "-singledir":
        g.force_single_dir = True
    elif argument.lower() == "-language":
        arg_modifier = "language"
    else:
        print "Unknown argument of " + argument
        print "Allowed arguments: -fullscreen, -640, -800, -1024, -1280,",
        print " -nosound, -language [language], -grab, -singledir"
        sys.exit(1)
if arg_modifier == "language":
    print "-language option requires language to be specified."
    sys.exit(1)

g.load_strings()
g.load_events()

pygame.display.set_caption("Endgame: Singularity")

#I can't use the standard image dictionary, as that requires the screen to
#be created.
if pygame.image.get_extended() == 0:
    print "Error: SDL_image required. Exiting."
    sys.exit(1)

# Initialize the screen with a dummy size.
pygame.display.set_mode((1,1))

#init data:
g.init_graphics_system()
g.reinit_mixer()
g.load_sounds()
g.load_items()
g.load_music()
g.load_locations()

# Set the application icon.
pygame.display.set_icon(graphics.g.images["icon.png"])

#Display the main menu
menu_screen = main_menu.MainMenu()
menu_screen.show()
