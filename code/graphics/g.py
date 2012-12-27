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

# User desktop size
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

# Standard resolutions
# Order DOES matter: first ones in each wide/non-wide "group" are more likely
# to be selected in Options Screen, so they should reflect popularity
# They will always be displayed in ascending size order
resolutions = [
    # 4:3 "Fullscreen"
    (1024, 768),  # 4:3, the former top 1, classics never die
    (1280,1024),  # 5:4, old power users
    (1152, 864),  # 4:3, XGA+, old 17"~21" monitors
    ( 800, 600),  # 4:3, another old classic. Safest "playable" resolution
    (1280, 960),  # 4:3, "SXGA-"
    (1600,1200),  # 4:3, UXGA, some old power monitors and notebooks
    (1400,1050),  # 4:3, SXGA+, middle ground between the 2 above
    (2048,1536),  # 4:3, QXGA, iPad 3rd/4th generation
    ( 640, 480),  # 4:3, I hope this is a smartphone...

    # Widescreen
    (1366, 768),  # 16:9 , Worldwide top 1 resolution
    (1280, 800),  # 16:10, WXGA, widely used in 14/15" notebooks
    (1920,1080),  # 16:9 , Full HD, TVs and LCD monitors
    (1440, 900),  # 16:10, WSXGA, 19" LCD monitors or power notebooks
    (1680,1050),  # 16:10, WSXGA+, 22" LCD monitors or power notebooks
    (1024, 600),  # 16:~9, WSVGA, very popular in 7"~10" netbooks and tablets
    (1600, 900),  # 16:9 , HD+ (900p), popular for notebooks
    (1280, 720),  # 16:9 , HD, TVs and LCD monitors
    (1920,1200),  # 16:10, WUXGA, 23"~28" power monitors and Apple notebooks
    (2560,1440),  # 16:9 , QHD, modern 27" monitors
    (2560,1600),  # 16:10, WQXGA, modern 30"+ monitors (I envy you)
    (3840,2160),  # 16:9 , FQHD, 4K-you-gotta-be-kidding-me TV

    # Smartphones
    ( 960, 640),  #  3:2, DVGA, iPhone 4/4S
    ( 800, 480),  # 15:9, WVGA, Androids and also early Asus EeePC
    ( 854, 480),  # 16:9, FWVGA, Sony Xperia and others

    # Odd-sized but still common, usually similar to more popular ones
    # Being at bottom these are unlikely to be displayed unless matches desktop
    (1024, 686),  # ~3:2, WSVGA variant
    (1024, 576),  # 16:9, WSVGA variant
    (1280, 768),  # 15:9, WXGA variant
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


def init_desktop_size():
    global desktop_size
    width, height = (pygame.display.Info().current_w,
                     pygame.display.Info().current_h)

    # Was pygame able to probe desktop size?
    if not (width > 0 and height > 0):
        return

    # We have a valid desktop size
    desktop_size = (width, height)

    # Insert (or move) desktop resolution to top of list
    if desktop_size in resolutions:
        resolutions.remove(desktop_size)
    resolutions.insert(0, desktop_size)

    # Calculate real screen size
    set_screen_size()


def init_graphics_system(data_dir, size=None):

    # Initialize the screen
    set_mode()

    load_fonts(data_dir)
    load_images(data_dir)
    init_alpha()

    # Set the application icon and caption
    pygame.display.set_icon(images["icon.png"])
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
    if not fits_desktop(screen_size):
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


def fits_desktop(res):
    """Return True if res <= desktop_size for both width and height
    or desktop_size is not set
    """
    return ((not desktop_size) or
            (res[0] <= desktop_size[0]) and (res[1] <= desktop_size[1]))


def is_wide(res):
    """Return True if res ratio >= 1.5 (16:9, 16:10, 3:2) or not defined,
    False otherwise (4:3, 5:4, or any "portrait" resolution)"""
    return (not res) or ((float(res[0]) / float(res[1])) >= 1.5)


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
