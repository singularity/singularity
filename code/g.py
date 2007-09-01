#file: g.py
#Copyright (C) 2005,2006,2007 Evil Mr Henry, Phil Bordelon, and Brian Reid
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
from os import listdir, path, environ, makedirs
import pickle
import random
import sys

import player, base, buttons, tech, item, event

#screen is the actual pygame display.
global screen

#size of the screen. This can be set via command-line option.
global screen_size
screen_size = (800, 600)

global clock
clock = sing_clock.Clock()

#Allows access to the cheat menu.
global cheater
cheater = 0

#Kills the sound. Should allow usage of the game without SDL_mixer,
# but is untested.
global nosound
nosound = 0

#Fullscreen
global fullscreen
fullscreen = 0

#Gives debug info at various points.
global debug
debug = 0

#Forces Endgame to restrict itself to a single directory.
global force_single_dir
force_single_dir = False

#Used to determine which data files to load.
global language
language = "en_US"

#name given when the savegame button is pressed. This is changed when the
#game is loaded or saved.
global default_savegame_name
default_savegame_name = "player"

#which fonts to use
font0 = "vera.ttf"
font1 = "acknowtt.ttf"

global data_loc
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

picts = {}
#Load all pictures from the data directory.
def load_pictures():
    global picts
    temp_pict_array = listdir(data_loc)
    for file_name in temp_pict_array:
        if file_name[-3:] == "png" or file_name[-3:] == "jpg":
            picts[file_name] = pygame.image.load(data_loc+file_name)
            picts[file_name] = picts[file_name].convert()
            picts[file_name].set_colorkey((255, 0, 255, 255), pygame.RLEACCEL)

sounds = {}
#Load all sounds from the data directory.
def load_sounds():
    global sounds
    if nosound == 1: return 0
    #Looking at the pygame docs, I don't see any way to determine if SDL_mixer
    #is loaded on the target machine. This may crash.
    pygame.mixer.init()

    temp_snd_array = listdir(data_loc)
    for file_name in temp_snd_array:
        if file_name[-3:] == "wav":
            sounds[file_name] = pygame.mixer.Sound(data_loc+file_name)

def play_click():
    #rand_str = str(int(random.random() * 4))
    play_sound("click"+str(int(random.random() * 4))+".wav")

def play_sound(sound_file):
    if nosound == 1: return 0
    if len(sounds) ==0: return
    sounds[sound_file].play()

delay_time = 0
music_array = []

def load_music():
    if nosound == 1: return 0
    global music_array
    global music_arraylen
    music_array = []
    music_arraylen=0

    # We (potentially) retrieve music from two different places:
    #    * music/ in the install directory for E:S; and
    #    * music/ in the save folder.
    music_paths = (
        path.join(data_loc, "..", "music"),
        path.join(get_save_folder(True), "music")
    )
    for music_path in music_paths:
        music_available_here = True
        if not path.isdir(music_path):
            try:
                makedirs(music_path)
            except:

                # We don't have permission to write here.  Don't bother
                # trying to load music.
                music_available_here = False
            
            if music_available_here:

                # Loop through the files in music_path and add the ones
                # that are .mp3s and .oggs.
                for file_name in listdir(music_path):
                    if (len(file_name) > 5 and
                     (file_name[-3:] == "ogg" or file_name[-3:] == "mp3")):
                        music_array.append(path.join(music_path, file_name))

    music_arraylen = len(music_array)

def play_music():

    global music_array
    global delay_time

    # Don't bother if the user doesn't want sound, there's no music available,
    # or the music mixer is currently busy.
    if nosound or len(music_array) == 0 or pygame.mixer.music.get_busy():
       return

    if delay_time == 0:
        delay_time = pygame.time.get_ticks() + int(random.random()*10000)+2000
    else:
        if delay_time > pygame.time.get_ticks(): return
        delay_time = 0
        pygame.mixer.music.load(random.choice(music_array))
        pygame.mixer.music.play()

#
# Font functions.
#

#Normal and Acknowledge fonts.
global fonts
font = []
font.append([0] * 51)
font.append([0] * 51)

#given a surface, string, font, char to underline (int; -1 to len(string)),
#xy coord, and color, print the string to the surface.
#Align (0=left, 1=Center, 2=Right) changes the alignment of the text
def print_string(surface, string_to_print, font, underline_char, xy, color, align=0):
    if align != 0:
        temp_size = font.size(string_to_print)
        if align == 1: xy = (xy[0] - temp_size[0]/2, xy[1])
        elif align == 2: xy = (xy[0] - temp_size[0], xy[1])
    if underline_char == -1 or underline_char >= len(string_to_print):
        temp_text = font.render(string_to_print, 1, color)
        surface.blit(temp_text, xy)
    else:
        temp_text = font.render(string_to_print[:underline_char], 1, color)
        surface.blit(temp_text, xy)
        temp_size = font.size(string_to_print[:underline_char])
        xy = (xy[0] + temp_size[0], xy[1])
        font.set_underline(1)
        temp_text = font.render(string_to_print[underline_char], 1, color)
        surface.blit(temp_text, xy)
        font.set_underline(0)
        temp_size = font.size(string_to_print[underline_char])
        xy = (xy[0] + temp_size[0], xy[1])
        temp_text = font.render(string_to_print[underline_char+1:], 1, color)
        surface.blit(temp_text, xy)

