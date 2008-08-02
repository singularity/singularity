#file: g.py
#Copyright (C) 2005,2006,2007,2008 Evil Mr Henry, Phil Bordelon, Brian Reid,
#                        and FunnyMan3595
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

#This file contains all global objects.

import os.path
import pygame

#size of the screen. This can be set via command-line option.
screen_size = (800, 600)

fullscreen = 0

#colors:
colors = {}

def fill_colors():
    colors["white"] = (255, 255, 255, 255)
    colors["black"] = (0, 0, 0, 255)
    colors["red"] = (255, 0, 0, 255)
    colors["green"] = (0, 255, 0, 255)
    colors["blue"] = (0, 0, 255, 255)
    colors["yellow"] = (255, 255, 0, 255)
    colors["orange"] = (255, 125, 0, 255)
    colors["gray"] = (125, 125, 125, 255)
    colors["dark_red"] = (125, 0, 0, 255)
    colors["dark_green"] = (0, 125, 0, 255)
    colors["dark_blue"] = (0, 0, 125, 255)
    colors["light_red"] = (255, 50, 50, 255)
    colors["light_green"] = (50, 255, 50, 255)
    colors["light_blue"] = (50, 50, 255, 255)

#
# Font functions.
#

#Normal and Acknowledge fonts.
font = []
font.append([0] * 51)
font.append([0] * 51)

#which fonts to use
font0 = "DejaVuSans.ttf"
font1 = "acknowtt.ttf"

def load_fonts(data_loc):
    """
load_fonts() loads the two fonts used throughout the game from the data/fonts/
directory.
"""

    global font

    font_dir = os.path.join(data_loc, "fonts")
    font0_file = os.path.join(font_dir, font0)
    font1_file = os.path.join(font_dir, font1)
    for i in range(8, 51):
        font[0][i] = pygame.font.Font(font0_file, i)
        font[1][i] = pygame.font.Font(font1_file, i)

images = {}
def load_images(data_loc):
    """
load_images() loads all of the images in the data/images/ directory.
"""
    global images

    image_dir = os.path.join(data_loc, "images")
    image_list = os.listdir(image_dir)
    for image_filename in image_list:

        # We only want JPGs and PNGs.
        if len(image_filename) > 4 and (image_filename[-4:] == ".png" or
         image_filename[-4:] == ".jpg"):

            # We need to convert the image to a Pygame image surface and
            # set the proper color key for the game.
            images[image_filename] = pygame.image.load(
             os.path.join(image_dir, image_filename)).convert()
            images[image_filename].set_colorkey((255, 0, 255, 255),
             pygame.RLEACCEL)

# This should be overridden by code.g.py
buttons = dict(yes = "yes", yes_hotkey = "y",
               no = "no", no_hotkey = "n",
               ok = "ok", ok_hotkey = "o",
               cancel = "cancel", cancel_hotkey = "c",
               destroy = "destroy", destroy_hotkey = "d",
               back = "back", back_hotkey = "b")

# Used to initialize surfaces that should have transparency.
# Why the SRCALPHA parameter isn't working, I have no idea.
ALPHA = None

def init_alpha():
    global ALPHA
    ALPHA = pygame.Surface((0,0)).convert_alpha()

# Global FPS, used where continuous behavior is undesirable or a CPU hog.
FPS = 30
