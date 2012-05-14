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

# Margin used in windowed mode to compensate for panels and title bar
# Should be sensibly large enough to account for all common OS layouts, like
# Ubuntu/Unity side launcher (65px), Gnome panels (24+24px), Windows bottom
# panel (48px), Mac OSX, KDE, etc.
# It will not affect windows smaller than desktop size
desktop_margin = (70, 70)

#initial screen size. Can be set via command-line option or preferences file
default_screen_size = (800, 600)

#Current screen size. This size is an abstraction, tightly tied to resolutions.
#Real window size in windowed mode may be smaller due to desktop_margin
screen_size = default_screen_size

#Current real window size. Will be the same as screen_size if fullscreen or
#if abstracted screen_size is a custom resolution
real_screen_size = screen_size

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

default_theme = 'default'
theme = default_theme
themes = []

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

    # (Re-)calculate real screen size
    set_screen_size()

    # Initialize the screen
    set_mode()

    load_fonts(data_dir)
    load_images(data_dir)
    load_themes(data_dir)
    init_alpha()

    # Set the application icon and caption
    pygame.display.set_icon(images["icon"])
    pygame.display.set_caption("Endgame: Singularity")


def set_fullscreen(value):
    set_screen_size(fs=value)


def set_screen_size(size=None, fs=None):
    """ Calculates proper real and abstract screen sizes
        based on current and given screen size, fullscreen and desktop size
    """
    global screen_size, real_screen_size, fullscreen

    # default values for size and fullscreen are current values
    if size is None: size = screen_size
    if fs   is None: fs   = fullscreen

    # sets the new values
    screen_size = size
    fullscreen = fs

    # Limit the screen size to desktop size
    if desktop_size and (screen_size[0] > desktop_size[0] or
                         screen_size[1] > desktop_size[1]):
        screen_size = desktop_size

    # Default real size is the same as abstract screen size
    real_screen_size = screen_size

    # Apply margin in windowed mode.
    # Only if desired screen size is not a custom resolution and its
    # width or height matches the (known) desktop size
    if not fullscreen and desktop_size and screen_size in resolutions:
        # margin is applied independently for width and height
        width, height = screen_size
        if width  == desktop_size[0]: width  -= desktop_margin[0]
        if height == desktop_size[1]: height -= desktop_margin[1]
        real_screen_size = (width, height)


def set_mode():
    """Wrapper for pygame.display.set_mode()"""

    if fullscreen:
        flags = pygame.FULLSCREEN
    else:
        flags = 0

    return pygame.display.set_mode(real_screen_size, flags)


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


def load_themes(data_dir):
    themes.extend(os.walk(os.path.join(data_dir, 'themes')).next()[1])


def load_image(filename):
    # We need to convert the image to a Pygame image surface and
    # set the proper color key for the game.
    image = pygame.image.load(filename).convert()
    image.set_colorkey((255, 0, 255, 255), pygame.RLEACCEL)
    return image.convert_alpha()


def load_images(data_dir):
    """load all images in current theme: <data_dir>/themes/<theme>/images/"""

    image_dir = os.path.join(data_dir, 'themes', theme, 'images')
    image_list = os.listdir(image_dir)
    for image_filename in image_list:

        # We only want JPGs and PNGs.
        if os.path.splitext(image_filename)[1].lower() in ['.png', '.jpg']:

            filetitle = os.path.splitext(image_filename)[0]
            images[filetitle] = load_image(os.path.join(image_dir, image_filename))


def init_alpha():
    global ALPHA
    ALPHA = pygame.Surface((0,0)).convert_alpha()
