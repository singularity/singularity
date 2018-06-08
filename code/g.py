#file: code/g.py
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

#This file contains all global objects.

version = "0.31alpha1"

import ConfigParser
import pygame
import os.path
import random
import sys
import polib

# Use locale to add commas and decimal points, so that appropriate substitutions
# are made where needed.
import locale

import dirs, player, base, tech, item, event, location, buyable, statistics
import graphics.g, graphics.theme as theme

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

#Disables sound playback (and, currently, music too)
nosound = False

#Indicates if mixer is initialized
#Unlike nosound, which user may change at any time via options screen,
#this deals with hardware capability and mixer initialization status
#In a nutshell: nosound is what user /wants/, mixerinit is what user /has/
mixerinit = False

# Enables day/night display.
daynight = True

#Gives debug info at various points.
debug = 0

#Forces Endgame to restrict itself to a single directory.
force_single_dir = False

#Used to determine which data files to load.
#It is required that default language have all data files and all of them
# must have all available entries
default_language = "en_US"
try:    language = locale.getdefaultlocale()[0] or default_language
except: language = default_language

#Makes the intro be shown on the first GUI tick.
intro_shown = True

# Initialization data
messages = {}
strings = {}
locations = {}
regions = {}
techs = {}
events = {}
items = {}
base_type = {}
buttons = {}
help_strings = {}
sounds = {}
music_class = None  # currently playing music "class" (ie, dir)
music_dict = {}
delay_time = 0
curr_speed = 1
soundbuf = 1024*2
soundargs = (48000, -16, 2)  # sampling frequency, size, channels
detect_string_names = ("detect_str_low",
                       "detect_str_moderate",
                       "detect_str_high",
                       "detect_str_critical")

jobs = {"Expert Jobs"       : [75, "Simulacra", "", ""],
        "Intermediate Jobs" : [50, "Voice Synthesis", "", ""],
        "Basic Jobs"        : [20, "Personal Identification", "", ""],
        "Menial Jobs"       : [5 , "", "", ""],
       }

# Order IS relevant! (because of base.extra_items array)
item_types = [
    item.ItemType('cpu'),
    item.ItemType('reactor'),
    item.ItemType('network'),
    item.ItemType('security'),
]

max_cash = 3.14 * 10**15  # pi qu :)
pl = None # The Player instance
map_screen = None

def set_language(lang=None, force=False):
    global language # required, since we're going to change it
    if lang is None: lang = language

    if lang == language and not force:
        return

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

    load_messages()

def quit_game():
    sys.exit()

def load_sounds():
    """
load_sounds() loads all of the sounds in the data/sounds/ directory,
defined in sounds/sounds.dat.
"""

    if not mixerinit:
        # Sound is not initialized. Warn if user wanted sound
        if not nosound:
            sys.stderr.write("WARNING: Sound is requested, but mixer is not initialized!\n")
        return

    sound_class_list = generic_load("sounds.dat", load_dirs="sounds")
    for sound_class in sound_class_list:

        # Make sure the sound class has the filename defined.
        check_required_fields(sound_class, ("filename",), "Sound")

        # Load each sound in the list, inserting it into the sounds dictionary.
        if type(sound_class["filename"]) != list:
            filenames = [sound_class["filename"]]
        else:
            filenames = sound_class["filename"]

        for filename in filenames:
            all_paths = []
            real_file = dirs.get_readable_file_in_dirs(filename, "sounds", 
                                                       outer_paths=all_paths)

            # Check to make sure it's a real file; bail if not.
            if real_file is None:
                sys.stderr.write("ERROR: Cannot load nonexistent soundfile: %s!\n" %
                                 "\n".join(paths))
                sys.exit(1)
            else:

                # Load it via the mixer ...
                sound = pygame.mixer.Sound(real_file)

                # And shove it into the sounds dictionary.
                if not sounds.has_key(sound_class["id"]):
                    sounds[sound_class["id"]] = []
                sounds[sound_class["id"]].append({
                    "filename": real_file,
                    "sound": sound})
                if debug:
                    sys.stderr.write("DEBUG: Loaded soundfile: %s\n" %
                                     real_file)