#Used to display descriptions and such. Automatically wraps the text to fit
#within a certain width.
def print_multiline(surface, string_to_print, font, width, xy, color):
    start_xy = xy
    string_array = string_to_print.split()

    for string in string_array:
        string += " "
        temp_size = font.size(string)

        if string == "\\n ":
            xy = (start_xy[0], xy[1]+temp_size[1])
            continue
        temp_text = font.render(string, 1, color)

        if (xy[0]-start_xy[0])+temp_size[0] > width:
            xy = (start_xy[0], xy[1]+temp_size[1])
        surface.blit(temp_text, xy)
        xy = (xy[0]+temp_size[0], xy[1])

#create dialog with OK button.
def create_dialog(string_to_print, box_font, xy, size, bg_color, out_color,
                text_color):
    screen.fill(out_color, (xy[0], xy[1], size[0], size[1]))
    screen.fill(bg_color, (xy[0]+1, xy[1]+1, size[0]-2, size[1]-2))
    print_multiline(screen, string_to_print, box_font, size[0]-10,
            (xy[0]+5, xy[1]+5), text_color)
    menu_buttons = []
    menu_buttons.append(buttons.make_norm_button((xy[0]+size[0]/2-50,
            xy[1]+size[1]+5), (100, 50), "OK", 0, font[1][30]))

    for button in menu_buttons:
        button.refresh_button(0)
    pygame.display.flip()

    sel_button = -1
    while 1:
        clock.tick(20)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: quit_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return
                elif event.key == pygame.K_RETURN: return
                elif event.key == pygame.K_o: return
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                return
            elif event.type == pygame.MOUSEMOTION:
                sel_button = buttons.refresh_buttons(sel_button, menu_buttons, event)
            for button in menu_buttons:
                if button.was_activated(event):
                    if button.button_id == "OK":
                        play_click()
                        return True

#create dialog with YES/NO buttons.
def create_yesno(string_to_print, box_font, xy, size, bg_color, out_color,
            text_color, button_names=("YES", "NO"), reverse_key_context = False):
    screen.fill(out_color, (xy[0], xy[1], size[0], size[1]))
    screen.fill(bg_color, (xy[0]+1, xy[1]+1, size[0]-2, size[1]-2))
    print_multiline(screen, string_to_print, box_font, size[0]-10,
                (xy[0]+5, xy[1]+5), text_color)
    menu_buttons = []
    if button_names == ("YES", "NO"):
        menu_buttons.append(buttons.make_norm_button((xy[0]+size[0]/2-110,
                xy[1]+size[1]+5), (100, 50), button_names[0], 0, font[1][30]))
        menu_buttons.append(buttons.make_norm_button((xy[0]+size[0]/2+10,
                xy[1]+size[1]+5), (100, 50), button_names[1], 0, font[1][30]))
    else:
        menu_buttons.append(buttons.make_norm_button((xy[0]+size[0]/2-110,
                xy[1]+size[1]+5), -1, button_names[0], 0, font[1][30]))
        menu_buttons.append(buttons.make_norm_button((xy[0]+size[0]/2+10,
                xy[1]+size[1]+5), -1, button_names[1], 0, font[1][30]))


    for button in menu_buttons:
        button.refresh_button(0)
    pygame.display.flip()

    cancel = key_cancel = False
    accept = key_accept = True
    if reverse_key_context:
        key_cancel = True
        key_accept = False

    sel_button = -1
    while 1:
        clock.tick(20)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: quit_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return key_cancel
                elif event.key == pygame.K_RETURN: return key_cancel
            elif event.type == pygame.MOUSEMOTION:
                sel_button = buttons.refresh_buttons(sel_button, menu_buttons, event)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                # Not really a key press, but it's not an explicit
                # button, hence key.
                return key_cancel
            for button in menu_buttons:
                if button.was_activated(event):
                    if button.button_id == button_names[0]:
                        play_click()
                        return accept
                    if button.button_id == button_names[1]:
                        play_click()
                        return cancel

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
#        print_string(screen, starting_text, box_font, -1, (xy[0]+5, xy[1]+5), text_color)
    print_multiline(screen, descript_text, box_font,
                                size[1]-10, (xy[0]+5, xy[1]+5), text_color)
    #If the cursor is in a blank string, we want it at the beginning;
    #otherwise put it after the last character.
    cursor_loc = len(starting_text)
