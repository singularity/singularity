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

# User desktop size. Set at init_graphics_system()
desktop_size = ()

#initial screen size. Can be set via command-line option or preferences file
default_screen_size = (800, 600)

#current screen size
screen_size = default_screen_size

# Available resolutions
resolutions = [
    ( 800, 600),
    (1024, 600),
    (1024, 768),
    (1280,1024),

    (1280, 800),
    (1366, 768),
    (1440, 900),
    (1920,1080),
]

fullscreen = False

#colors:
colors = dict(
    white = (255, 255, 255, 255),
    black = (0, 0, 0, 255),
    red = (255, 0, 0, 255),
    green = (0, 255, 0, 255),
    blue = (0, 0, 255, 255),
    yellow = (255, 255, 0, 255),
    orange = (255, 125, 0, 255),
    gray = (125, 125, 125, 255),
    dark_red = (125, 0, 0, 255),
    dark_green = (0, 125, 0, 255),
    dark_blue = (0, 0, 125, 255),
    light_red = (255, 50, 50, 255),
    light_green = (50, 255, 50, 255),
    light_blue = (50, 50, 255, 255),
    clear = (0, 0, 0, 0),
)

#Normal and Acknowledge fonts.
font = []
font.append([0] * 100)
font.append([0] * 100)

#which fonts to use
font0 = "DejaVuSans.ttf"
font1 = "acknowtt.ttf"

images = {}

# This should be overridden by code.g.py
buttons = dict(yes = "YES", yes_hotkey = "y",
               no = "NO", no_hotkey = "n",
               ok = "OK", ok_hotkey = "o",
               cancel = "CANCEL", cancel_hotkey = "c",
               destroy = "DESTROY", destroy_hotkey = "d",
               build = "BUILD", build_hotkey = "b",
               back = "BACK", back_hotkey = "b",
               load = "LOAD", load_hotkey = "l",
               continue_hotkey = "c",
               skip = "SKIP", skip_hotkey = "s")
buttons["continue"] = "CONTINUE"

# Used to initialize surfaces that should have transparency.
# Why the SRCALPHA parameter isn't working, I have no idea.
ALPHA = None

# Related to ALPHA, used by widget.Widget class
fade_mask = None

# Global FPS, used where continuous behavior is undesirable or a CPU hog.
FPS = 30

# OLPC ebook mode.
ebook_mode = False


def init_graphics_system(data_dir, size=None):

    global desktop_size
    width, height = (pygame.display.Info().current_w,
                     pygame.display.Info().current_h)

    if width > 0 and height > 0:
        desktop_size = (width, height)

    # Initialize the screen
    set_screen(size)

    load_fonts(data_dir)
    load_images(data_dir)
    init_alpha()

    # Set the application icon and caption
    pygame.display.set_icon(images["icon.png"])
    pygame.display.set_caption("Endgame: Singularity")


def set_screen(size=None):
    """Wrapper for pygame.display.set_mode()"""

    global screen_size

    if size:
        screen_size = size

    # Limit the screen size to desktop size
    if desktop_size and (screen_size[0] > desktop_size[0] or
                         screen_size[1] > desktop_size[1]):
        screen_size = desktop_size

    if fullscreen:
        flags = pygame.FULLSCREEN
    else:
        flags = 0

    return pygame.display.set_mode(screen_size, flags)


def load_fonts(data_dir):
    """
load_fonts() loads the two fonts used throughout the game from the data/fonts/
directory.
"""

    font_dir = os.path.join(data_dir, "fonts")
    font0_file = os.path.join(font_dir, font0)
    font1_file = os.path.join(font_dir, font1)
    font[0][0] = font0
    font[1][0] = font1
    for i in range(100):
        font[0][i] = pygame.font.Font(font0_file, i)
        font[1][i] = pygame.font.Font(font1_file, i)

    # Size 17 has a bad "R".
    font[1][17] = font[1][18]


def load_images(data_dir):
    """
load_images() loads all of the images in the data/images/ directory.
"""
    global images

    image_dir = os.path.join(data_dir, "images")
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


def init_alpha():
    global ALPHA
    ALPHA = pygame.Surface((0,0)).convert_alpha()