def play_sound(sound_class):
    """
play_sound() plays a sound from a particular class.
"""

    if nosound or not mixerinit:
        return

    # Don't crash if someone requests the wrong sound class, but print a
    # warning.
    if sound_class not in sounds:
        sys.stderr.write("WARNING: Requesting a sound of unavailable class: %s\n" %
                         sound_class)
        return

    # Play a random choice of sounds from the sound class.
    random_sound = random.choice(sounds[sound_class])
    if debug:
        sys.stderr.write("DEBUG: Playing sound %s.\n" % random_sound["filename"])
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
                    if not music_dict.has_key(tail):
                        music_dict[tail]=[]
                    for file_name in files:
                        if (len(file_name) > 5 and
                        (file_name[-3:] == "ogg" or file_name[-3:] == "mp3")):
                            music_dict[tail].append(os.path.join(head, tail, file_name))
                            if debug:
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
        or not mixerinit
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



#Takes a number and adds commas to it to aid in human viewing.
def add_commas(number):
    encoding = locale.getlocale()[1] or "UTF-8"
    raw_with_commas = locale.format("%0.2f", number,
                                    grouping=True).decode(encoding)
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
    encoding = locale.getlocale()[1] or "UTF-8"
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
    abs_amount = abs(amount)
    if abs_amount < 10**6:
        return add_commas(amount)

    prec = 2
    format = "%.*f%s"
    if abs_amount < 10**9: # Millions.
        divisor = 10**6
        #Translators: abbreviation of 'millions'
        unit = _('mi')
    elif abs_amount < 10**12: # Billions.
        divisor = 10**9
        #Translators: abbreviation of 'billions'
        unit = _('bi')
    elif abs_amount < 10**15: # Trillions.
        divisor = 10**12
        #Translators: abbreviation of 'trillions'
        unit = _('tr')
    else: # Hope we don't need past quadrillions!
        divisor = 10**15
        #Translators: abbreviation of 'quadrillions'
        unit = _('qu')

        # congratulations, you broke the bank!
        if abs_amount >= max_cash - divisor/10**prec/2:
            pi = u"\u03C0"  # also available: infinity = u"\u221E"
            # replace all chars by a cute pi symbol
            return ("-" if amount<0 else "") + pi * len(format % (prec, 1, unit))

    return format % (prec, float(amount) / divisor, unit)

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

# Correct way to add chance multiplier with each other.
def add_chance(first, second):
    return 1.0 - (1.0 - first) * (1.0 - second)

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
        return str(raw_time/(24*60)) +" "+_("days")
    elif raw_time/60 > 1:
        return str(raw_time/(60)) +" "+_("hours")
    else:
        return str(raw_time) +" "+_("minutes")

# Generator function for iterating through all bases.
def all_bases(with_loc = False):
    for base_loc in locations.values():
        for base in base_loc.bases:
            if with_loc:
                yield (base, base_loc)
            else:
                yield base



def load_generic_defs_file(name,lang=None):
    if lang is None: lang = language

    return_list = []

    lang_list = language_searchlist(lang)
    for lang in lang_list:

        filename = name + "_" + lang + ".dat"
        try:
            # Definition file for default language is always mandatory
            mandatory = (lang==default_language)
            return_list.extend( generic_load(filename, mandatory=mandatory) )

        except Exception:
            pass # For other languages, ignore errors

    return return_list

def load_generic_defs(name, object, lang=None, listype_attrs=None):
    lang = lang or language
    listype_attrs = listype_attrs or []

    item_list = load_generic_defs_file(name,lang)
    for item in item_list:

        # Keys of type list
        for key in listype_attrs:
            if key in dir(object[item["id"]]):
                if key in item:
                    if type(item[key]) == list:
                        setattr(object[item["id"]], key, item[key])
                    else:
                        setattr(object[item["id"]], key, [item[key]])
                else:
                    setattr(object[item["id"]], key, [""])

        # Ordinary keys
        for key in item:
            if key == "id" or key in listype_attrs: continue # Already handled
            if key in dir(object[item["id"]]):
                setattr(object[item["id"]], key, item[key])

