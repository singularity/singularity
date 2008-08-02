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
import optparse

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
desc = """Endgame: Singularity is a simulation of a true AI. Go from computer to computer, pursued by the entire world. Keep hidden, and you might have a chance."""
parser = optparse.OptionParser(version=g.version, description=desc, 
                               prog="singularity")
parser.add_option("--nosound", action="store_false", dest="sound", 
                  default=True, help="disable sound")
langs = g.available_languages()
parser.add_option("-l", "--lang", "--language", dest="language", type="choice",
                  choices=langs, metavar="LANG",
                  help="set the language to LANG (available languages: " +
                       " ".join(langs) + ")")
parser.add_option("-g", "--grab", help="grab the mouse pointer",
                  action="store_true", default=False)
parser.add_option("-s", "--singledir", 
                  help="keep saved games and settings in the Singularity directory",
                  action="store_true", default=False)

display_options = optparse.OptionGroup(parser, "Display Options")
display_options.add_option("-r", "--res", "--resolution", dest="resolution",
                           help="set resolution to RES (e.g. 800x600)",
                           metavar="RES")
for common_res in [(640,480), (800,600), (1024,768), (1280,1024)]:
    x = str(common_res[0])
    res_str = "%dx%d" % common_res
    display_options.add_option("--" + x, action="store_const", 
                               dest="resolution", const=res_str,
                               help="set resolution to %s" % res_str)
display_options.add_option("--fullscreen", action="store_true", default=False,
                           help="start in fullscreen mode")
parser.add_option_group(display_options)

hidden_options = optparse.OptionGroup(parser, "Hidden Options")
hidden_options.add_option("-p", help="(ignored)", metavar=" ")
hidden_options.add_option("-d", "--debug", help="for finding bugs",
                          action="store_true", default=False)
hidden_options.add_option("--cheater", help="for bad little boys and girls",
                          action="store_true", default=False)
# Uncomment to make the hidden options visible.
#parser.add_option_group(hidden_options)

(options, args) = parser.parse_args()
if options.language:
    g.language = options.language
    g.set_locale()

if options.resolution:
    try:
        xres, yres = options.resolution.split("x")
        graphics.g.screen_size = (int(xres), int(yres))
    except Exception:
        parser.error("Resolution must be of the form <h>x<v>, e.g. 800x600.")

if options.grab:
    pygame.event.set_grab(True)

graphics.g.fullscreen = options.fullscreen
g.cheater = options.cheater
g.nosound = not options.sound
g.debug = options.debug
g.singledir = options.singledir

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
