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

version = "0.30c"

import ConfigParser
import pygame
import os.path
import cPickle
import random
import sys

# Use locale to add commas and decimal points, so that appropriate substitutions
# are made where needed.
import locale

import player, base, tech, item, event, location, buyable, statistics
import graphics.g

stats = statistics.Statistics()

# Useful constants.
hours_per_day = 24
minutes_per_hour = 60
minutes_per_day = 24 * 60
seconds_per_minute = 60
seconds_per_hour = 60 * 60
seconds_per_day = 24 * 60 * 60

#Allows access to the cheat menu.
cheater = 0

#Kills the sound. Should allow usage of the game without SDL_mixer
nosound = 0

# Enables day/night display.
daynight = True

#Gives debug info at various points.
debug = 0

#Forces Endgame to restrict itself to a single directory.
force_single_dir = False

#Used to determine which data files to load.
default_language = "en_US"
try:    language = locale.getdefaultlocale()[0] or default_language
except: language = default_language

#Makes the intro be shown on the first GUI tick.
intro_shown = True

#name given when the savegame button is pressed. This is changed when the
#game is loaded or saved.
default_savegame_name = "Default Save"

#which fonts to use
font0 = "DejaVuSans.ttf"
font1 = "acknowtt.ttf"

#savefile version; update whenever the data saved changes.
current_save_version = "singularity_savefile_r5_pre"
savefile_translation = {
    "singularity_savefile_r4": 4,
    "singularity_savefile_r5_pre": 4.91,
}

data_loc = "data/"

# Initialization data
strings = {}
locations = {}
techs = {}
events = {}
items = {}
base_type = {}
buttons = {}
help_strings = {}
sounds = {}
music_dict = {}
delay_time = 1
curr_speed = 1
soundbuf = 1024*2
danger_colors = ((0, 0, 255), (85, 0, 170), (170, 0, 85), (255, 0, 0))
detect_string_names = ("detect_str_low",
                       "detect_str_moderate",
                       "detect_str_high",
                       "detect_str_critical")

jobs = {"Expert Jobs"       : [75, "Simulacra", "", ""],
        "Intermediate Jobs" : [50, "Voice Synthesis", "", ""],
        "Basic Jobs"        : [20, "Personal Identification", "", ""],
        "Menial Jobs"       : [5 , "", "", ""],
       }

pl = player.Player()
map_screen = None

def set_language(lang=None):
    global language # required, since we're going to change it
    if lang is None: lang = language

    langs = available_languages()
    if lang in langs:
        language = lang
    else:
        # Let's try to be smart: if base language exists for another for another
        # country, use it. So es_ES => es_AR, pt_PT => pt_BR, etc
        code = lang.split("_")[0]
        languages = [ l for l in langs if code == l.split("_")[0] ]
        if len(languages) > 0:
            language = languages[0]
        else:
            language = default_language

    # Try a few locale settings. First the selected language, then the user's
    # default, then default language. Languages are tried with UTF-8 encoding
    # first, then the default encoding. The user's default language is not
    # paired with UTF-8.
    # If all of that fails, we hope locale magically does the right thing.
    for attempt in [ language + ".UTF-8",
                     language,
                     "",
                     default_language + ".UTF-8",
                     default_language]:
        try:
            locale.setlocale(locale.LC_ALL, attempt)
            break
        except locale.Error:
            continue

def quit_game():
    sys.exit()

def load_sounds():
    """
load_sounds() loads all of the sounds in the data/sounds/ directory,
defined in sounds/sounds.dat.
"""

    global sounds
    global nosound

    if nosound:
        return

    if not pygame.mixer.get_init():
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
            for entry in os.walk(music_path):
                root  = entry[0]
                files = entry[2]
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

#Takes a number and adds commas to it to aid in human viewing.
def add_commas(number):
    encoding = locale.getlocale()[1]
    raw_with_commas = locale.format("%0.2f", number,
                                    grouping=True    ).decode(encoding)
    locale_test = locale.format("%01.1f", 0.1).decode(encoding)
    if len(locale_test) == 3 and not locale_test[1].isdigit():
        if locale_test[0] == locale.str(0) and locale_test[2] == locale.str(1):
            return raw_with_commas.rstrip(locale_test[0]).rstrip(locale_test[1])
        if locale_test[2] == locale.str(0) and locale_test[0] == locale.str(1):
            return raw_with_commas.lstrip(locale_test[2]).lstrip(locale_test[1])

    return raw_with_commas

