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

import buttons
from buttons import always, void, exit

#screen is the actual pygame display.
global screen

#size of the screen. This can be set via command-line option.
screen_size = (800, 600)

#colors:
colors = {}

def fill_colors():
    colors["white"] = (255, 255, 255, 255)
    colors["black"] = (0, 0, 0, 255)
    colors["red"] = (255, 0, 0, 255)
    colors["green"] = (0, 255, 0, 255)
    colors["blue"] = (0, 0, 255, 255)
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

#create dialog with OK button.
def create_dialog(string_to_print, box_font = None, xy = None, size = (250,250),
                  bg_color = None, out_color = None, text_color = None):
    # Defaults that reference other variables, which may not be initialized when
    # the function is defined.
    if box_font == None:
        box_font = font[0][18]
    if xy == None:
        xy = ( (screen_size[0] / 2) - 100, 50)
    if bg_color == None:
        bg_color = colors["dark_blue"]
    if out_color == None:
        out_color = colors["white"]
    if text_color == None:
        text_color = colors["white"]

    screen.fill(out_color, (xy[0], xy[1], size[0], size[1]))
    screen.fill(bg_color, (xy[0]+1, xy[1]+1, size[0]-2, size[1]-2))
    print_multiline(screen, string_to_print, box_font, size[0]-10,
            (xy[0]+5, xy[1]+5), text_color)
    menu_buttons = {}
    menu_buttons[buttons.make_norm_button((xy[0]+size[0]/2-50,
            xy[1]+size[1]+5), (100, 50), "OK", "O", font[1][30])] = always(True)

    buttons.show_buttons(menu_buttons)

#create dialog with YES/NO buttons.
def create_yesno(string_to_print, box_font, xy, size, bg_color, out_color,
            text_color, button_names=("YES", "NO"), reverse_key_context = False):
    screen.fill(out_color, (xy[0], xy[1], size[0], size[1]))
    screen.fill(bg_color, (xy[0]+1, xy[1]+1, size[0]-2, size[1]-2))
    print_multiline(screen, string_to_print, box_font, size[0]-10,
                (xy[0]+5, xy[1]+5), text_color)
    menu_buttons = {}
    if button_names == ("YES", "NO"):
        menu_buttons[buttons.make_norm_button((xy[0]+size[0]/2-110,
                xy[1]+size[1]+5), (100, 50), button_names[0], "Y", font[1][30])] = always(True)
        menu_buttons[buttons.make_norm_button((xy[0]+size[0]/2+10,
                xy[1]+size[1]+5), (100, 50), button_names[1], "N", font[1][30])] = always(False)
    else:
        menu_buttons[buttons.make_norm_button((xy[0],
                xy[1]+size[1]+5), -1, button_names[0], button_names[0][0], font[1][30])] = always(True)
        menu_buttons[buttons.make_norm_button((xy[0]+size[0]-100,
                xy[1]+size[1]+5), -1, button_names[1], button_names[1][0], font[1][30])] = always(False)


    default = False
    if reverse_key_context:
        default = True

    return buttons.show_buttons(menu_buttons, 
                               key_callback=buttons.simple_key_handler(default))

valid_input_characters = ('a','b','c','d','e','f','g','h','i','j','k','l','m',
                        'n','o','p','q','r','s','t','u','v','w','x','y','z',
                        'A','B','C','D','E','F','G','H','I','J','K','L','M',
                        'N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
                        '0','1','2','3','4','5','6','7','8','9','.',' ')

