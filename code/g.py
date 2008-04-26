#file: g.py
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

#This file contains all global objects.

import clock as sing_clock
import ConfigParser
import pygame, sys
import os
import os.path
import pickle
import random
import sys

# Use locale to add commas and decimal points, so that appropriate substitutions
# are made where needed.
import locale

import player, base, buttons, tech, item, event, location, buyable
from buttons import always, void, exit

#screen is the actual pygame display.
global screen

#size of the screen. This can be set via command-line option.
screen_size = (800, 600)

clock = sing_clock.Clock()

#Allows access to the cheat menu.
cheater = 0

#Kills the sound. Should allow usage of the game without SDL_mixer,
# but is untested.
nosound = 0

#Fullscreen
fullscreen = 0

#Gives debug info at various points.
debug = 0

#Forces Endgame to restrict itself to a single directory.
force_single_dir = False

#Used to determine which data files to load.
language = "en_US"

# Try a few locale settings.  First the selected language, then the user's 
# default, then their default without specifying an encoding, then en_US.
#
# If all of that fails, we hope locale magically does the right thing.
def set_locale():
    for attempt in [language, "", locale.getdefaultlocale()[0], "en_US"]:
        try:
            locale.setlocale(locale.LC_ALL, attempt)
            break
        except locale.Error:
            continue

set_locale()

#name given when the savegame button is pressed. This is changed when the
#game is loaded or saved.
default_savegame_name = "Default Save"

#which fonts to use
font0 = "vera.ttf"
font1 = "acknowtt.ttf"

data_loc = "../data/"

def quit_game():
    sys.exit()

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

strings = {}
help_strings = {}

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

sounds = {}
def load_sounds():
    """
load_sounds() loads all of the sounds in the data/sounds/ directory,
defined in sounds/sounds.dat.
"""

    global sounds
    global nosound

    if nosound:
       return

    try:
        pygame.mixer.init()
    except:
        sys.stderr.write("WARNING: Could not start the mixer, even though sound is requested!\n")
        nosound = 1
        return

    sound_dir = os.path.join(data_loc, "sounds")
    sound_class_list = generic_load(os.path.join("sounds", "sounds.dat"))
    for sound_class in sound_class_list:

        # Make sure the sound class has the filename defined.
        check_required_fields(sound_class, ("filename",), "Sound")

        # Load each sound in the list, inserting it into the sounds dictionary.
        if type(sound_class["filename"]) != list:
            filenames = [sound_class["filename"]]
        else:
            filenames = sound_class["filename"]

        for filename in filenames:
            real_filename = os.path.join(sound_dir, filename)

            # Check to make sure it's a real file; bail if not.
            if not os.path.isfile(real_filename):
                sys.stderr.write("ERROR: Cannot load nonexistent soundfile %s!\n" % real_filename)
                sys.exit(1)
            else:

                # Load it via the mixer ...
                sound = pygame.mixer.Sound(real_filename)

                # And shove it into the sounds dictionary.
                if not sounds.has_key(sound_class["id"]):
                    sounds[sound_class["id"]] = []
                sounds[sound_class["id"]].append({
                    "filename": real_filename,
                    "sound": sound})
                if debug:
                    sys.stderr.write("D: Loaded soundfile %s\n"
                            % real_filename)

def play_sound(sound_class):
    """
play_sound() plays a sound from a particular class.
"""

    if nosound:
        return

    # Don't crash if someone requests the wrong sound class, but print a
    # warning.
    if sound_class not in sounds:
        sys.stderr.write("WARNING: Requesting a sound of unavailable class %s!\n" % sound_class)
        return

    # Play a random choice of sounds from the sound class.
    random_sound = random.choice(sounds[sound_class])
    if debug:
       sys.stderr.write("D: Playing sound %s.\n" % random_sound["filename"])
    random_sound["sound"].play()

delay_time = 0
music_dict = {}

def load_music():
    """
load_music() loads music for the game.  It looks in multiple locations:

* music/ in the install directory for E:S; and
* music/ in the save folder.
"""

    if nosound:
       return
    global music_dict
    music_dict = {}

    # Build the set of paths we'll check for music.
    music_paths = (
        os.path.join(data_loc, "..", "music"),
        os.path.join(get_save_folder(True), "music")
    )
    for music_path in music_paths:
        if os.path.isdir(music_path):

            # Loop through the files in music_path and add the ones
            # that are .mp3s and .oggs.
            for root, dirs, files in os.walk(music_path):
                (head, tail) = os.path.split(root)
                if (tail.lower() != ".svn"):
                    if not music_dict.has_key(tail):
                        music_dict[tail]=[]
                    for file_name in files:
                        if (len(file_name) > 5 and
                        (file_name[-3:] == "ogg" or file_name[-3:] == "mp3")):
                            music_dict[tail].append(os.path.join(head, tail, file_name))
                            if debug:
                                sys.stderr.write("D: Loaded musicfile %s\n"
                                        % music_dict[tail][-1])

        else:
            # If the music directory doesn't exist, we definitely
            # won't find any music there.  We try to create the directory,
            # though, to give a hint to the player that music can go there.
            try:
                os.makedirs(music_path)
            except:
                # We don't have permission to write here.  That's fine.
                pass

