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

from __future__ import absolute_import


import collections
import random
import sys

# Use locale to add commas and decimal points, so that appropriate substitutions
# are made where needed.
import locale

from singularity.code.pycompat import *


# Useful constants.
hours_per_day = 24
minutes_per_hour = 60
minutes_per_day = 24 * 60
seconds_per_minute = 60
seconds_per_hour = 60 * 60
seconds_per_day = 24 * 60 * 60

#Allows access to the cheat menu.
cheater = 0

# Enables day/night display.
daynight = True

#Gives debug info at various points.
debug = 0

#Forces Endgame to restrict itself to a single directory.
force_single_dir = False

# Initialization data
significant_numbers = []
internal_id_forward = {}
internal_id_backward = {}
dangers = {}
data_strings = {}
story_translations = {}
story = {}
knowledge = {}
groups = {}
locations = {}
regions = {}
techs = {}
events = {}
event_specs = {}
items = {}
tasks = {}
tasks_by_type = collections.defaultdict(list)
base_type = {}
buttons = {}
help_strings = {}
delay_time = 0
curr_speed = 1

max_cash = 3.14 * 10**15  # pi qu :)
pl = None # The Player instance
map_screen = None

def no_gui():
    """ Disable few pygame functionality (used for test) """
    import singularity.code.mixer as mixer
    mixer.nosound = True

def quit_game():
    sys.exit()

#Takes a number and adds commas to it to aid in human viewing.
def add_commas(number, fixed_size=False):
    # Do not use unicode strings to fix python2 format bug. It doesn't work and crash.
    # See the correct fix at the end of function.
    raw_with_commas = locale.format_string("%0.2f", number,
                                    grouping=True)
    locale_test = locale.format_string("%01.1f", 0.1) if not fixed_size else ''
    if len(locale_test) == 3 and not locale_test[1].isdigit():
        if locale_test[0] == locale.str(0) and locale_test[2] == locale.str(1):
            raw_with_commas = raw_with_commas.rstrip(locale_test[0]).rstrip(locale_test[1])
        elif locale_test[2] == locale.str(0) and locale_test[0] == locale.str(1):
            raw_with_commas = raw_with_commas.lstrip(locale_test[2]).lstrip(locale_test[1])

    # Fix python2 format bug: See https://bugs.python.org/issue15276
    # Note: This a crah in some platform, do not remove it because you can't reproduce it.
    try:
        return unicode(raw_with_commas)
    except UnicodeDecodeError:
        return raw_with_commas.decode("utf-8")


#Percentages are internally represented as an int, where 10=0.10% and so on.
#This converts that format to a human-readable one.
def to_percent(raw_percent, show_full = False):
    if raw_percent % 100 != 0 or show_full:
        return _('{0}%').format(locale.format_string(u"%.2f", raw_percent / 100.))
    else:
        return _('{0}%').format(locale.format_string(u"%d", raw_percent // 100))


# nearest_percent takes values in the internal representation and modifies
# them so that they only represent the nearest percentage.
def nearest_percent(value, step=100):
    sub_percent = value % step
    if 2 * sub_percent <= step:
        return value - sub_percent
    else:
        return value + (step - sub_percent)

# percent_to_detect_str takes a percent and renders it to a short (four
# characters or less) string representing whether it is low, moderate, high,
# or critically high.
def suspicion_to_detect_str(suspicion):
    return danger_level_to_detect_str(suspicion_to_danger_level(suspicion))

def danger_level_to_detect_str(danger):
    detect_string_names = (_("LOW"),
                           _("MODR"),
                           _("HIGH"),
                           _("CRIT"))
    return detect_string_names[danger]

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
def to_money(amount, fixed_size=False):
    abs_amount = abs(amount)
    if abs_amount < 10**6:
        return add_commas(amount, fixed_size=fixed_size)

    prec = 2
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
            format_str = "%0.*f%s" if fixed_size else "%.*f%s"
            pi = u"\u03C0"  # also available: infinity = u"\u221E"
            # replace all chars by a cute pi symbol
            return ("-" if amount < 0 else "") + pi * len(format_str % (prec, 1, unit))

    amount = round(float(amount) / divisor, prec)
    return add_commas(amount, fixed_size=fixed_size) + unit

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


# Takes a number of minutes, and returns a string suitable for display.
def to_time(raw_time):
    if raw_time//60 > 48:
        time_number = raw_time // (24*60)
        return ngettext("{0} day", "{0} days", time_number).format(time_number)
    if raw_time//60 > 1:
        time_number = raw_time // 60
        return ngettext("{0} hour", "{0} hours", time_number).format(time_number)
    return ngettext("{0} minute", "{0} minutes", raw_time).format(raw_time)


# Generator function for iterating through all bases.
def all_bases(with_loc = False):
    for base_loc in pl.locations.values():
        for base in base_loc.bases:
            if with_loc:
                yield (base, base_loc)
            else:
                yield base


def get_story_section(name):
    section = story[name]

    for segment in section:
        # TODO: Execute command
        key = (segment.msgctxt, segment.text)
        yield story_translations.get(key, segment.text)


def new_game(difficulty_name, initial_speed=1):
    global curr_speed
    curr_speed = initial_speed
    global pl

    from singularity.code.stats import itself as stats
    stats.reset()

    from singularity.code import difficulty, player, base

    diff = difficulty.difficulties[difficulty_name]

    pl = player.Player(cash = diff.starting_cash, difficulty = diff)

    for tech_id in diff.techs:
        pl.techs[tech_id].finish(is_player=False)

    #Starting base
    open = [loc for loc in pl.locations.values() if loc.available()]
    random.choice(open).add_base(base.Base(_("University Computer"),
                                 base_type["Stolen Computer Time"], built=True))

    pl.initialize()


def read_modifiers_dict(modifiers_info):
    modifiers_dict = {}

    for modifier_str in modifiers_info:
        key, value = modifier_str.split(":")
        key = key.lower().strip()
        value_str = value.lower().strip()

        if "/" in value_str:
            left, right = value_str.split("/")
            value = float(left.strip()) / float(right.strip())
        else:
            value = float(value_str)

        modifiers_dict[key] = float(value)

    return modifiers_dict


internal_id_version = None

def to_internal_id(obj_type, obj_id):
    if internal_id_version:
        try:
            return internal_id_forward[obj_type + "_" + internal_id_version][obj_id]
        except KeyError:
            pass

    try:
        return internal_id_forward[obj_type][obj_id]
    except KeyError:
        # If we cannot, that's should not happen, but try to return as is.
        return obj_id

def from_internal_id(obj_type, obj_internal_id):
    try:
        return internal_id_backward[obj_type][obj_internal_id]
    except KeyError:
        raise ValueError("Cannot convert internal ID: %s" % obj_internal_id) # That's should not happen

def convert_internal_id(id_type, id_value):
    if id_value is None:
        return None

    internal_id = id_value

    # Not a internal ID, transform to it.
    if not internal_id.startswith("0x"):
        internal_id = to_internal_id(id_type, id_value)

    return from_internal_id(id_type, internal_id)

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

    Examples: (showing only key, pos, orig, text as a tuple for clarity)
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
        from singularity.code.pycompat import unicode
        nfkd_form = normalize('NFKD', unicode(text))
        return u"".join(c for c in nfkd_form if not combining(c))

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

# Demo code for safety.safe, runs on game start.
#load_sounds()
#from safety import safe
#@safe(on_error = "Made it!")
#def raises_exception():
#   raise Exception, "Aaaaaargh!"
#
#print raises_exception()