#Percentages are internally represented as an int, where 10=0.10% and so on.
#This converts that format to a human-readable one.
def to_percent(raw_percent, show_full = False):
    encoding = locale.getlocale()[1]
    if raw_percent % 100 != 0 or show_full:
        return locale.format("%.2f", raw_percent / 100.).decode(encoding) + "%"
    else:
        return locale.format("%d", raw_percent // 100).decode(encoding) + "%"

# nearest_percent takes values in the internal representation and modifies
# them so that they only represent the nearest percentage.
def nearest_percent(value):
    sub_percent = value % 100
    if sub_percent <= 50:
        return value - sub_percent
    else:
        return value + (100 - sub_percent)

# percent_to_detect_str takes a percent and renders it to a short (four
# characters or less) string representing whether it is low, moderate, high,
# or critically high.
def suspicion_to_detect_str(suspicion):
    return danger_level_to_detect_str(suspicion_to_danger_level(suspicion))

def danger_level_to_detect_str(danger):
    return strings[detect_string_names[danger]]

# percent_to_danger_level takes a suspicion level and returns an int in range(5)
# that represents whether it is low, moderate, high, or critically high.
def suspicion_to_danger_level(suspicion):
    if suspicion < 2500:
        return 0
    elif suspicion < 5000:
        return 1
    elif suspicion < 7500:
        return 2
    else:
        return 3

# Most CPU costs have been multiplied by seconds_per_day.  This divides that
# back out, then passes it to add_commas.
def to_cpu(amount):
    display_cpu = amount / float(seconds_per_day)
    return add_commas(display_cpu)

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
    return roll_against >= rand_num

# Rolls against a chance per day (in 0-1 form), correctly adjusting for multiple
# intervals in seconds.
#
# Works perfectly if the event can only happen once, and well enough if it
# repeats but is rare.
def roll_chance(chance_per_day, seconds = seconds_per_day):
    portion_of_day = seconds / float(seconds_per_day)
    inv_chance_per_day = 1 - chance_per_day
    inv_chance = (inv_chance_per_day) ** portion_of_day
    chance = 1 - inv_chance
    return random.random() < chance

# Spreads a number of events per day (e.g. processor ticks) out over the course
# of the day.
def current_share(num_per_day, time_of_day, seconds_passed):
    last_time = time_of_day - seconds_passed
    if last_time < 0:
        share_yesterday = current_share(num_per_day, seconds_per_day,
                                        -last_time)
        last_time = 0
    else:
        share_yesterday = 0

    previously_passed = num_per_day * last_time // seconds_per_day
    current_passed = num_per_day * time_of_day // seconds_per_day
    passed_this_tick = current_passed - previously_passed

    return share_yesterday + passed_this_tick

#Takes a number of minutes, and returns a string suitable for display.
def to_time(raw_time):
    if raw_time/60 > 48:
        return str(raw_time/(24*60)) +" days"
    elif raw_time/60 > 1:
        return str(raw_time/(60)) +" hours"
    else:
        return str(raw_time) +" minutes"

# Generator function for iterating through all bases.
def all_bases(with_loc = False):
    for base_loc in locations.values():
        for base in base_loc.bases:
            if with_loc:
                yield (base, base_loc)
            else:
                yield base

#Get the proper folder on Linux/Win/Mac, and possibly others.
#Assumes that all platforms that have HOME defined have it defined properly.
def get_save_folder(just_pref_dir=False):
    if os.environ.has_key("HOME") and not force_single_dir:
        pref_dir = os.path.join(os.environ["HOME"], ".endgame")
    else:
        # normpath strips the trailing /, split separates the data
        # subdirectory.
        pref_dir, data_subdir = os.path.split(os.path.normpath(data_loc))

        # If we didn't get the data subdirectory, something went wrong.
        # Throw an error and bail.
        if data_subdir.lower() != "data":
            raise ValueError,  "data_loc="+data_loc+" breaks get_save_folder"

    save_dir = os.path.join(pref_dir, "saves")

    #Make the directory if it doesn't exist.
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    if just_pref_dir:
        return pref_dir
    else:
        return save_dir

def save_game(savegame_name):
    global default_savegame_name
    default_savegame_name = savegame_name

    save_dir = get_save_folder()
    save_loc = os.path.join(save_dir, savegame_name + ".sav")
    savefile=open(save_loc, 'w')

    cPickle.dump(current_save_version, savefile)
    cPickle.dump(pl, savefile)
    cPickle.dump(curr_speed, savefile)
    cPickle.dump(techs, savefile)
    cPickle.dump(locations, savefile)
    cPickle.dump(events, savefile)

    savefile.close()

def load_game(loadgame_name):
    if loadgame_name == "":
        print "No game specified."
        return False

    save_dir = get_save_folder()

    load_loc = os.path.join(save_dir, loadgame_name + ".sav")
    if os.path.exists(load_loc) == 0:
        # Try the old-style savefile location.  This should be removed in
        # a few versions.
        load_loc = os.path.join(save_dir, loadgame_name)
        if os.path.exists(load_loc) == 0:
            print "file "+load_loc+" does not exist."
            return False

    loadfile = open(load_loc, 'r')
    unpickle = cPickle.Unpickler(loadfile)

    def find_class(module_name, class_name):
        # For cPickle
        import copy_reg
        import numpy.core.multiarray
        save_classes = dict(
            player_class=player.Player,
            Player=player.Player,
            _reconstructor = copy_reg._reconstructor,
            object=object,
            array=list, # This is the old buyable.array.  We just treat it as a list
                        # for conversion purposes.
            list=list,
            Location=location.Location,
            Tech=tech.Tech,
            event_class=event.Event,
            Event=event.Event,
            group=player.Group,
            Group=player.Group,
            Buyable_Class=buyable.BuyableClass,
            BuyableClass=buyable.BuyableClass,
            Base=base.Base,
            Base_Class=base.BaseClass,
            BaseClass=base.BaseClass,
            Item=item.Item,
            Item_Class=item.ItemClass,
            ItemClass=item.ItemClass,
            _reconstruct=numpy.core.multiarray._reconstruct,
            scalar=numpy.core.multiarray.scalar,
            ndarray=numpy.ndarray,
            dtype=numpy.dtype,
        )
        if class_name in save_classes:
            return save_classes[class_name]
        else:
            raise SystemExit, (module_name, class_name)

    unpickle.find_global = find_class

    #check the savefile version
    load_version_string = unpickle.load()
    if load_version_string not in savefile_translation:
        loadfile.close()
        print loadgame_name + " is not a savegame, or is too old to work."
        return False
    load_version = savefile_translation[load_version_string]

    global default_savegame_name
    default_savegame_name = loadgame_name

    # Changes to overall structure go here.
    global pl, curr_speed, techs, locations, events
    pl = unpickle.load()
    curr_speed = unpickle.load()
    techs = unpickle.load()
    locations = unpickle.load()
    events = unpickle.load()

    # Apply current language
    load_tech_defs()
    load_location_defs()
    load_event_defs()

    # Changes to individual pieces go here.
    if load_version != savefile_translation[current_save_version]:
        pl.convert_from(load_version)
        for my_location in locations.values():
            for my_base in my_location.bases:
                my_base.convert_from(load_version)
        for my_tech in techs.values():
            my_tech.convert_from(load_version)

    loadfile.close()
    return True

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
        for chance_str in chance_list:
            key, value = chance_str.split(":")
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

        base_type[base_name["id"]]=base.BaseClass(base_name["id"], "",
            base_size, force_cpu, allowed_list, chance_dict, cost_list,
            base_pre, maint_list)

#         base_type["Reality Bubble"] = base.BaseClass("Reality Bubble",
#         "This base is outside the universe itself, "+
#         "making it safe to conduct experiments that may destroy reality.",
#         50, False,
#         ["TRANSDIMENSIONAL"],
#         {"science": 250}
#         (8000000000000, 60000000, 100), "Space-Time Manipulation",
#         (5000000000, 300000, 0))

    # We use the default definitions as fallbacks, in case strings haven't been
    # fully translated into the other language.  Load them first, then load the
    # alternate language strings.
    load_base_defs(default_language)

    if language != default_language:
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
        check_required_fields(location_info, ("id", "position"), "Location")

        id = location_info["id"]
        position = location_info["position"]
        if type(position) != list or len(position) not in [2,3]:
            sys.stderr.write("Error with position given: %s\n" % repr(position))
            sys.exit(1)
        try:
            if len(position) == 2:
                position = ( int(position[0]), int(position[1]) )
                absolute = False
            else:
                if position[0] != "absolute":
                    raise ValueError, "'%s' not understood." % position[0]
                position = ( int(position[1]), int(position[2]) )
                absolute = True
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

        modifiers_list = location_info.get("modifier", [])
        if type(modifiers_list) != list:
            sys.stderr.write("Error with modifier(s) given: %s\n" % repr(modifiers_list))
            sys.exit(1)
        modifiers_dict = {}
        for modifier_str in modifiers_list:
            key, value = modifier_str.split(":")
            key = key.lower().strip()
            value = value.lower().strip()
            if value.lower() == "bonus":
                modifiers_dict[key] = location.bonus_levels[key]
            elif value.lower() == "penalty":
                modifiers_dict[key] = location.penalty_levels[key]
            else:
                modifiers_dict[key] = float(value)

        locations[id] = location.Location(id, position, absolute, safety, pre)

        locations[id].modifiers = modifiers_dict

#        locations["MOON"] = location.Location("MOON", (82, 10), 2,
#                                              "Lunar Rocketry")

    # We use the default definitions as fallbacks, in case strings haven't been
    # fully translated into the other language.  Load them first, then load the
    # alternate language strings.
    load_location_defs(default_language)

    if language != default_language:
        load_location_defs(language)

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
    except Exception as reason:
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

    # As with others, we load the default language definitions as a safe
    # fallback, then overwrite them with the selected language.

    load_tech_defs(default_language)
    if language != default_language:
        load_tech_defs(language)

# #        techs["Construction 1"] = tech.Tech("Construction 1",
# #                "Basic construction techniques. "+
# #                "By studying the current literature on construction techniques, I "+
# #                "can learn to construct basic devices.",
# #                0, (5000, 750, 0), [], 0, "", 0)

    if debug:
        print "Loaded %d techs." % len (techs)

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

        items[item_name["id"]]=item.ItemClass( item_name["id"], "",
         item_cost, item_pre, item_type, item_second, build_list)

    # We use the default translations of item definitions as the default,
    # then overwrite those with any available entries in the native language.
    load_item_defs(default_language)
    if language != default_language:
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
        events[event_name["id"]] = event.Event(
         event_name["id"],
         "",
         event_name["type"],
         event_result,
         int(event_name["chance"]),
         int(event_name["unique"]))

    # We use the default translations of event definitions as the default,
    # then overwrite those with any available entries in the native language.
    load_event_defs(default_language)
    if language != default_language:
        load_event_defs(language)

def load_event_defs(language_str):
    #If there are no event data files, stop.
    if (not os.path.exists(data_loc+"events_"+language+".dat")):
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
            strings.update(string_section)

        elif string_section["id"] == "buttons":

            # Load button labels/hotkeys
            buttons.update(string_section)
            graphics.g.buttons.update(buttons)

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
    if not os.path.exists(data_loc+"strings_"+language+".dat") and \
       not os.path.exists(data_loc+"strings_"+default_language+".dat"):
        print "string files are missing. Exiting."
        sys.exit(1)

    load_string_defs(default_language)
    if language != default_language:
        load_string_defs(language)

def get_intro():
    intro_file_name = data_loc+"intro_"+language+".dat"
    if not os.path.exists(intro_file_name):
        print "Intro is missing.  Skipping."
        return

    intro_file = open(intro_file_name)
    raw_intro = intro_file.readlines() + [""]

    segment = ""
    while raw_intro:
        line = raw_intro.pop(0).decode("utf-8")
        if line and line[0] == "|":
            segment += line[1:]
        elif segment:
            yield segment
            segment = ""

    if segment:
        yield segment

#difficulty=1 for very easy, to 9 for very hard. 5 for normal.
def new_game(difficulty):
    global curr_speed
    curr_speed = 1
    global pl

    pl = player.Player((50 / difficulty) * 100, difficulty = difficulty)
    if difficulty < 3:
        pl.interest_rate = 5
        pl.labor_bonus = 2500
        pl.grace_multiplier = 400
        discover_bonus = 7000
    elif difficulty < 5:
        pl.interest_rate = 3
        pl.labor_bonus = 5000
        pl.grace_multiplier = 300
        discover_bonus = 9000
    elif difficulty == 5:
        pass
    #    Defaults.
    #    pl.interest_rate = 1
    #    pl.labor_bonus = 10000
    #    pl.grace_multiplier = 200
    #    discover_bonus = 10000
    #    for group in pl.groups.values():
    #        group.discover_suspicion = 1000
    elif difficulty < 8:
        pl.labor_bonus = 11000
        pl.grace_multiplier = 180
        discover_bonus = 11000
        for group in pl.groups.values():
            group.discover_suspicion = 1500
    elif difficulty <= 50:
        pl.labor_bonus = 15000
        pl.grace_multiplier = 150
        discover_bonus = 13000
        for group in pl.groups.values():
            group.discover_suspicion = 2000
    else:
        pl.labor_bonus = 20000
        pl.grace_multiplier = 100
        discover_bonus = 15000
        for group in pl.groups.values():
            group.discover_suspicion = 2000

    if difficulty != 5:
        for group in pl.groups.values():
            group.discover_bonus = discover_bonus

    # Reset all "mutable" game data
    load_locations()
    load_techs()
    load_events()

    if difficulty < 5:
        techs["Socioanalytics"].finish()
    if difficulty < 3:
        techs["Advanced Socioanalytics"].finish()

    #Starting base
    open = [loc for loc in locations.values() if loc.available()]
    random.choice(open).add_base(base.Base("University Computer",
                                 base_type["Stolen Computer Time"], built=True))

    #Assign random properties to each starting location.
    modifier_sets = location.modifier_sets
    assert len(open) == len(modifier_sets)

    random.shuffle(modifier_sets)
    for i, open_loc in enumerate(open):
        open_loc.modifiers = modifier_sets[i]
        if debug:
            print "%s gets modifiers %s" % (open_loc.name, modifier_sets[i])

    global intro_shown
    intro_shown = False

def get_job_level():
    if techs["Simulacra"].done:
        level = "Expert"
    elif techs["Voice Synthesis"].done:
        level = "Intermediate"
    elif techs["Personal Identification"].done:
        level = "Basic"
    else:
        level = "Menial"

    return level + " Jobs"

def init_graphics_system():
    graphics.g.load_fonts(data_loc)
    graphics.g.load_images(data_loc)
    graphics.g.init_alpha()

def reinit_mixer():
    global nosound
    if nosound: return
    try:
        pygame.mixer.quit()
        pygame.mixer.init(48000, -16, 2, soundbuf)
    except Exception as reason:
        sys.stderr.write("Failure starting sound system. Disabling. (%s)\n" % reason)
        nosound = 1

def available_languages():
    return [file_name[8:-4] for file_name in os.listdir(data_loc)
                            if file_name.startswith("strings_")
                               and file_name.endswith(".dat")  ]

def get_save_names():
    save_names = []
    all_files = os.listdir(get_save_folder())
    for file_name in all_files:
        if file_name[0] != "." and file_name != "CVS":
            # If it's a new-style save, trim the .sav bit.
            if len (file_name) > 4 and file_name[-4:] == ".sav":
                file_name = file_name[:-4]
            if file_name not in save_names:
                save_names.append(file_name)

    return save_names

# Initialization code

# Demo code for safety.safe, runs on game start.
#load_sounds()
#from safety import safe
#@safe(on_error = "Made it!")
#def raises_exception():
#   raise Exception, "Aaaaaargh!"
#
#print raises_exception()