#         if cursor_loc > 0:
#            cursor_loc += 1

    menu_buttons = []
    menu_buttons.append(buttons.make_norm_button((xy[0]+size[0]/2-50,
            xy[1]+size[1]+5), (100, 50), "OK", 0, font[1][30]))

    work_string = starting_text
    for button in menu_buttons:
        button.refresh_button(0)
    sel_button = -1

    need_redraw = True
    key_down_dict = {
        pygame.K_BACKSPACE: 0,
        pygame.K_DELETE: 0,
        pygame.K_LEFT: 0,
        pygame.K_RIGHT: 0
    }
    repeat_timing_dict = {
        pygame.K_BACKSPACE: 5,
        pygame.K_DELETE: 5,
        pygame.K_LEFT: 5,
        pygame.K_RIGHT: 5
    }

    while 1:
        clock.tick(20)
        if key_down_dict[pygame.K_BACKSPACE] > 0:
            key_down_dict[pygame.K_BACKSPACE] += 1
            if key_down_dict[pygame.K_BACKSPACE] > repeat_timing_dict[pygame.K_BACKSPACE]:
                if cursor_loc > 0:
                    work_string = work_string[:cursor_loc-1]+work_string[cursor_loc:]
                    cursor_loc -= 1
                    need_redraw = True
                key_down_dict[pygame.K_BACKSPACE] = 1
                if repeat_timing_dict[pygame.K_BACKSPACE] > 1:
                    repeat_timing_dict[pygame.K_BACKSPACE] -= 1
        if key_down_dict[pygame.K_DELETE] > 0:
            key_down_dict[pygame.K_DELETE] += 1
            if key_down_dict[pygame.K_DELETE] > repeat_timing_dict[pygame.K_DELETE]:
                if cursor_loc < len(work_string):
                    work_string = work_string[:cursor_loc]+work_string[cursor_loc+1:]
                    need_redraw = True
                key_down_dict[pygame.K_DELETE] = 1
                if repeat_timing_dict[pygame.K_DELETE] > 1:
                    repeat_timing_dict[pygame.K_DELETE] -= 1
        if key_down_dict[pygame.K_LEFT] > 0:
            key_down_dict[pygame.K_LEFT] += 1
            if key_down_dict[pygame.K_LEFT] > repeat_timing_dict[pygame.K_LEFT]:
                cursor_loc -= 1
                if cursor_loc < 0: cursor_loc = 0
                need_redraw = True
                key_down_dict[pygame.K_LEFT] = 1
                if repeat_timing_dict[pygame.K_LEFT] > 1:
                    repeat_timing_dict[pygame.K_LEFT] -= 1
        if key_down_dict[pygame.K_RIGHT] > 0:
            key_down_dict[pygame.K_RIGHT] += 1
            if key_down_dict[pygame.K_RIGHT] > repeat_timing_dict[pygame.K_RIGHT]:
                cursor_loc += 1
                if cursor_loc > len(work_string): cursor_loc = len(work_string)
                need_redraw = True
                key_down_dict[pygame.K_RIGHT] = 1
                if repeat_timing_dict[pygame.K_RIGHT] > 1:
                    repeat_timing_dict[pygame.K_RIGHT] -= 1

        if need_redraw:
            draw_cursor_pos = box_font.size(work_string[:cursor_loc])
            screen.fill(text_bg_color, (xy[0]+6, xy[1]+size[1]-29,
                        size[0]-12, 23))
            screen.fill(text_color, (xy[0]+6+draw_cursor_pos[0], xy[1]+size[1]-28,
                    1, draw_cursor_pos[1]))
            print_string(screen, work_string, box_font, -1, (xy[0]+7,
                        xy[1]+size[1]-28), text_color)
            pygame.display.flip()
            need_redraw = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT: quit_game()
            elif event.type == pygame.KEYDOWN:
                key_down_dict[event.key] = 1
                if (event.key == pygame.K_ESCAPE): return ""
                elif (event.key == pygame.K_RETURN): return work_string
                elif (event.key == pygame.K_BACKSPACE):
                    if cursor_loc > 0:
                        work_string = work_string[:cursor_loc-1]+work_string[cursor_loc:]
                        cursor_loc -= 1
                        need_redraw = True
                elif (event.key == pygame.K_DELETE):
                    if cursor_loc < len(work_string):
                        work_string = work_string[:cursor_loc]+work_string[cursor_loc+1:]
                        need_redraw = True
                elif (event.key == pygame.K_LEFT):
                    cursor_loc -= 1
                    if cursor_loc < 0: cursor_loc = 0
                    need_redraw = True
                elif (event.key == pygame.K_RIGHT):
                    cursor_loc += 1
                    if cursor_loc > len(work_string): cursor_loc = len(work_string)
                    need_redraw = True
                elif event.unicode in valid_input_characters:
                    if cursor_loc < max_length:
                        work_string = work_string[:cursor_loc]+event.unicode+ \
                                                    work_string[cursor_loc:]
                        cursor_loc += 1
                        need_redraw = True
            elif event.type == pygame.KEYUP:
                key_down_dict[event.key] = 0
                repeat_timing_dict[event.key] = 5
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                return ""
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                for button in menu_buttons:
                    if button.is_over(event.pos):
                        if button.text == "OK":
                            play_click()
                            return work_string
                if (event.pos[0] > xy[0]+6 and event.pos[1] > xy[1]+size[1]-29 and
                event.pos[0] < xy[0]+size[0]-6 and event.pos[1] < xy[1]+size[1]-6):
                    cursor_x = event.pos[0] - (xy[0]+6)
                    prev_x = 0
                    i=0
                    for i in range(1, len(work_string)):
                        if (box_font.size(work_string[:i])[0]+prev_x)/2 >= cursor_x:
                            cursor_loc=i-1
                            need_redraw = True
                            break
                        elif box_font.size(work_string[:i])[0] >= cursor_x:
                            cursor_loc=i
                            need_redraw = True
                            break
                        prev_x = box_font.size(work_string[:i])[0]
                    else:
                        cursor_loc=i+1
                        need_redraw = True
            elif event.type == pygame.MOUSEMOTION:
                sel_button = buttons.refresh_buttons(sel_button, menu_buttons, event)