def create_textbox(descript_text, starting_text, box_font, xy, size,
            max_length, bg_color, out_color, text_color, text_bg_color):
    screen.fill(out_color, (xy[0], xy[1], size[0], size[1]))
    screen.fill(bg_color, (xy[0]+1, xy[1]+1, size[0]-2, size[1]-2))
    screen.fill(out_color, (xy[0]+5, xy[1]+size[1]-30, size[0]-10, 25))
    print_multiline(screen, descript_text, box_font,
                                size[0]-10, (xy[0]+5, xy[1]+5), text_color)

    # Cursor starts at the end.
    global cursor_loc, work_string
    cursor_loc = len(starting_text)

    def give_text():
        return work_string

    menu_buttons = {}
    menu_buttons[buttons.make_norm_button((xy[0]+size[0]/2-50,
            xy[1]+size[1]+5), (100, 50), "OK", "", font[1][30])] = give_text

    work_string = starting_text
    sel_button = -1

    key_down_dict = {
        pygame.K_BACKSPACE: False,
        pygame.K_DELETE: False,
        pygame.K_LEFT: False,
        pygame.K_RIGHT: False
    }
    key_down_time_dict = {
        pygame.K_BACKSPACE: 0,
        pygame.K_DELETE: 0,
        pygame.K_LEFT: 0,
        pygame.K_RIGHT: 0
    }
    repeat_timing_dict = {
        pygame.K_BACKSPACE: 6,
        pygame.K_DELETE: 6,
        pygame.K_LEFT: 6,
        pygame.K_RIGHT: 6
    }

    def on_tick(tick_len):
        global cursor_loc, work_string
        need_redraw = False

        keys = (pygame.K_BACKSPACE, pygame.K_DELETE, pygame.K_LEFT, 
                pygame.K_RIGHT)
        backspace, delete, left, right = keys
        for key in keys:
            if key_down_time_dict[key]:
                i_need_redraw = False

                key_down_time_dict[key] += 1
                if key_down_time_dict[key] > repeat_timing_dict[key]:
                    key_down_time_dict[key] = 1
                    if repeat_timing_dict[key] > 1:
                        repeat_timing_dict[key] -= 1

                    i_need_redraw = True
                    if key == backspace and cursor_loc > 0:
                        work_string = work_string[:cursor_loc-1] + \
                                      work_string[cursor_loc:]
                        cursor_loc -= 1
                    elif key == delete and cursor_loc < len(work_string):
                        work_string = work_string[:cursor_loc] + \
                                      work_string[cursor_loc+1:]
                    elif key == left and cursor_loc > 0:
                        cursor_loc -= 1
                    elif key == right and cursor_loc < len(work_string):
                        cursor_loc += 1
                    else:
                        # Nothing happened.
                        i_need_redraw = False

                if not key_down_dict[key]:
                    key_down_time_dict[key] = 0
                    repeat_timing_dict[key] = 6

                need_redraw = need_redraw or i_need_redraw

        return need_redraw

    def do_refresh():
        draw_cursor_pos = box_font.size(work_string[:cursor_loc])
        screen.fill(text_bg_color, (xy[0]+6, xy[1]+size[1]-29,
                    size[0]-12, 23))
        screen.fill(text_color, (xy[0]+6+draw_cursor_pos[0], xy[1]+size[1]-28,
                1, draw_cursor_pos[1]))
        print_string(screen, work_string, box_font, -1, (xy[0]+7,
                    xy[1]+size[1]-28), text_color)

    def on_key_down(event):
        key = event.key
        global cursor_loc, work_string
        if key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            return work_string
        if key == pygame.K_ESCAPE:
            return ""

        if event.unicode in valid_input_characters:
            if cursor_loc < max_length:
                work_string = work_string[:cursor_loc]+event.unicode+ \
                                            work_string[cursor_loc:]
                cursor_loc += 1
            return

        # Mark the key as down.
        key_down_dict[key] = True
        # And force it to trigger immediately.
        key_down_time_dict[key] = 6

    def on_key_up(event):
        key = event.key
        # Mark the key as up, but don't clear its down time.
        key_down_dict[key] = False

    def on_click(event):
        global cursor_loc
        if event.button == 1:
            if (event.pos[0] > xy[0]+6 and event.pos[1] > xy[1]+size[1]-29 and
             event.pos[0] < xy[0]+size[0]-6 and event.pos[1] < xy[1]+size[1]-6):
                cursor_x = event.pos[0] - (xy[0]+6)
                prev_x = 0
                for i in range(1, len(work_string)):
                    curr_x = box_font.size(work_string[:i])[0]
                    if (curr_x + prev_x) / 2 >= cursor_x:
                        cursor_loc=i-1
                        break
                    elif curr_x >= cursor_x:
                        cursor_loc=i
                        break
                    prev_x = curr_x
                else:
                    cursor_loc=len(work_string)

    return buttons.show_buttons(menu_buttons, click_callback=on_click,
                                  tick_callback=on_tick, 
                                  key_callback=on_key_down,
                                  keyup_callback=on_key_up,
                                  refresh_callback=do_refresh)

#which fonts to use
font0 = "DejaVuSans.ttf"
font1 = "acknowtt.ttf"

data_loc = "../../data/"

def load_fonts():
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
def load_images():
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


load_fonts()
load_images()
fill_colors()

ALPHA = pygame.Surface((0,0)).convert_alpha()
FPS = 30