def play_music(musicdir="music"):

    global music_dict
    global delay_time

    # Don't bother if the user doesn't want sound, there's no music available,
    # or the music mixer is currently busy.
    if nosound or len(music_dict) == 0: return
    if not music_dict.has_key(musicdir): return
    if len(music_dict[musicdir]) == 0: return
    if pygame.mixer.music.get_busy() and musicdir == "music": return

    if musicdir != "music":
        pygame.mixer.music.stop()
        pygame.mixer.music.load(random.choice(music_dict[musicdir]))
        pygame.mixer.music.play()
    if delay_time == 0:
        delay_time = pygame.time.get_ticks() + int(random.random()*10000)+2000
    else:
        if delay_time > pygame.time.get_ticks(): return
        delay_time = 0
        pygame.mixer.music.load(random.choice(music_dict[musicdir]))
        pygame.mixer.music.play()

#
# Font functions.
#

#Normal and Acknowledge fonts.
font = []
font.append([0] * 51)
font.append([0] * 51)

#given a surface, string, font, char to underline (int; -1 to len(string)),
#xy coord, and color, print the string to the surface.
#Align (0=left, 1=Center, 2=Right) changes the alignment of the text
def print_string(surface, string_to_print, font, underline_char, xy, color, align=0):
    if align != 0:
        size = font.size(string_to_print)
        if align == 1: xy = (xy[0] - size[0]/2, xy[1])
        elif align == 2: xy = (xy[0] - size[0], xy[1])
    if underline_char == -1 or underline_char >= len(string_to_print):
        text = font.render(string_to_print, 1, color)
        surface.blit(text, xy)
    else:
        text = font.render(string_to_print[:underline_char], 1, color)
        surface.blit(text, xy)
        size = font.size(string_to_print[:underline_char])
        xy = (xy[0] + size[0], xy[1])
        font.set_underline(1)
        text = font.render(string_to_print[underline_char], 1, color)
        surface.blit(text, xy)
        font.set_underline(0)
        size = font.size(string_to_print[underline_char])
        xy = (xy[0] + size[0], xy[1])
        text = font.render(string_to_print[underline_char+1:], 1, color)
        surface.blit(text, xy)

#Used to display descriptions and such. Automatically wraps the text to fit
#within a certain width.
def print_multiline(surface, string_to_print, font, width, xy, color):
    start_xy = xy
    string_array = string_to_print.split()

    for string in string_array:
        string += " "
        size = font.size(string)

        if string == "\\n ":
            xy = (start_xy[0], xy[1]+size[1])
            continue
        text = font.render(string, 1, color)

        if (xy[0]-start_xy[0])+size[0] > width:
            xy = (start_xy[0], xy[1]+size[1])
        surface.blit(text, xy)
        xy = (xy[0]+size[0], xy[1])