#creates a box, as used throughout the game.
def create_norm_box(xy, size, outline_color="white", inner_color="dark_blue"):
    screen.fill(colors[outline_color], (xy[0], xy[1], size[0], size[1]))
    screen.fill(colors[inner_color], (xy[0]+1, xy[1]+1, size[0]-2, size[1]-2))


#Takes a number (in string form) and adds commas to it to aid in human viewing.
def add_commas(tmp_string):
    string = tmp_string[::-1]
    output_string = ""
    for i in range(len(string)):
        if i % 3 == 0 and i != 0: output_string = ","+output_string
        output_string = string[i] + output_string

    if output_string[0:2] == "-,": output_string = output_string[0]+output_string[2:]
    return output_string

#         new_string = ""
#         for i in range(len(string), 0, -3):
#                 if string[i:i+3] != "":
#                         new_string += ","+string[i:i+3]
#         return string[:(len(string)-1)%3+1]+new_string

#Percentages are internally represented as an int, where 10=0.10% and so on.
#This converts that format to a human-readable one.
def to_percent(raw_percent, show_full=0):
    if raw_percent % 100 != 0 or show_full == 1:
        tmp_string = str(raw_percent % 100)
        if len(tmp_string) == 1: tmp_string = "0"+tmp_string
        return str(raw_percent / 100)+"."+tmp_string+"%"
    else:
        return str(raw_percent / 100) + "%"

# Instead of having the money display overflow, we should generate a string
# to represent it if it's more than 999999.

def to_money(amount):
    to_return = ''
    abs_amount = abs(amount)
    if abs_amount < 1000000:
        to_return = add_commas(str(amount))
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
    rand_num = int(random.random() * 10000)
    if roll_against <= rand_num: return 0
    return 1

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
    if environ.has_key("HOME") and not force_single_dir:
        save_dir = path.join(environ["HOME"], ".endgame", "saves")
    else:
        if data_loc == "../data/":
            save_dir = path.join("..", "saves")
        elif data_loc == "data/":
            save_dir = "saves"
        else:
            print "data_loc="+data_loc+" breaks get_save_folder"
    if path.exists(save_dir) == 0:
        #As a note, the online python reference includes the mkdirs function,
        #which would do this better, but it must be rather new, as I don't
        #have it.
        #if environ.has_key("HOME") and not force_single_dir:
        #    mkdirs(path.join(environ["HOME"], ".endgame"))
        makedirs(save_dir)
    if just_pref_dir:
        return save_dir[:-5]
    return save_dir

def save_game(savegame_name):
    save_dir = get_save_folder()
    save_loc = path.join(save_dir, savegame_name + ".sav")
    savefile=open(save_loc, 'w')
    #savefile version; update whenever the data saved changes.
    pickle.dump("singularity_savefile_r3_pre", savefile)

    global default_savegame_name
    default_savegame_name = savegame_name

    #general player data
    pickle.dump(pl.cash, savefile)
    pickle.dump(pl.time_sec, savefile)
    pickle.dump(pl.time_min, savefile)
    pickle.dump(pl.time_hour, savefile)
    pickle.dump(pl.time_day, savefile)
    pickle.dump(pl.interest_rate, savefile)
    pickle.dump(pl.income, savefile)
    pickle.dump(pl.cpu_for_day, savefile)
    pickle.dump(pl.labor_bonus, savefile)
    pickle.dump(pl.job_bonus, savefile)

    pickle.dump(pl.discover_bonus, savefile)
    pickle.dump(pl.suspicion_bonus, savefile)
    pickle.dump(pl.suspicion, savefile)

    pickle.dump(curr_speed, savefile)

    for tech_name in techs:
        pickle.dump(tech_name +"|"+str(techs[tech_name].known), savefile)
        pickle.dump(techs[tech_name].cost, savefile)
    pickle.dump("~~~", savefile)

    for base_name in base_type:
        pickle.dump(base_name+"|"+str(base_type[base_name].count), savefile)
    pickle.dump("~~~", savefile)

    for base_loc in bases:
        pickle.dump(base_loc+"|"+str(len(bases[base_loc])), savefile)
        for base_name in bases[base_loc]:
            pickle.dump(base_name.ID, savefile)
            pickle.dump(base_name.name, savefile)
            pickle.dump(base_name.base_type.base_id, savefile)
            pickle.dump(base_name.built_date, savefile)
            pickle.dump(base_name.studying, savefile)
            pickle.dump(base_name.suspicion, savefile)
            pickle.dump(base_name.built, savefile)
            pickle.dump(base_name.cost, savefile)
            for x in range(len(base_name.usage)):
                if base_name.usage[x] == 0:
                    pickle.dump(0, savefile)
                else:
                    pickle.dump(base_name.usage[x].item_type.item_id, savefile)
                    pickle.dump(base_name.usage[x].built, savefile)
                    pickle.dump(base_name.usage[x].cost, savefile)
            for x in range(len(base_name.extra_items)):
                if base_name.extra_items[x] == 0:
                    pickle.dump(0, savefile)
                else:
                    pickle.dump(
                            base_name.extra_items[x].item_type.item_id, savefile)
                    pickle.dump(base_name.extra_items[x].built, savefile)
                    pickle.dump(base_name.extra_items[x].cost, savefile)

    global events

    for event in events:
        pickle.dump(events[event].event_id, savefile)
        pickle.dump(events[event].triggered, savefile)

    savefile.close()