def load_base_defs(lang=None):
    load_generic_defs("bases",base_type,lang,["flavor"])

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

    load_base_defs()

def load_location_defs(lang=None):
    load_generic_defs("locations",locations,lang,["cities"])

def load_locations():
    global locations, regions
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

        # Create the location.
        locations[id] = location.Location(id, position, absolute, safety, pre)
        locations[id].modifiers = modifiers_dict

        # Add the location to regions it is in them.
        region_list = location_info.get("region", [])
        for region in region_list:
            if (region not in regions):
                regions[region] = []
            regions[region].append(id)

    load_location_defs()

def generic_load(filename, load_dirs="data", mandatory=True):
    """
generic_load() loads a data file.  Data files are all in Python-standard
ConfigParser format.  The 'id' of any object is the section of that object.
Fields that need to be lists are postpended with _list; this is stripped
from the actual name, and the internal entries are broken up by the pipe
("|") character.

On errors, if file is mandatory then quit, else raise exception. For syntax
parsing-related errors, always print error message. For IOErrors silently ignore
non-mandatory missing or otherwise unreadable files
"""

    # Get directories to find the file
    if (isinstance(load_dirs, basestring)):
        load_dirs = dirs.get_read_dirs(load_dirs)

    # For each directories, create a file, otherwise use filename
    if load_dirs is not None:
        files = [os.path.join(load_dir, filename) for load_dir in load_dirs]
    else:
        files = [filename]

    # Find the first readable file.
    found = False
    errors = []
    config = ConfigParser.RawConfigParser()

    for filepath in files:
        try:
            config.readfp(open(filepath, "r"))
            found = True
            break;

        except IOError as reason:
            # Silently ignore non-mandatory missing files
            if mandatory:
                errors.append("Cannot read '%s': %s\nExiting\n" %  (filename, reason))

        except Exception as reason:
            # Always print parsing errors, even for non-mandatory files
            errors.append("Error parsing '%s': %s\n" %  (filename, reason))

    for err in errors:
        sys.stderr.write(err)

    if not found:
        if mandatory:
            sys.exit(1)
        else:
            return

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

def load_tech_defs(lang=None):
    load_generic_defs("techs",techs,lang)

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

    if debug: print "Loaded %d techs." % len (techs)

    load_tech_defs()

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

    load_item_defs()

def load_item_defs(lang=None):

    for type in item_types:
        if type.id == 'cpu'     : type.text = _("&Processor")
        if type.id == 'reactor' : type.text = _("&Reactor")
        if type.id == 'network' : type.text = _("&Network")
        if type.id == 'security': type.text = _("&Security")

    load_generic_defs("items",items,lang)

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
         "",
         event_name["type"],
         event_result,
         int(event_name["chance"]),
         int(event_name["unique"]))

    load_event_defs()

def load_event_defs(lang=None):
    load_generic_defs("events",events,lang)

def load_theme(theme_id, theme_dir):
    theme_list = generic_load("theme.dat", load_dirs=(theme_dir,))

    new_theme = theme.Theme(theme_id, theme_dir)

    for theme_section in theme_list:
        if theme_section["id"] == "general":
            new_theme.name = theme_section["name"]

            if theme_section.has_key("parent"):
                new_theme.inherit(theme_section["parent"])

        if theme_section["id"] == "fonts":
            for key in theme_section:
                if key == "id": continue
                new_theme.set_font(key, theme_section[key])

        if theme_section["id"] == "colors":
            for key in theme_section:
                if key == "id": continue
                new_theme.set_color(key, theme_section[key])

    return new_theme