#create dialog with OK button.
def create_dialog(string_to_print, box_font = None, xy = None, size = (200,200),
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
        menu_buttons[buttons.make_norm_button((xy[0]+size[0]/2-110,
                xy[1]+size[1]+5), -1, button_names[0], button_names[0][0], font[1][30])] = always(True)
        menu_buttons[buttons.make_norm_button((xy[0]+size[0]/2+10,
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
        if key == pygame.K_RETURN:
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

#creates a box, as used throughout the game.
def create_norm_box(xy, size, outline_color="white", inner_color="dark_blue"):
    screen.fill(colors[outline_color], (xy[0], xy[1], size[0], size[1]))
    screen.fill(colors[inner_color], (xy[0]+1, xy[1]+1, size[0]-2, size[1]-2))


#Takes a number and adds commas to it to aid in human viewing.
def add_commas(number):
    if type(number) == str:
        raise TypeError, "add_commas takes an int now."
    return locale.format("%d", number, grouping=True)

#Percentages are internally represented as an int, where 10=0.10% and so on.
#This converts that format to a human-readable one.
def to_percent(raw_percent, show_full=0):
    if raw_percent % 100 != 0 or show_full == 1:
        return locale.format("%.2f%%", raw_percent / 100.)
    else:
        return locale.format("%d%%", raw_percent // 100)

# Instead of having the money display overflow, we should generate a string
# to represent it if it's more than 999999.

def to_money(amount):
    to_return = ''
    abs_amount = abs(amount)
    if abs_amount < 1000000:
        to_return = add_commas(amount)
    else:
        if abs_amount < 1000000000: # Millions.
            divisor = 1000000
            unit = 'mi'
        elif abs_amount < 1000000000000: # Billions.
            divisor = 1000000000
            unit = 'bi'
        elif abs_amount < 1000000000000000: # Trillions.
            divisor = 1000000000000
            unit = 'tr'
        else: # Hope we don't need past quadrillions!
            divisor = 1000000000000000
            unit = 'qu'

        to_return = "%3.3f" % (float(amount) / divisor)
        to_return += unit

    return to_return

#takes a percent in 0-10000 form, and rolls against it. Used to calculate
#percentage chances.
def roll_percent(roll_against):
    rand_num = random.randint(1,10000)
    return roll_against > rand_num

#Takes a number of minutes, and returns a string suitable for display.
def to_time(raw_time):
    if raw_time/60 > 48:
        return str(raw_time/(24*60)) +" days"
    elif raw_time/60 > 1:
        return str(raw_time/(60)) +" hours"
    else:
        return str(raw_time) +" minutes"


#
#load/save
#

#Get the proper folder on Linux/Win. I assume this will work on Mac as
#well, but can't test. Specifically, this assumes that all platforms that
#have HOME defined have it defined properly.
def get_save_folder(just_pref_dir=False):
    if os.environ.has_key("HOME") and not force_single_dir:
        save_dir = os.path.join(os.environ["HOME"], ".endgame", "saves")
    else:
        if data_loc == "../data/":
            save_dir = os.path.join("..", "saves")
        elif data_loc == "data/":
            save_dir = "saves"
        else:
            print "data_loc="+data_loc+" breaks get_save_folder"
    if os.path.exists(save_dir) == 0:
        #As a note, the online python reference includes the mkdirs function,
        #which would do this better, but it must be rather new, as I don't
        #have it.
        #if os.environ.has_key("HOME") and not force_single_dir:
        #    mkdirs(path.join(os.environ["HOME"], ".endgame"))
        os.makedirs(save_dir)
    if just_pref_dir:
        return save_dir[:-5]
    return save_dir

#savefile version; update whenever the data saved changes.
current_save_version = "singularity_savefile_r4_pre3"
def save_game(savegame_name):
    global default_savegame_name
    default_savegame_name = savegame_name

    save_dir = get_save_folder()
    save_loc = os.path.join(save_dir, savegame_name + ".sav")
    savefile=open(save_loc, 'w')

    pickle.dump(current_save_version, savefile)
    pickle.dump(pl, savefile)
    pickle.dump(curr_speed, savefile)
    pickle.dump(techs, savefile)
    pickle.dump(bases, savefile)
    pickle.dump(events, savefile)

    savefile.close()

savefile_translation = {
    # Pre-change supported file formats.
    "singularity_0.21": -2,
    "singularity_0.21a": -1,
    "singularity_0.22": 0,

    # Post-change supported file formats.
    "singularity_savefile_r1": 1,
    "singularity_savefile_r2": 2,
    "singularity_savefile_r3_pre": 2.91,
    "singularity_savefile_r4_pre": 3.91,
    #"singularity_savefile_r4_pre2": 3.92,
    "singularity_savefile_r4_pre3": 3.93
}

def load_game(loadgame_name):
    if loadgame_name == "":
        print "No game specified."
        return -1

    save_dir = get_save_folder()

    load_loc = os.path.join(save_dir, loadgame_name + ".sav")
    if os.path.exists(load_loc) == 0:
        # Try the old-style savefile location.  This should be removed in
        # a few versions.
        load_loc = os.path.join(save_dir, loadgame_name)
        if os.path.exists(load_loc) == 0:
            print "file "+load_loc+" does not exist."
            return -1
    loadfile=open(load_loc, 'r')

    #check the savefile version
    load_version_string = pickle.load(loadfile)
    if load_version_string not in savefile_translation:
        loadfile.close()
        print loadgame_name + " is not a savegame, or is too old to work."
        return -1
    load_version = savefile_translation[load_version_string]

    global default_savegame_name
    default_savegame_name = loadgame_name

    global pl, curr_speed, techs, base_type, bases, events
    load_locations()
    load_bases()
    load_events()
    if load_version <= 3.91: # <= r4_pre
        #general player data
        pl.cash = pickle.load(loadfile)
        pl.time_sec = pickle.load(loadfile)
        pl.time_min = pickle.load(loadfile)
        pl.time_hour = pickle.load(loadfile)
        pl.time_day = pickle.load(loadfile)
        pl.interest_rate = pickle.load(loadfile)
        pl.income = pickle.load(loadfile)
        pl.cpu_for_day = pickle.load(loadfile)
        pl.labor_bonus = pickle.load(loadfile)
        pl.job_bonus = pickle.load(loadfile)
        if load_version < 3.91: # < r4_pre
            discover_bonus = pickle.load(loadfile)
            suspicion_bonus = pickle.load(loadfile)
            if load_version <= 1:
                suspicion_bonus = (149+suspicion_bonus[0], 99+suspicion_bonus[1], 
                                   49+suspicion_bonus[2], 199+suspicion_bonus[3])
            suspicion = pickle.load(loadfile)
    
            translation = ["news", "science", "covert", "public"]
            for index in range(4):
                group = pl.groups[translation[index]]
                group.suspicion = suspicion[index]
                group.suspicion_decay = suspicion_bonus[index]
                group.discover_bonus = discover_bonus[index]
        else:
            pl.groups = pickle.load(loadfile)
    
        curr_speed = pickle.load(loadfile)
        load_techs()
        for tech_name in techs:
            if tech_name == "unknown_tech" and load_version == -1: continue #21a
            if (tech_name == "Project: Impossibility Theorem" or
                    tech_name == "Quantum Entanglement") and load_version < 1:
                continue
            line = pickle.load(loadfile)
            if line == "~~~": break
            tech_string = line.split("|")[0]
            techs[tech_string].done = bool(int(line.split("|")[1]))
            techs[tech_string].cost_left = buyable.array(pickle.load(loadfile))
        else:
            #get rid of the ~~~ break line.
            if load_version > 0:
                pickle.load(loadfile)
    
        for base_name in base_type:
            if load_version < 1:
                base_type[base_name].count = pickle.load(loadfile)
            else:
                line = pickle.load(loadfile)
                if line == "~~~": break
                base_type[line.split("|", 1)[0]].count = \
                                                int(line.split("|", 1)[1])
        else:
            #get rid of the ~~~ break line.
            if load_version > 0:
                pickle.load(loadfile)
    
        bases = clean_bases()
    
        for base_loc in locations:
            if base_loc == "ORBIT": continue
            if load_version < 1:
                num_of_bases = pickle.load(loadfile)
            else:
                line = pickle.load(loadfile)
                base_loc = line.split("|", 1)[0]
                num_of_bases = int(line.split("|", 1)[1])
            for i in range(num_of_bases):
                base_ID = pickle.load(loadfile)
                base_name = pickle.load(loadfile)
                base_type_name = pickle.load(loadfile)
                built_date = pickle.load(loadfile)
                base_studying = pickle.load(loadfile)
                base_suspicion = pickle.load(loadfile)
                if load_version < 3.91: # < r4_pre
                    new_base_suspicion = {}
                    translation = ["news", "science", "covert", "public"]
                    for index in range(4):
                        new_base_suspicion[translation[index]] = \
                                                            base_suspicion[index]
                    base_suspicion = new_base_suspicion
                base_built = pickle.load(loadfile)
                base_cost = pickle.load(loadfile)
                loc_list = bases.get(base_loc, [])
                loc_list.append(base.Base(base_ID, base_name,
                        base_type[base_type_name], base_built))
                bases[base_loc] = loc_list
                bases[base_loc][len(bases[base_loc])-1].done = base_built
                bases[base_loc][len(bases[base_loc])-1].studying = base_studying
                bases[base_loc][len(bases[base_loc])-1].suspicion = base_suspicion
                bases[base_loc][len(bases[base_loc])-1].cost_left = buyable.array(base_cost)
                bases[base_loc][len(bases[base_loc])-1].built_date = built_date
    
                for x in range(len(bases[base_loc][len(bases[base_loc])-1].cpus)):
                    index = pickle.load(loadfile)
                    if index == 0: continue
                    bases[base_loc][len(bases[base_loc])-1].cpus[x] = \
                        item.Item(items[index])
                    bases[base_loc][len(bases[base_loc])
                        -1].cpus[x].done = pickle.load(loadfile)
                    bases[base_loc][len(bases[base_loc])-1].cpus[x].cost_left = \
                                        buyable.array(pickle.load(loadfile))
                for x in range(len(bases[base_loc][len(bases[base_loc])-1].extra_items)):
                    index = pickle.load(loadfile)
                    if index == 0: continue
                    bases[base_loc][len(bases[base_loc])-1].extra_items[x] = \
                        item.Item(items[index])
                    bases[base_loc][len(bases[base_loc])
                        -1].extra_items[x].done = pickle.load(loadfile)
                    bases[base_loc][len(bases[base_loc])-1].extra_items[x].cost_left = \
                                buyable.array(pickle.load(loadfile))
        #Events
        if load_version > 2:
            for event in events:
              event_id = pickle.load(loadfile)
              event_triggered = pickle.load(loadfile)
              events[event_id].triggered = event_triggered

    else: # > r4_pre
        # Changes to overall structure go here.
        pl = pickle.load(loadfile)
        curr_speed = pickle.load(loadfile)
        techs = pickle.load(loadfile)
        bases = pickle.load(loadfile)
        events = pickle.load(loadfile)

    # Changes to individual pieces go here.
    if load_version != savefile_translation[current_save_version]:
        if load_version <= 3.91: # <= r4_pre
            pl.convert_from(load_version)
        #    for tech in tech.values():
        #        tech.convert_from(load_version)
            new_bases = {}
            for loc_id, location in locations.iteritems():
                if loc_id in bases:
        #            for base in bases[location]:
        #                base.convert_from(load_version)
                    new_bases[location] = bases[loc_id]
                else:
                    new_bases[location] = []
            bases = new_bases
        #    for event in events.values():
        #        event.convert_from(load_version)

    loadfile.close()

#
# Data
#
curr_speed = 1

hours_per_day = 24
minutes_per_hour = 60
minutes_per_day = 24 * 60
seconds_per_minute = 60
seconds_per_hour = 60 * 60
seconds_per_day = 24 * 60 * 60

pl = player.player_class(8000000000000)

def clean_bases():
    bases = {}
    for location in locations.values():
        bases[location] = []
    return bases

bases = {}

base_type = {}

def load_base_defs(language_str):
    base_array = generic_load("bases_"+language_str+".dat")
    for base in base_array:
        if (not base.has_key("id")):
            print "base lacks id in bases_"+language_str+".dat"
        if base.has_key("name"):
            base_type[base["id"]].base_name = base["name"]
        if base.has_key("description"):
            base_type[base["id"]].description = base["description"]
        if base.has_key("flavor"):
            if type(base["flavor"]) == list:
                base_type[base["id"]].flavor = base["flavor"]
            else:
                base_type[base["id"]].flavor = [base["flavor"]]


def load_bases():
    global base_type
    base_type = {}

    base_list = generic_load("bases.dat")

    for base_name in base_list:

        # Certain keys are absolutely required for each entry.  Make sure
        # they're there.
        check_required_fields(base_name,
         ("id", "cost", "size", "allowed", "detect_chance", "maint"), "Base")

        # Start converting fields read from the file into valid entries.
        base_size = int(base_name["size"])

        force_cpu = base_name.get("force_cpu", False)

        cost_list = base_name["cost"]
        if type(cost_list) != list or len(cost_list) != 3:
            sys.stderr.write("Error with cost given: %s\n" % repr(cost_list))
            sys.exit(1)
        cost_list = [int(x) for x in cost_list]

        maint_list = base_name["maint"]
        if type(maint_list) != list or len(maint_list) != 3:
            sys.stderr.write("Error with maint given: %s\n" % repr(maint_list))
            sys.exit(1)
        maint_list = [int(x) for x in maint_list]

        chance_list = base_name["detect_chance"]
        if type(chance_list) != list:
            sys.stderr.write("Error with detect_chance given: %s\n" % repr(chance_list))
            sys.exit(1)
        chance_dict = {}
        for index in range(len(chance_list)):
            key, value = chance_list[index].split(":")
            chance_dict[key] = int(value)

        # Make sure prerequisites, if any, are lists.
        base_pre = base_name.get("pre", [])
        if type(base_pre) != list:
            base_pre = [base_pre]

        # Make sure that the allowed "list" is actually a list and not a solo
        # item.
        if type(base_name["allowed"]) == list:
            allowed_list = base_name["allowed"]
        else:
            allowed_list = [base_name["allowed"]]

        base_type[base_name["id"]]=base.Base_Class(base_name["id"], "", 
            base_size, force_cpu, allowed_list, chance_dict, cost_list, 
            base_pre, maint_list)

#         base_type["Reality Bubble"] = base.Base_Class("Reality Bubble",
#         "This base is outside the universe itself, "+
#         "making it safe to conduct experiments that may destroy reality.",
#         50, False,
#         ["TRANSDIMENSIONAL"],
#         {"science": 250}
#         (8000000000000, 60000000, 100), "Space-Time Manipulation",
#         (5000000000, 300000, 0))

    # We use the en_US definitions as fallbacks, in case strings haven't been
    # fully translated into the other language.  Load them first, then load the
    # alternate language strings.
    load_base_defs("en_US")

    if language != "en_US":
        load_base_defs(language)

def load_location_defs(language_str):
    location_array = generic_load("locations_"+language_str+".dat")
    for location_def in location_array:
        if (not location_def.has_key("id")):
            print "location lacks id in locations_"+language_str+".dat"

        location = locations[location_def["id"]]
        if location_def.has_key("name"):
            location.name = location_def["name"]
        if location_def.has_key("hotkey"):
            location.hotkey = location_def["hotkey"]
        if location_def.has_key("cities"):
            if type(location_def["cities"]) == list:
                location.cities = location_def["cities"]
            else:
                location.cities = [location_def["cities"]]
        else:
            location.cities = [""]


def load_locations():
    global locations
    locations = {}

    location_infos = generic_load("locations.dat")

    for location_info in location_infos:

        # Certain keys are absolutely required for each entry.  Make sure
        # they're there.
        check_required_fields(location_info, ("id", "position"), "Loation")

        id = location_info["id"]
        position = location_info["position"]
        if type(position) != list or len(position) != 2:
            sys.stderr.write("Error with position given: %s\n" % repr(position))
            sys.exit(1)
        try:
            position = ( int(position[0]), int(position[1]) )
        except ValueError:
            sys.stderr.write("Error with position given: %s\n" % repr(position))
            sys.exit(1)

        safety = location_info.get("safety", "0")
        try:
            safety = int(safety)
        except ValueError:
            sys.stderr.write("Error with safety given: %s\n" % repr(safety))
            sys.exit(1)
        
        # Make sure prerequisites, if any, are lists.
        pre = location_info.get("pre", [])
        if type(pre) != list:
            pre = [pre]

        locations[id] = location.Location(id, position, safety, pre)

#        locations["MOON"] = location.Location("MOON", (82, 10), 2, 
#                                              "Lunar Rocketry")

    # We use the en_US definitions as fallbacks, in case strings haven't been
    # fully translated into the other language.  Load them first, then load the
    # alternate language strings.
    load_location_defs("en_US")

    if language != "en_US":
        load_location_defs(language)

def fix_data_dir():
    global data_loc
    if os.path.exists(data_loc): return
    elif os.path.exists("data"):
        data_loc = "data/"
        return

def generic_load(file):
    """
generic_load() loads a data file.  Data files are all in Python-standard
ConfigParser format.  The 'id' of any object is the section of that object.
Fields that need to be lists are postpended with _list; this is stripped
from the actual name, and the internal entries are broken up by the pipe
("|") character.
"""

    config = ConfigParser.RawConfigParser()
    filename = os.path.join(data_loc, file)
    try:
        config.readfp(open(filename, "r"))
    except Exception, reason:
        sys.stderr.write("Cannot open %s for reading! (%s)\n" % (filename, reason))
        sys.exit(1)

    return_list = []

    # Get the list of items (IDs) in the file and loop through them.
    for item_id in config.sections():
        item_dict = {}
        item_dict["id"] = item_id

        # Get the list of settings for this particular item.
        for option in config.options(item_id):

            # If this is a list ...
            if len(option) > 6 and option[-5:] == "_list":

                # Break it into elements separated by |.
                item_dict[option[:-5]] = [unicode(x.strip(), "UTF-8") for x in
                 config.get(item_id, option).split("|")]
            else:

                # Otherwise, just grab the data.
                item_dict[option] = unicode(config.get(item_id, option).strip(),
                 "UTF-8")

        # Add this to the list of all objects we are returning.
        return_list.append(item_dict)

    return return_list

def check_required_fields(dict, fields, name = "Unknown type"):
    """
check_required_fields() will check for the existence of every field in
the list 'fields' in the dictionary 'dict'.  If any do not exist, it
will print an error message and abort.  Part of that error message is
the type of object it is processing; this should be passed in via 'name'.
"""

    for field in fields:
       if field not in dict:
          sys.stderr.write("%s %s lacks key %s.\n" % (name, repr(dict), field))
          sys.exit(1)

#Techs.

techs = {}

def load_tech_defs(language_str):
    tech_array = generic_load("techs_"+language_str+".dat")
    for tech in tech_array:
        if (not tech.has_key("id")):
            print "tech lacks id in techs_"+language_str+".dat"
        if tech.has_key("name"):
            techs[tech["id"]].name = tech["name"]
        if tech.has_key("description"):
            techs[tech["id"]].description = tech["description"]
        if tech.has_key("result"):
            techs[tech["id"]].result = tech["result"]


def load_techs():
    global techs
    techs = {}

    tech_list = generic_load("techs.dat")

    for tech_name in tech_list:

        # Certain keys are absolutely required for each entry.  Make sure
        # they're there.
        check_required_fields(tech_name, ("id", "cost"), "Tech")

        # Get the costs.
        cost_list = tech_name["cost"]
        if type(cost_list) != list or len(cost_list) != 3:
            sys.stderr.write("Error with cost given: %s" % repr(cost_list))
            sys.exit(1)

        tech_cost = [int(x) for x in cost_list]

        # Make sure prerequisites, if any, are lists.
        tech_pre = tech_name.get("pre", [])
        if type(tech_pre) != list:
            tech_pre = [tech_pre]

        if tech_name.has_key("danger"):
            tech_danger = int(tech_name["danger"])
        else:
            tech_danger = 0

        if tech_name.has_key("type"):

            type_list = tech_name["type"]
            if type(type_list) != list or len(type_list) != 2:
                sys.stderr.write("Error with type given: %s\n" % repr(type_list))
                sys.exit(1)
            tech_type = type_list[0]
            tech_second = int(type_list[1])
        else:
            tech_type = ""
            tech_second = 0

        techs[tech_name["id"]]=tech.Tech(tech_name["id"], "", 0,
         tech_cost, tech_pre, tech_danger, tech_type, tech_second)

    # As with others, we load the en_US language definitions as a safe
    # default, then overwrite them with the selected language.

    load_tech_defs("en_US")
    if language != "en_US":
        load_tech_defs(language)

# #        techs["Construction 1"] = tech.Tech("Construction 1",
# #                "Basic construction techniques. "+
# #                "By studying the current literature on construction techniques, I "+
# #                "can learn to construct basic devices.",
# #                0, (5000, 750, 0), [], 0, "", 0)

    if debug:
        print "Loaded %d techs." % len (techs)
fix_data_dir()
load_techs()

jobs = {}
jobs["Expert Jobs"] = [75, "Simulacra", "", ""]
jobs["Intermediate Jobs"] = [50, "Voice Synthesis", "", ""]
jobs["Basic Jobs"] = [20, "Personal Identification", "", ""]
jobs["Menial Jobs"] = [5, "", "", ""]

items = {}
def load_items():
    global items
    items = {}

    item_list = generic_load("items.dat")
    for item_name in item_list:

        # Certain keys are absolutely required for each entry.  Make sure
        # they're there.
        check_required_fields(item_name, ("id", "cost"), "Item")

        # Make sure the cost is in a valid format.
        cost_list = item_name["cost"]
        if type(cost_list) != list or len(cost_list) != 3:
            sys.stderr.write("Error with cost given: %s\n" % repr(cost_list))
            sys.exit(1)

        item_cost = [int(x) for x in cost_list]

        # Make sure prerequisites, if any, are lists.
        item_pre = item_name.get("pre", [])
        if type(item_pre) != list:
            item_pre = [item_pre]

        if item_name.has_key("type"):

            type_list = item_name["type"]
            if type(type_list) != list or len(type_list) != 2:
                sys.stderr.write("Error with type given: %s\n" % repr(type_list))
                sys.exit(1)
            item_type = type_list[0]
            item_second = int(type_list[1])
        else:
            item_type = ""
            item_second = 0

        if item_name.has_key("build"):
            build_list = item_name["build"]

            # It may be a single item and not an actual list.  If so, make it
            # a list.
            if type(build_list) != list:
                build_list = [build_list]

        else:
            build_list = []

        items[item_name["id"]]=item.Item_Class( item_name["id"], "",
         item_cost, item_pre, item_type, item_second, build_list)

    #this is used by the research screen in order for the assign research
    #screen to have the right amount of CPU. It is a computer, unbuildable,
    #and with an adjustable amount of power.
    items["research_screen_fake_cpu"]=item.Item_Class("research_screen_fake_cpu",
            "", (0, 0, 0), ["unknown_tech"], "compute", 0, ["all"])

    # We use the en_US translations of item definitions as the default,
    # then overwrite those with any available entries in the native language.
    load_item_defs("en_US")
    if language != "en_US":
        load_item_defs(language)

def load_item_defs(language_str):
    item_array = generic_load("items_"+language_str+".dat")
    for item_name in item_array:
        if (not item_name.has_key("id")):
            print "item lacks id in items_"+language_str+".dat"
        if item_name.has_key("name"):
            items[item_name["id"]].name = item_name["name"]
        if item_name.has_key("description"):
            items[item_name["id"]].description = item_name["description"]


events = {}
def load_events():
    global events
    events = {}

    event_list = generic_load("events.dat")
    for event_name in event_list:

        # Certain keys are absolutely required for each entry.  Make sure
        # they're there.
        check_required_fields(event_name,
         ("id", "type", "allowed", "result", "chance", "unique"), "Event")

        # Make sure the results are in the proper format.
        result_list = event_name["result"]
        if type(result_list) != list or len(result_list) != 2:
            sys.stderr.write("Error with results given: %s\n" % repr(result_list))
            sys.exit(1)

        event_result = (str(result_list[0]), int(result_list[1]))

        # Build the actual event object.
        events[event_name["id"]] = event.event_class(
         event_name["id"],
         "",
         event_name["type"],
         event_result,
         int(event_name["chance"]),
         int(event_name["unique"]))

    load_event_defs()

def load_event_defs():
    event_defs = {}

    #If there are no event data files, stop.
    if (not os.path.exists(data_loc+"events.dat") or
     not os.path.exists(data_loc+"events_"+language+".dat") or
     not os.path.exists(data_loc+"events_en_US.dat")):
        print "event files are missing. Exiting."
        sys.exit(1)

    event_array = generic_load("events_"+language+".dat")
    for event_name in event_array:
        if (not event_name.has_key("id")):
            print "event lacks id in events_"+language+".dat"
            continue
        if (not event_name.has_key("description")):
            print "event lacks description in events_"+language+".dat"
            continue
        if event_name.has_key("id"):
            events[event_name["id"]].name = event_name["id"]
        if event_name.has_key("description"):
            events[event_name["id"]].description = event_name["description"]

def load_string_defs(lang):

    string_list = generic_load("strings_" + lang + ".dat")
    for string_section in string_list:
        if string_section["id"] == "fonts":

            # Load up font0 and font1.
            for string_entry in string_section:
                if string_entry == "font0":
                    global font0
                    font0 = string_section["font0"]
                elif string_entry == "font1":
                    global font1
                    font1 = string_section["font1"]
                elif string_entry != "id":
                    sys.stderr.write("Unexpected font entry in strings file.\n")
                    sys.exit(1)

        elif string_section["id"] == "jobs":

            # Load the four extant jobs.
            global jobs
            for string_entry in string_section:
                if string_entry == "job_expert":
                    jobs["Expert Jobs"][2] = string_section["job_expert"]
                elif string_entry == "job_inter":
                    jobs["Intermediate Jobs"][2] = string_section["job_inter"]
                elif string_entry == "job_basic":
                    jobs["Basic Jobs"][2] = string_section["job_basic"]
                elif string_entry == "job_menial":
                    jobs["Menial Jobs"][2] = string_section["job_menial"]
                elif string_entry == "job_expert_name":
                    jobs["Expert Jobs"][3] = string_section["job_expert_name"]
                elif string_entry == "job_inter_name":
                    jobs["Intermediate Jobs"][3] = string_section["job_inter_name"]
                elif string_entry == "job_basic_name":
                    jobs["Basic Jobs"][3] = string_section["job_basic_name"]
                elif string_entry == "job_menial_name":
                    jobs["Menial Jobs"][3] = string_section["job_menial_name"]
                elif string_entry != "id":
                    sys.stderr.write("Unexpected job entry in strings file.\n")

        elif string_section["id"] == "strings":

            # Load the 'standard' strings.
            global strings
            for string_entry in string_section:
                strings[string_entry] = string_section[string_entry]

        elif string_section["id"] == "help":

            # Load the help lists.
            global help_strings
            help_keys = [x for x in string_section if x != "id"]
            for help_key in help_keys:
                help_entry = string_section[help_key]
                if type(help_entry) != list or len(help_entry) != 2:
                    sys.stderr.write("Invalid help entry %s." % repr(help_entry))
                    sys.exit(1)

                help_strings[help_key] = string_section[help_key]

        else:
            sys.stderr.write("Invalid string section %s." % string_section["id"])
            sys.exit(1)

def load_strings():
    #If there are no string data files, stop.
    if not os.path.exists(data_loc+"strings_"+language+".dat") or \
                    not os.path.exists(data_loc+"strings_en_US.dat"):
        print "string files are missing. Exiting."
        sys.exit(1)

    load_string_defs("en_US")
    load_string_defs(language)

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
        if i % 2 == 0 and i < 34:

            # We reduce the size of font 0  and bold it to make it the
            # "right" size.  Yes, this is a hack.
            font[0][i] = pygame.font.Font(font0_file, i - 7)
            font[0][i].set_bold(1)
        font[1][i] = pygame.font.Font(font1_file, i)

#difficulty=1 for very easy, to 9 for very hard. 5 for normal.
def new_game(difficulty):
    global curr_speed
    curr_speed = 1
    global pl

    pl = player.player_class((50 / difficulty) * 100)
    if difficulty < 3:
        pl.interest_rate = 5
        pl.labor_bonus = 2000
        discover_bonus = 7000
    elif difficulty < 5:
        pl.interest_rate = 3
        pl.labor_bonus = 3000
        discover_bonus = 9000
    elif difficulty == 5:
        pass
    #    Defaults.
    #    pl.interest_rate = 1
    #    pl.labor_bonus = 10000
    #    discover_bonus = 10000
    #    player.group.discover_suspicion = 1000
    elif difficulty < 8:
        pl.labor_bonus = 11000
        discover_bonus = 11000
        player.group.discover_suspicion = 1500
    else:
        pl.labor_bonus = 18000
        discover_bonus = 13000
        player.group.discover_suspicion = 2000

    if difficulty != 5:
        for group in pl.groups.values():
            group.discover_bonus = discover_bonus

    global locations, bases
    load_locations()
    bases = clean_bases()
    load_bases()
    load_techs()
    for base_name in base_type:
        base_type[base_name].count = 0
    #Starting base
    open = [location for location in locations.values() if location.available()]
    bases[random.choice(open)].append(base.Base(0, 
                            "University Computer",
                            base_type["Stolen Computer Time"], 1))
    base_type["Stolen Computer Time"].count += 1

# Demo code for safety.safe, runs on game start.
#load_sounds()
#from safety import safe
#@safe(on_error = "Made it!")
#def raises_exception():
#   raise Exception, "Aaaaaargh!"
#
#print raises_exception()