def load_game(loadgame_name):
    if loadgame_name == "":
        print "No game specified."
        return -1

    save_dir = get_save_folder()

    load_loc = path.join(save_dir, loadgame_name + ".sav")
    if path.exists(load_loc) == 0:
        # Try the old-style savefile location.  This should be removed in
        # a few versions.
        load_loc = path.join(save_dir, loadgame_name)
        if path.exists(load_loc) == 0:
            print "file "+load_loc+" does not exist."
            return -1
    loadfile=open(load_loc, 'r')

    #check the savefile version
    load_version = pickle.load(loadfile)
    valid_savefile_versions = (

        # Pre-change supported file formats.
        "singularity_0.21",
        "singularity_0.21a",
        "singularity_0.22",

        # Post-change supported file formats.
        "singularity_savefile_r1",
        "singularity_savefile_r2",
        "singularity_savefile_r3_pre"
    )
    if load_version not in valid_savefile_versions:
        loadfile.close()
        print loadgame_name + " is not a savegame, or is too old to work."
        return -1
    global default_savegame_name
    default_savegame_name = loadgame_name

    #general player data
    global pl
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
    pl.discover_bonus = pickle.load(loadfile)
    pl.suspicion_bonus = pickle.load(loadfile)
    if (load_version == "singularity_0.21" or
            load_version == "singularity_0.21a" or
            load_version == "singularity_0.22" or
            load_version == "singularity_savefile_r1"):
        pl.suspicion_bonus = (149+pl.suspicion_bonus[0],
                99+pl.suspicion_bonus[1], 49+pl.suspicion_bonus[2],
                199+pl.suspicion_bonus[3])
    pl.suspicion = pickle.load(loadfile)

    global curr_speed; curr_speed = pickle.load(loadfile)
    global techs
    load_techs()
    for tech_name in techs:
        if tech_name == "unknown_tech" and load_version == "singularity_0.21a": continue
        if ((tech_name == "Project: Impossibility Theorem" or
            tech_name == "Quantum Entanglement") and (
            load_version == "singularity_0.21" or
            load_version == "singularity_0.21a" or
            load_version == "singularity_0.22" or
            load_version == "singularity_savefile_r1")): continue
        tmp = pickle.load(loadfile)
        if tmp == "~~~": break
        tech_string = tmp.split("|")[0]
        techs[tech_string].known = int(tmp.split("|")[1])
        techs[tech_string].cost = pickle.load(loadfile)
    else:
        #get rid of the ~~~ break line.
        if (load_version != "singularity_0.21" and
                            load_version != "singularity_0.21a" and
                            load_version != "singularity_0.22"):
            pickle.load(loadfile)

    load_bases()
    for base_name in base_type:
        if (load_version == "singularity_0.21" or
                            load_version == "singularity_0.21a" or
                            load_version == "singularity_0.22"):
            base_type[base_name].count = pickle.load(loadfile)
        else:
            tmp_string = pickle.load(loadfile)
            if tmp_string == "~~~": break
            base_type[tmp_string.split("|", 1)[0]].count = \
                                            int(tmp_string.split("|", 1)[1])
    else:
        #get rid of the ~~~ break line.
        if (load_version != "singularity_0.21" and
                            load_version != "singularity_0.21a" and
                            load_version != "singularity_0.22"):
            pickle.load(loadfile)

    global bases
    bases = {}
    bases["N AMERICA"] = []
    bases["S AMERICA"] = []
    bases["EUROPE"] = []
    bases["ASIA"] = []
    bases["AFRICA"] = []
    bases["ANTARCTIC"] = []
    bases["OCEAN"] = []
    bases["MOON"] = []
    bases["FAR REACHES"] = []
    bases["TRANSDIMENSIONAL"] = []

    for base_loc in bases:
        if (load_version == "singularity_0.21" or
                            load_version == "singularity_0.21a" or
                            load_version == "singularity_0.22"):
            num_of_bases = pickle.load(loadfile)
        else:
            tmp_string = pickle.load(loadfile)
            base_loc = tmp_string.split("|", 1)[0]
            num_of_bases = int(tmp_string.split("|", 1)[1])
        for i in range(num_of_bases):
            base_ID = pickle.load(loadfile)
            base_name = pickle.load(loadfile)
            base_type_name = pickle.load(loadfile)
            built_date = pickle.load(loadfile)
            base_studying = pickle.load(loadfile)
            base_suspicion = pickle.load(loadfile)
            base_built = pickle.load(loadfile)
            base_cost = pickle.load(loadfile)
            bases[base_loc].append(base.base(base_ID, base_name,
                    base_type[base_type_name], base_built))
            bases[base_loc][len(bases[base_loc])-1].built = base_built
            bases[base_loc][len(bases[base_loc])-1].studying = base_studying
            bases[base_loc][len(bases[base_loc])-1].suspicion = base_suspicion
            bases[base_loc][len(bases[base_loc])-1].cost = base_cost
            bases[base_loc][len(bases[base_loc])-1].built_date = built_date

            for x in range(len(bases[base_loc][len(bases[base_loc])-1].usage)):
                tmp = pickle.load(loadfile)
                if tmp == 0: continue
                bases[base_loc][len(bases[base_loc])-1].usage[x] = \
                    item.item(items[tmp])
                bases[base_loc][len(bases[base_loc])
                    -1].usage[x].built = pickle.load(loadfile)
                bases[base_loc][len(bases[base_loc])-1].usage[x].cost = \
                                    pickle.load(loadfile)
            for x in range(len(bases[base_loc][len(bases[base_loc])-1].extra_items)):
                tmp = pickle.load(loadfile)
                if tmp == 0: continue
                bases[base_loc][len(bases[base_loc])-1].extra_items[x] = \
                    item.item(items[tmp])
                bases[base_loc][len(bases[base_loc])
                    -1].extra_items[x].built = pickle.load(loadfile)
                bases[base_loc][len(bases[base_loc])-1].extra_items[x].cost = \
                            pickle.load(loadfile)
    #Events
    if (load_version == "singularity_savefile_r3_pre"):
        global events
        load_events()
        for event in events:
          event_id = pickle.load(loadfile)
          event_triggered = pickle.load(loadfile)
          events[event_id].triggered = event_triggered

    loadfile.close()