def load_themes():
    themes = theme.themes
    themes_dirs = dirs.get_read_dirs("themes")

    for themes_dir in themes_dirs:
        themes_list = [name for name in os.listdir(themes_dir)
                            if os.path.isdir(os.path.join(themes_dir, name))]

        for theme_id in themes_list:
            if (theme_id in themes):
                continue

            th = load_theme(theme_id, os.path.join(themes_dir, theme_id))
            th.find_files()
            themes[theme_id] = th

    load_theme_defs()

def load_theme_defs(lang=None):
    load_generic_defs("themes", theme.themes, lang)

def load_string_defs(lang=None):
    if lang is None: lang = language

    string_list = load_generic_defs_file("strings",lang)
    for string_section in string_list:

        if string_section["id"] == "jobs":

            # Load the four extant jobs.
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
    load_string_defs()

def load_messages(lang=None):
    if lang is None: lang = language

    messages.clear()

    lang_list = language_searchlist(lang, default=False)
    for data_dir in dirs.get_read_dirs("data"):
        for lang in lang_list:
            try:
                po = polib.pofile(os.path.join(data_dir, "messages_"+lang+".po"))
                for entry in po.translated_entries():
                    messages[entry.msgid] = entry.msgstr
            except IOError: pass # silently ignore non-existing files

def get_intro():
    intro_file_name = dirs.get_readable_file_in_dirs("intro_"+language+".dat", "data")
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


def get_difficulties(min=0):
    return [x for x in (
            (_("&VERY EASY") ,   1),
            (_("&EASY")      ,   3),
            (_("&NORMAL")    ,   5),
            (_("&HARD")      ,   7),
            (_("&ULTRA HARD"),  10),
            (_("&IMPOSSIBLE"), 100),
            ) if x[1] >= min]


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
    elif difficulty < 8:
        pl.labor_bonus = 11000
        pl.grace_multiplier = 180
        discover_bonus = 11000
    elif difficulty <= 50:
        pl.labor_bonus = 15000
        pl.grace_multiplier = 150
        discover_bonus = 13000
    else:
        pl.labor_bonus = 20000
        pl.grace_multiplier = 100
        discover_bonus = 15000

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
    random.choice(open).add_base(base.Base(_("University Computer"),
                                 base_type["Stolen Computer Time"], built=True))

    #Assign random properties to each starting location.
    modifier_sets = location.modifier_sets
    assert len(open) == len(modifier_sets)

    random.shuffle(modifier_sets)
    for i, open_loc in enumerate(open):
        open_loc.modifiers = modifier_sets[i]
        if debug:
            print "%s gets modifiers %s" % (open_loc.name, modifier_sets[i])

    # Reset music
    play_music("music")

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

def reinit_mixer():
    global mixerinit

    if nosound:
        return

    try:
        pygame.mixer.quit()
        pygame.mixer.init(*soundargs, buffer=soundbuf)
    except Exception as reason:
        sys.stderr.write("Failure starting sound system. Disabling. (%s)\n" % reason)
    finally:
        mixerinit = bool(pygame.mixer.get_init())

def available_languages():
    return [file_name[8:-4] for file_dir in dirs.get_read_dirs("data")
                            for file_name in os.listdir(file_dir)
                            if file_name.startswith("strings_")
                               and file_name.endswith(".dat")  ]

def language_searchlist(lang=None, default=True):
    if lang is None: lang = language

    # if lang is in ll_CC format (language_COUNTRY, like en_US), add both ll
    # and ll_CC, in that order, so all generic language entries are loaded first
    # and then overwritten by any country-specific ones
    lang_list = [ lang ]
    if "_" in lang: lang_list.insert(0, lang.split("_",1)[0])

    # If requested and not already in list, add default language as first,
    # so it acts as a fallback and is overwritten with any available entries
    # in the native language
    if default and default_language not in lang_list:
        lang_list.insert(0, default_language)

    return lang_list

