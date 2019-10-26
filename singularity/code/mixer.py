#file: code/mixer.py
#Copyright (C) 2005 Evil Mr Henry, Phil Bordelon, Brian Reid, FunnyMan3595,
#                   MestreLion
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
#along with this program.  If not, see <http://www.gnu.org/licenses/>.
#A full copy of this license is provided in GPL.txt

#This file contains sound and musics function.

from __future__ import absolute_import

import os
import sys
import random
import pygame

from singularity.code import g, dirs

sounds = {}
music_class = None  # currently playing music "class" (ie, dir)
music_dict = {}

#Disables sound playback (and, currently, music too)
nosound = False

#Indicates if mixer is initialized
#Unlike nosound, which user may change at any time via options screen,
#this deals with hardware capability and mixer initialization status
#In a nutshell: nosound is what user /wants/, mixerinit is what user /has/
init = False

soundbuf = 1024*2
soundargs = (48000, -16, 2)  # sampling frequency, size, channels
soundvolumes = {"gui": 1.0, "music": 1.0}

def preinit(desired_soundbuf):
    pygame.mixer.pre_init(*soundargs, buffer=desired_soundbuf)
    
    global soundbuf
    soundbuf = desired_soundbuf
    
def update():
    global init
    init = bool(pygame.mixer.get_init())

    if (init):
        pygame.mixer.music.set_volume(soundvolumes["music"])

def reinit():
    global init

    if nosound:
        return

    try:
        pygame.mixer.quit()
        pygame.mixer.init(*soundargs, buffer=soundbuf)
    except Exception as reason:
        sys.stderr.write("Failure starting sound system. Disabling. (%s)\n" % reason)
    finally:
        init = bool(pygame.mixer.get_init())

def load_sounds():
    """ 
        load_sounds() loads all of the sounds in the data/sounds/ directory 
    """
    global sounds
    sounds = {}

    if not init:
        # Sound is not initialized. Warn if user wanted sound
        if not nosound:
            sys.stderr.write("WARNING: Sound is requested, but mixer is not initialized!\n")
        return

    # Build the set of paths we'll check for sounds.
    sounds_paths = dirs.get_read_dirs("sounds")

    # Main loop for sounds_paths
    for sounds_path in sounds_paths:
        if not os.path.isdir(sounds_path): continue

        # Loop through the files in sounds_path and add them
        for entry in os.walk(sounds_path):
            root  = entry[0]
            files = entry[2]
            (head, tail) = os.path.split(root)
            
            # Avoid hidden file
            if tail.startswith("."): continue
                
            for file_name in files:
                # Only wav file supported now.
                if (len(file_name) < 6 or file_name[-3:] != "wav"): continue
                    
                real_file = os.path.join(head, tail, file_name)
                sound_class = tail
                    
                # Load it via the mixer ...
                sound = pygame.mixer.Sound(real_file)

                # And shove it into the sounds dictionary.
                if sound_class not in sounds:
                    sounds[sound_class] = []
                    
                sounds[sound_class].append({
                    "filename": real_file,
                    "sound": sound})
                    
                if g.debug:
                    sys.stderr.write("DEBUG: Loaded soundfile: %s\n" %real_file)

def play_sound(sound_class, sound_volume="gui"):
    """
play_sound() plays a sound from a particular class and volume.
"""

    if nosound or not init:
        return

    # Don't crash if someone requests the wrong sound class, but print a
    # warning.
    if sound_class not in sounds:
        sys.stderr.write("WARNING: Requesting a sound of unavailable class: %s\n" %
                         sound_class)
        return

    # Play a random choice of sounds from the sound class.
    random_sound = random.choice(sounds[sound_class])
    if g.debug:
        sys.stderr.write("DEBUG: Playing sound %s.\n" % random_sound["filename"])

    random_sound["sound"].set_volume(soundvolumes[sound_volume])
    random_sound["sound"].play()

def load_music():
    """
load_music() loads music for the game.  It looks in multiple locations:

* music/ in the install directory for E:S.
* music/ in user's XDG_DATA_HOME/singularity folder.
"""

    global music_dict
    music_dict = {}

    # Build the set of paths we'll check for music.
    music_paths = dirs.get_read_dirs("music")

    # Main loop for music_paths
    for music_path in music_paths:
        if os.path.isdir(music_path):

            # Loop through the files in music_path and add the ones
            # that are .mp3s and .oggs.
            for entry in os.walk(music_path):
                root  = entry[0]
                files = entry[2]
                (head, tail) = os.path.split(root)
                if (tail.lower() != ".svn"):
                    if tail not in music_dict:
                        music_dict[tail]=[]
                    for file_name in files:
                        if (len(file_name) > 5 and
                        (file_name[-3:] == "ogg" or file_name[-3:] == "mp3")):
                            music_dict[tail].append(os.path.join(head, tail, file_name))
                            if g.debug:
                                sys.stderr.write("D: Loaded musicfile %s\n"
                                        % music_dict[tail][-1])

def play_music(musicdir=None):

    global delay_time
    global music_class

    if musicdir:
        music_class = musicdir
        delay_time = 0  # unset delay to force music switch
    else:
        musicdir = music_class

    # Don't bother if the user doesn't want or have sound,
    # there's no music available at all or for that musicdir,
    # or the delay has not yet expired
    if (nosound
        or not init
        or not music_dict.get(musicdir)
        or delay_time > pygame.time.get_ticks()):
        return

    # If music mixer is currently busy and switch was not forced, renew delay
    if pygame.mixer.music.get_busy() and delay_time:
        delay_time = pygame.time.get_ticks() + int(random.random()*10000)+2000
        return

    pygame.mixer.music.stop()
    pygame.mixer.music.load(random.choice(music_dict[musicdir]))
    pygame.mixer.music.play()
    delay_time = 1  # set a (dummy) delay

def set_volume(type, value):
    # Chomp volume to the 0-100 range.  
    # Just to avoid blasting peoples ears out if something goes wrong.
    # pygame already disallows bad value but just in case...
    value = min(max(value, 0), 100)
    
    soundvolumes[type] = value / float(100)
    
    if init and type == "music":
        pygame.mixer.music.set_volume(soundvolumes["music"])

def get_volume(type):
    return int(soundvolumes[type] * 100)

def itervolumes():
    for name in soundvolumes:
        yield name

def set_sound(value):
    global nosound
    if nosound == (not value):
        # No transition requested, bail out
        return

    nosound = not value
    if init:
        if nosound:
            pygame.mixer.music.stop()
        else:
            play_sound("click")
            play_music(music_class)  # force music switch at same dir

def set_soundbuf(value):
    global soundbuf
    old_soundbuf = soundbuf
    soundbuf = value

    if init and soundbuf != old_soundbuf:
        reinit()

def get_soundbuf():
    return int(soundbuf)