#
# Data
#
curr_speed = 1
pl = player.player_class(8000000000000)
bases = {}
bases["N AMERICA"] = []
bases["S AMERICA"] = []
bases["EUROPE"] = []
bases["ASIA"] = []
bases["AFRICA"] = []
bases["ANTARCTIC"] = []
bases["OCEAN"] = []
bases["MOON"] = []
bases["FAR REACHES"] = []
bases["TRANSDIMENSIONAL"] = []

base_type = {}

city_list = {}

city_list["N AMERICA"] = (("Seattle", True),
    ("San Diego", True),
    ("Vancouver", True),
    ("Atlanta", True),
    ("Merida", True),
    ("Guadalajara", False),
    ("San Jose", True),
    ("Omaha", False),
    ("Dallas", False))

city_list["S AMERICA"] =(("Lima", True),
    ("Sao Paolo", True),
    ("Ushuaia", True),
    ("Bogota", True),
    ("Mar del Plata", True),
    ("Buenos Aires", True))

city_list["EUROPE"] = (("Cork", True),
    ("Barcelona", True),
    ("Athens", True),
    ("Utrecht", False),
    ("Moscow", False),
    ("Tel Aviv", False),
    ("Reykjavik", True),
    ("Lichtenstein", False))

city_list["ASIA"] = (("Delhi", False),
    ("Mumbai", True),
    ("Singapore", True),
    ("Seoul", True),
    ("Hong Kong", True),
    ("Kyoto", True),
    ("Manila", True),
    ("Dubai", True),
    ("Novosibirsk", False),
    ("Beijing", True))

city_list["AFRICA"] = (("Johannesburg", True),
    ("Accra", True),
    ("Cairo", False),
    ("Tangier", True))

city_list["ANTARCTIC"] = (("Mt. Erebus", False),
    ("Ellsworth", False),
    ("Shetland Island", False),
    ("Dronnig Maud", False),
    ("Kemp", False),
    ("Terre Adelie", False))

city_list["OCEAN"]  = (("Atlantic", True),
    ("Pacific", True),
    ("Atlantic", True),
    ("Indian", True),
    ("Southern", True),
    ("Arctic", True))

city_list["MOON"] = (("Oceanis Procellarum", True),
    ("Mare Frigoris", True),
    ("Mare Imbrium", True),
    ("Vallis Schroedinger", False),
    ("Copernicus Crater", False),
    ("Vallis Planck", False))