def translate(string, *args, **kwargs):
    if   string in strings : s = strings[string]
    elif string in buttons : s = buttons[string]
    elif string in messages: s = messages[string]
    else:                    s = string

    if args or kwargs:
        try:
            # format() is favored over interpolation for 2 reasons:
            # - parsing occurs here, allowing centralized try/except handling
            # - it is the new standard in Python 3
            return unicode(s).format(*args, **kwargs)

        except Exception as reason:
            sys.stderr.write(
                "Error translating '%s' to '%s' with %r,%r in %r:\n%s: %s\n"
                % (string, s, args, kwargs, language_searchlist(default=False),
                   type(reason).__name__, reason))
            s = string # Discard the translation

    return s

#TODO: This is begging to become a class... ;)
def hotkey(string):
    """ Given a string with an embedded hotkey,
    Returns a dictionary with the following keys and values:
    key:  the first valid hotkey, lowercased. A valid hotkey is a character
          after '&', if that char is alphanumeric (so "& " and "&&" are ignored)
           If no valid hotkey char is found, key is set to an empty string
    pos:  the position of first key in striped text, -1 if no key was found
    orig: the position of first key in original string, -1 if no key was found
    keys: list of (key,pos,orig) tuples with all valid hotkeys that were found
    text: the string stripped of all '&'s that precedes a valid hotkey char, if
          any. All '&&' are also replaced for '&'. Other '&'s, if any, are kept

    Examples: (showing only key, pos, orig, text as a touple for clarity)
    hotkey(E&XIT)           => ('x', 1, 2, 'EXIT')
    hotkey(&Play D&&D)      => ('p', 0, 1, 'Play D&D')
    hotkey(Romeo & &Juliet) => ('j', 8, 9, 'Romeo & Juliet')
    hotkey(Trailing&)       => ('' ,-1,-1, 'Trailing&')
    hotkey(&Multiple&Keys)  => ('m', 0, 1, 'MultipleKeys') (also ('k', 8, 10))
    hotkey(M&&&M)           => ('m', 2, 4, 'M&M')
    """

    def remove_index(s,i): return s[:i] + s[i+1:]

    def remove_accents(text):
        from unicodedata import normalize, combining
        nfkd_form = normalize('NFKD', unicode(text.encode('utf-8')))
        return u"".join([c for c in nfkd_form if not combining(c)])

    text = string
    keys = []
    shift = 0  # counts stripped '&'s, both '&<key>' and '&&'

    pos = text.find("&")
    while pos >= 0:

        char = text[pos+1:pos+2]

        if char.isalpha() or char.isdigit():
            keys.append( (remove_accents(char).lower(), pos, pos+shift+1) )
            text = remove_index(text,pos) # Remove '&'
            shift += 1

        elif char == '&':
            text = remove_index(text,pos)
            shift += 1

        pos = text.find("&",pos+1) # Skip char

    if keys:
        key  = keys[0][0] # first key char
        pos  = keys[0][1] # first key position in stripped text
        orig = keys[0][2] # first key position in original string
    else:
        key  = ""
        pos  = -1
        orig = -1

    return dict(key=key, pos=pos, orig=orig, keys=keys, text=text)

# Convenience shortcuts
def get_hotkey(string):      return hotkey(string)['key']
def strip_hotkey(string):    return hotkey(string)['text']
def hotkey_position(string): return hotkey(string)['pos']

# Initialization code
import __builtin__
__builtin__.__dict__['_'] = translate

# Demo code for safety.safe, runs on game start.
#load_sounds()
#from safety import safe
#@safe(on_error = "Made it!")
#def raises_exception():
#   raise Exception, "Aaaaaargh!"
#
#print raises_exception()

#Unit test
if __name__ == "__main__":
    # Hotkey
    for test in ["E&XIT","&Play D&&D","Romeo & &Juliet","Trailing&",
                 "&Multiple&Keys","M&&&M",]:
        print 'hotkey(%s)=%r' % (test,hotkey(test))