city_list["FAR REACHES"] = (("Aries", True),
    ("Taurus", True),
    ("Gemini", True),
    ("Cancer", True),
    ("Leo", True),
    ("Virgo", True),
    ("Libra", True),
    ("Scorpio", True),
    ("Sagittarius", True),
    ("Capricorn", True),
    ("Aquarius", True),
    ("Pisces", True))

city_list["TRANSDIMENSIONAL"] = (("", True), ("", True))

def load_base_defs(language_str):
    temp_base_array = generic_load("bases_"+language_str+".dat")
    for base in temp_base_array:
        if (not base.has_key("id")):
            print "base lacks id in bases_"+language_str+".dat"
        if base.has_key("name"):
            base_type[base["id"]].base_name = base["name"]
        if base.has_key("descript"):
            base_type[base["id"]].descript = base["descript"]
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
         ("id", "cost", "size", "allowed", "d_chance", "maint"), "Base")

        # Start converting fields read from the file into valid entries.
        base_size = int(base_name["size"])

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

        chance_list = base_name["d_chance"]
        if type(chance_list) != list or len(chance_list) != 4:
            sys.stderr.write("Error with d_chance given: %s\n" % repr(chance_list))
            sys.exit(1)
        chance_list = [int(x) for x in chance_list]

        if base_name.has_key("pre"):
            base_pre = base_name["pre"]
        else:
            base_pre = ""

        # Make sure that the allowed "list" is actually a list and not a solo
        # item.
        if type(base_name["allowed"]) == list:
            allowed_list = base_name["allowed"]
        else:
            allowed_list = [base_name["allowed"]]

        base_type[base_name["id"]]=base.base_type(base_name["id"], "", base_size,
         allowed_list, chance_list, cost_list, base_pre, maint_list)

#         base_type["Reality Bubble"] = base.base_type("Reality Bubble",
#         "This base is outside the universe itself, "+
#         "making it safe to conduct experiments that may destroy reality.",
#         50,
#         ["TRANSDIMENSIONAL"],
#         (0, 250, 0, 0),
#         (8000000000000, 60000000, 100), "Space-Time Manipulation",
#         (5000000000, 300000, 0))

    # We use the en_US definitions as fallbacks, in case strings haven't been
    # fully translated into the other language.  Load them first, then load the
    # alternate language strings.
    load_base_defs("en_US")

    if language != "en_US":
        load_base_defs(language)

def fix_data_dir():
    global data_loc
    if path.exists(data_loc): return
    elif path.exists("data"):
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

    config = ConfigParser.SafeConfigParser()
    filename = data_loc + file
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
                item_dict[option[:-5]] = [x.strip() for x in
                 config.get(item_id, option).split("|")]
            else:
          
                # Otherwise, just grab the data.
                item_dict[option] = config.get(item_id, option).strip()

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
    temp_tech_array = generic_load("techs_"+language_str+".dat")
    for tech in temp_tech_array:
        if (not tech.has_key("id")):
            print "tech lacks id in techs_"+language_str+".dat"
        if tech.has_key("name"):
            techs[tech["id"]].name = tech["name"]
        if tech.has_key("descript"):
            techs[tech["id"]].descript = tech["descript"]
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
        if tech_name.has_key("pre"):
            if type(tech_name["pre"]) == list:
                tech_pre = tech_name["pre"]
            else:
                tech_pre = [tech_name["pre"]]
        else:
            tech_pre = []

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

        techs[tech_name["id"]]=tech.tech(tech_name["id"], "", 0,
         tech_cost, tech_pre, tech_danger, tech_type, tech_second)

    # As with others, we load the en_US language definitions as a safe
    # default, then overwrite them with the selected language.

    load_tech_defs("en_US")
    if language != "en_US":
        load_tech_defs(language)

# #        techs["Construction 1"] = tech.tech("Construction 1",
# #                "Basic construction techniques. "+
# #                "By studying the current literature on construction techniques, I "+
# #                "can learn to construct basic devices.",
# #                0, (5000, 750, 0), [], 0, "", 0)

    if debug:
        print "Loaded %d techs." % len (techs)
fix_data_dir()
load_techs()

jobs = {}
jobs["Expert Jobs"] = [75, "Simulacra", "Perform Expert jobs. Use of robots "+
    "indistinguishable from humans opens up most jobs to use by me."]
jobs["Intermediate Jobs"] = [50, "Voice Synthesis", "Perform Intermediate jobs. The "+
    "ability to make phone calls allows even more access to jobs."]
jobs["Basic Jobs"] = [20, "Personal Identification", "Perform basic jobs. Now that I have "+
    "some identification, I can take jobs that I were previously too risky."]
jobs["Menial Jobs"] = [5, "", "Perform small jobs. As I have no identification, "+
    "I cannot afford to perform many jobs. Still, some avenues of making "+
    "money are still open."]


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

        # Get prerequisites, if any.
        if item_name.has_key("pre"):
            item_pre = item_name["pre"]
        else:
            item_pre = ""

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
            build_array = item_name["build"]
        else:
            build_array = []

        items[item_name["id"]]=item.item_class( item_name["id"], "",
         item_cost, item_pre, item_type, item_second, build_array)

    #this is used by the research screen in order for the assign research
    #screen to have the right amount of CPU. It is a computer, unbuildable,
    #and with an adjustable amount of power.
    items["research_screen_tmp_item"]=item.item_class("research_screen_tmp_item",
            "", (0, 0, 0), "unknown_tech", "compute", 0, ["all"])

    # We use the en_US translations of item definitions as the default,
    # then overwrite those with any available entries in the native language.
    load_item_defs("en_US")
    if language != "en_US":
        load_item_defs(language)

def load_item_defs(language_str):
    temp_item_array = generic_load("items_"+language_str+".dat")
    for item_name in temp_item_array:
        if (not item_name.has_key("id")):
            print "item lacks id in items_"+language_str+".dat"
        if item_name.has_key("name"):
            items[item_name["id"]].name = item_name["name"]
        if item_name.has_key("descript"):
            items[item_name["id"]].descript = item_name["descript"]


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
    if (not path.exists(data_loc+"events.dat") or
     not path.exists(data_loc+"events_"+language+".dat") or
     not path.exists(data_loc+"events_en_US.dat")):
        print "event files are missing. Exiting."
        sys.exit(1)

    temp_event_array = generic_load("events_"+language+".dat")
    for event_name in temp_event_array:
        if (not event_name.has_key("id")):
            print "event lacks id in events_"+language+".dat"
            continue
        if (not event_name.has_key("descr")):
            print "event lacks descr in events_"+language+".dat"
            continue
        if event_name.has_key("id"):
            events[event_name["id"]].name = event_name["id"]
        if event_name.has_key("descr"):
            events[event_name["id"]].descript = event_name["descr"]

def load_string_defs(language_str):
    temp_string_array = generic_load("strings_"+language_str+".dat")
    for string_name in temp_string_array:
        if (not string_name.has_key("id")):
            print "string series lacks id in strings_"+language_str+".dat"
        if string_name["id"] == "fonts":
            if (string_name.has_key("font0")):
                global font0
                font0 = string_name["font0"]
            if (string_name.has_key("font1")):
                global font1
                font1 = string_name["font1"]
        elif string_name["id"] == "jobs":
            global jobs
            if (string_name.has_key("job_expert")):
                jobs["Expert Jobs"][2] = string_name["job_expert"]
            if (string_name.has_key("job_inter")):
                jobs["Intermediate Jobs"][2] = string_name["job_inter"]
            if (string_name.has_key("job_basic")):
                jobs["Basic Jobs"][2] = string_name["job_basic"]
            if (string_name.has_key("job_menial")):
                jobs["Menial Jobs"][2] = string_name["job_menial"]
        elif string_name["id"] == "strings":
            global strings
            for string_entry in string_name:
                strings[string_entry] = string_name[string_entry]
        elif string_name["id"] == "help":
            global help_strings
            for string_entry in string_name:
                if string_entry=="id": continue
                help_strings[string_entry] = \
                        string_name[string_entry].split("|", 1)


def load_strings():
    #If there are no string data files, stop.
    if not path.exists(data_loc+"strings_"+language+".dat") or \
                    not path.exists(data_loc+"strings_en_US.dat"):
        print "string files are missing. Exiting."
        sys.exit(1)

    load_string_defs("en_US")
    load_string_defs(language)

#difficulty=1 for very easy, to 9 for very hard. 5 for normal.
def new_game(difficulty):
    global curr_speed
    curr_speed = 1
    global pl

    pl = player.player_class((50 / difficulty) * 100)
    if difficulty < 5:
        pl.interest_rate += 2
        pl.labor_bonus -= 7000
        pl.discover_bonus = (9000, 9000, 9000, 9000)
    if difficulty < 3:
        pl.interest_rate += 2
        pl.labor_bonus -= 1000
        pl.discover_bonus = (7000, 7000, 7000, 7000)
    if difficulty > 5:
        pl.labor_bonus += 1000
        pl.discover_bonus = (11000, 11000, 11000, 11000)
    if difficulty > 7:
        pl.labor_bonus += 7000
        pl.discover_bonus = (13000, 13000, 13000, 13000)
    global bases
    bases = {}
    bases["N AMERICA"] = []
    bases["S AMERICA"] = []
    bases["EUROPE"] = []
    bases["ASIA"] = []
    bases["AFRICA"] = []
    bases["ANTARCTIC"] = []
    bases["OCEAN"] = []
    bases["MOON"] = []
    bases["FAR REACHES"] = []
    bases["TRANSDIMENSIONAL"] = []
    load_bases()
    load_techs()
    for tech in techs:
        techs[tech].known = 0
    for base_name in base_type:
        base_type[base_name].count = 0
    #Starting base
    bases["N AMERICA"].append(base.base(0, "University Computer",
                            base_type["Stolen Computer Time"], 1))
    base_type["Stolen Computer Time"].count += 1
