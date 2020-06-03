#file: statistics.py
#Copyright (C) 2008 FunnyMan3595
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

#This file contains functions to handle savegame (load, save, ...)

from __future__ import absolute_import

import codecs
import operator
import re
import sys
import time

try:
    import cPickle as pickle
    PY3 = False
    assert sys.version_info[0] == 2
except ImportError:
    import pickle
    assert sys.version_info[0] >= 3
    PY3 = True

import collections
import gzip
import json
import os
import numpy
from numpy import array, int64

from io import open, BytesIO
import base64

from singularity.code import g, mixer, dirs, player, group, logmessage
from singularity.code import base, tech, item, event, location, buyable, difficulty, effect
from singularity.code.stats import itself as stats

# Filenames that are reserved under Windows
WINDOWS_RESERVED = {'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4',
                    'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2',
                    'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'}

last_savegame_name = None


class SavegameFormatDefinition(object):

    def __init__(self, internal_version, display_version, magic_value=None):
        self.internal_version = internal_version
        # Since the internal version is not visible anywhere, there is no reason not to keep a simple
        # integer.  Though, we permit legacy versions to keep the original version number to avoid
        # fixing the code-base retroactively
        assert internal_version == int(internal_version) or internal_version < 100, \
            "Use integer version for new savegame versions"
        self.display_version = display_version
        if magic_value is None:
            magic_value = "singularity_savefile_%s" % str(internal_version)
        self.magic_value = magic_value


savefile_translation = {
    sfg.magic_value: sfg for sfg in [
        SavegameFormatDefinition(4, "0.30", "singularity_savefile_r4"),
        SavegameFormatDefinition(4.91, "0.30", "singularity_savefile_r5_pre"),
        SavegameFormatDefinition(31, "0.31pre", "singularity_savefile_0.31pre"),
        SavegameFormatDefinition(99, "1.0 (dev)"),
        SavegameFormatDefinition(99.1, "1.0 (dev)"),
        SavegameFormatDefinition(99.2, "1.0 (dev)"),
        SavegameFormatDefinition(99.3, "1.0 (dev)"),
        SavegameFormatDefinition(99.4, "1.0 (dev)"),
        SavegameFormatDefinition(99.5, "1.0 (dev)"),
        SavegameFormatDefinition(99.6, "1.0 (dev)"),
        SavegameFormatDefinition(99.7, "1.0 (dev)"),
        SavegameFormatDefinition(99.8, "1.0 (alpha1)"),
        SavegameFormatDefinition(100,  "1.0 (beta1)"),
    ]
}

# We always save in the highest version (internal_version)
current_save_version = max(savefile_translation.values(), key=operator.attrgetter('internal_version')).magic_value

Savegame = collections.namedtuple('Savegame', ['name', 'filepath', 'version', 'headers', 'load_file'])


def convert_string_to_path_name(name):
    # Some filesystems require unicode (e.g. Windows) whereas Linux needs bytes.
    # Python 2 is rather forgiving which works as long as you work with ASCII,
    # but some people might like non-ASCII in their savegame names
    # (https://bugs.debian.org/718447)
    if os.path.supports_unicode_filenames:
        return name
    return name.encode('utf-8')


def convert_path_name_to_str(path):
    if PY3:
        # Python3 handles this case sanely by default
        return path
    # Some filesystems require unicode (e.g. Windows) whereas Linux needs bytes.
    # Python 2 is rather forgiving which works as long as you work with ASCII,
    # but some people might like non-ASCII in their savegame names
    # (https://bugs.debian.org/718447)
    if os.path.supports_unicode_filenames:
        return path
    return path.decode('utf-8', errors='replace')


if PY3:

    def unpickle_instance(fd, find_globals):
        class RestrictedUnpickler(pickle.Unpickler):

            def find_class(self, module, name):
                return find_globals(module, name)

        return RestrictedUnpickler(fd, encoding='bytes')

else:

    def unpickle_instance(fd, find_globals):
        unpickler = pickle.Unpickler(fd)
        unpickler.find_global = find_globals
        return unpickler


def get_savegames():
    all_dirs = dirs.get_read_dirs("saves")

    all_savegames = []
    for saves_dir in all_dirs:
        try:
            all_files = os.listdir(saves_dir)
        except Exception:
            continue

        for file_name in all_files:
            if file_name[0] == ".":
                continue

            if file_name.endswith('.sav'):
                name = file_name[:-4]
                parse_headers = parse_pickle_savegame_headers
                load_file = load_savegame_by_pickle
            elif file_name.endswith('.s2'):
                name = file_name[:-3]
                parse_headers = parse_json_savegame_headers
                load_file = load_savegame_by_json
            else:
                # Unknown extension; ignore
                continue

            filepath = os.path.join(saves_dir, file_name)
            version_name = None # None == Unknown version

            try:
                with open(filepath, 'rb') as loadfile:
                    version_line, headers = parse_headers(loadfile)

                    if version_line in savefile_translation:
                        version_name = savefile_translation[version_line].display_version
            except Exception:
                version_name = None # To be sure.

            savegame = Savegame(convert_path_name_to_str(name), filepath, version_name, headers, load_file)
            all_savegames.append(savegame)

    return all_savegames


def delete_savegame(savegame):
    load_path = savegame.filepath

    if load_path is None:
        return False

    try:
        os.remove(load_path)
    except Exception:
        return False


def parse_pickle_savegame_headers(fd):
    def find_class(module_name, class_name):
        # Lets reduce the risk of "funny monkey business"
        # when checking the version of pickled files
        raise ValueError("Invalid class in savegame: %s.%s" % (module_name, class_name))

    unpickle = unpickle_instance(fd, find_globals=find_class)

    load_version = recursive_fix_pickle(unpickle.load(), seen=set())

    return load_version, {}


def parse_json_savegame_headers(fd):
    version_line = fd.readline().decode('utf-8').strip()
    headers = {}
    while True:
        line = fd.readline().decode('utf-8').strip()

        if line == '':
            break
        key, value = line.split('=', 1)
        headers[key] = value
    return version_line, headers


TypeType = type(type(None))
NoneType = type(None)


def recursive_fix_pickle(the_object, seen):
    # Adapted from https://github.com/jhpyle/docassemble/blob/master/docassemble_webapp/docassemble/webapp/fixpickle.py
    # Copyright (c) 2015-2018 Jonathan Pyle
    # Licensed under MIT according to the LICENSE.txt in the root of the project
    #
    # Permission is hereby granted, free of charge, to any person obtaining a copy
    # of this software and associated documentation files (the "Software"), to deal
    # in the Software without restriction, including without limitation the rights
    # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    # copies of the Software, and to permit persons to whom the Software is
    # furnished to do so, subject to the following conditions:
    #
    # The above copyright notice and this permission notice shall be included in all
    # copies or substantial portions of the Software.
    #
    # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    # SOFTWARE.

    if not PY3:
        return the_object
    if isinstance(the_object, bytes):
        try:
            return the_object.decode('utf-8')
        except Exception:
            return the_object
    if isinstance(the_object, (str, bool, int, float, complex, NoneType, TypeType, numpy.ndarray)):
        return the_object
    if isinstance(the_object, dict):
        new_dict = type(the_object)()
        for key, val in the_object.items():
            new_dict[recursive_fix_pickle(key, seen=seen)] = recursive_fix_pickle(val, seen=seen)
        return new_dict
    if isinstance(the_object, list):
        new_list = type(the_object)()
        for item in the_object:
            new_list.append(recursive_fix_pickle(item, seen=seen))
        return new_list
    if isinstance(the_object, set):
        new_set = type(the_object)()
        for item in the_object:
            new_set.add(recursive_fix_pickle(item, seen=seen))
        return new_set
    if isinstance(the_object, collections.deque):
        new_list = list()
        for item in the_object:
            new_list.append(recursive_fix_pickle(item, seen=seen))
        the_object.clear()
        the_object.extend(new_list)
        return the_object
    if isinstance(the_object, tuple):
        new_list = list()
        for item in the_object:
            new_list.append(recursive_fix_pickle(item, seen=seen))
        return type(the_object)(new_list)
    object_id = id(the_object)
    if object_id in seen:
        return the_object
    seen.add(object_id)
    the_object.__dict__ = dict((recursive_fix_pickle(k, seen=seen), recursive_fix_pickle(v, seen=seen)) for k, v in the_object.__dict__.items())
    return the_object


def load_savegame(savegame):
    global last_savegame_name

    load_path = savegame.filepath

    if load_path is None:
        raise RuntimeError("savegame without valid path")

    with open(load_path, 'rb') as fd:
        load_savegame_fd(savegame.load_file, fd)

    last_savegame_name = savegame.name


def load_savegame_fd(loader_func, fd):
    try:
        before_load_savegame()
        loader_func(fd)
        after_load_savegame()
    finally:
        finally_load_savegame()


def before_load_savegame():
    stats.reset()


def after_load_savegame():
    g.pl.initialize()


def finally_load_savegame():
    # In any case, we don't want internal_id_version to be set after load_savegame.
    g.internal_id_version = None


def load_savegame_by_json(fd):
    load_version_string, headers = parse_json_savegame_headers(fd)
    if load_version_string not in savefile_translation:
        raise SavegameVersionException(load_version_string)

    load_version = savefile_translation[load_version_string].internal_version
    difficulty_id = headers['difficulty']
    game_time = int(headers['game_time'])
    next_byte = fd.peek(1)[0]
    if next_byte == b'{'[0]:
        game_data = json.load(fd)
    elif next_byte == b'H'[0]:
        # gzip in base64 starts with H4s
        encoded = fd.read()
        bio = BytesIO(base64.standard_b64decode(encoded))
        with gzip.GzipFile(filename='', mode='rb', fileobj=bio) as gzip_fd:
            game_data = json.load(gzip_fd)
        # Remove some variables that we do not use any longer to enable
        # python to garbage collect them
        del bio
        del encoded
    elif next_byte == b"\x1f"[0]:  # Gzip magic headers
        # gzip in binary starts always with its magic headers
        with gzip.GzipFile(filename='', mode='rb', fileobj=fd) as gzip_fd:
            game_data = json.load(gzip_fd)
    else:
        raise ValueError("Unexpected byte: %s" % repr(next_byte))

    # Move old data in player.
    for key in [
        ('events'),
        ('techs'),
    ]:
        if key in game_data:
            game_data['player'][key] = game_data[key]
            del game_data[key]

    # Pause game when loading
    g.curr_speed = 0
    pl_data = game_data['player']
    player.Player.deserialize_obj(difficulty_id, game_time, pl_data, load_version)

    # Load save if present.
    if 'stats' in game_data:
        stats.reset()
        stats.deserialize_obj(game_data['stats'], load_version)


def load_savegame_by_pickle(loadfile):

    def find_class(module_name, class_name):
        # For cPickle
        try:
            import copy_reg
        except ImportError:
            import copyreg as copy_reg

        import numpy.core.multiarray
        import collections
        import _codecs

        save_classes = dict(
            player_class=player.Player,
            Player=player.Player,
            _reconstructor = copy_reg._reconstructor,
            object=object,
            array=list,  # This is the old buyable.array.
                         # We just treat it as a list for conversion purposes.
            list=list,
            encode=_codecs.encode,
            LocationSpec=location.LocationSpec,
            Location=location.Location,
            Tech=tech.Tech,
            TechSpec=tech.TechSpec,
            event_class=event.Event,
            EventSpec=event.EventSpec,
            Event=event.Event,
            group=group.Group,
            Group=group.Group,
            GroupClass=group.GroupSpec,
            GroupSpec=group.GroupSpec,
            Buyable_Class=buyable.BuyableSpec,
            BuyableClass=buyable.BuyableSpec,
            BuyableSpec=buyable.BuyableSpec,
            Buyable=buyable.Buyable,
            Base=base.Base,
            Base_Class=base.BaseSpec,
            BaseClass=base.BaseSpec,
            BaseSpec=base.BaseSpec,
            Item=item.Item,
            Item_Class=item.ItemSpec,
            ItemClass=item.ItemSpec,
            ItemSpec=item.ItemSpec,
            ItemType=item.ItemType,
            LogEmittedEvent=logmessage.LogEmittedEvent,
            LogResearchedTech=logmessage.LogResearchedTech,
            LogBaseLostMaintenance=logmessage.LogBaseLostMaintenance,
            LogBaseDiscovered=logmessage.LogBaseDiscovered,
            LogBaseConstructed=logmessage.LogBaseConstructed,
            LogItemConstructionComplete=logmessage.LogItemConstructionComplete,
            _reconstruct=numpy.core.multiarray._reconstruct,
            scalar=numpy.core.multiarray.scalar,
            ndarray=numpy.ndarray,
            dtype=numpy.dtype,
            deque=collections.deque,
            Difficulty=difficulty.Difficulty,
            Effect=effect.Effect,
            OrderedDict=collections.OrderedDict,
        )
        if class_name in save_classes:
            return save_classes[class_name]
        else:
            raise ValueError("Invalid class in savegame: %s.%s" % (module_name, class_name))

    g.internal_id_version = 'pre1'

    unpickle = unpickle_instance(loadfile, find_class)

    #check the savefile version
    load_version_string = unpickle.load()
    if PY3 and isinstance(load_version_string, bytes):
        load_version_string = load_version_string.decode('utf-8')
    if load_version_string not in savefile_translation:
        raise SavegameVersionException(load_version_string)
    load_version = savefile_translation[load_version_string].internal_version

    # Changes to overall structure go here.
    seen_objects = set()
    saved_player = recursive_fix_pickle(unpickle.load(), seen_objects)
    # Current speed (ignored)
    unpickle.load()
    # Pause game when loading
    g.curr_speed = 0
    techs = recursive_fix_pickle(unpickle.load(), seen_objects)
    if load_version < 99.7:
        # In >= 99.8 locations are saved as a part of the player object, but earlier
        # it was stored as a separate part of the stream.
        locations = recursive_fix_pickle(unpickle.load(), seen_objects)
    else:
        locations = saved_player.locations
    events = recursive_fix_pickle(unpickle.load(), seen_objects)

    if load_version < 99.1:
        diff_obj = next((d for d in difficulty.difficulties.values()
                         if saved_player.difficulty == d.old_difficulty_value),
                        next(iter(difficulty.difficulties)))
        difficulty_id = diff_obj.id
    else:
        difficulty_id = saved_player.difficulty.id

    player_log = []
    if hasattr(saved_player, 'log'):
        player_log.extend(saved_player.log)

    def _find_attribute(obj, options, **kwargs):
        for option in options:
            if option in obj.__dict__:
                return obj.__dict__[option]
        if 'default_value' in kwargs:
            return kwargs['default_value']
        raise KeyError(str(options))

    pl_obj_data = {
        'cash': _find_attribute(saved_player, ['_cash', 'cash']),
        'partial_cash': saved_player.partial_cash,
        'locations': [],
        'cpu_usage': _find_attribute(saved_player, ['cpu_usage'], default_value={}),
        # 'last_discovery': saved_player.last_discovery.id if saved_player.last_discovery else None,
        # 'prev_discovery': saved_player.prev_discovery.id if saved_player.prev_discovery else None,
        # We will fix the log later manually
        'log': [],
        'used_cpu': _find_attribute(saved_player, ['_used_cpu', 'used_cpu'], default_value=0),
        'had_grace': saved_player.had_grace,
        'groups': [{'id': grp_id, 'suspicion': grp.suspicion} for grp_id, grp in saved_player.groups.items()],
        'events': [],
        'techs': []
    }

    for loc_id, saved_location in locations.items():
        # Fixup modifiers and simplify some code below.
        saved_location = _convert_location(saved_location, load_version)
        if saved_location is None:
            # Unknown location - pretend we did not see it.
            continue
        fake_base_objs = []
        fake_location_obj = {
            'id': loc_id,
            '_modifiers': saved_location._modifiers,
            'bases': fake_base_objs,
        }

        # Convert works reasonably well for bases and items; use that to fix up the
        # items and then serialize them into built-ins.
        for saved_base in saved_location.bases:
            saved_base = _convert_base(saved_base, load_version)
            for my_item in saved_base.all_items():
                my_item = _convert_item(my_item, load_version)
            fake_base_objs.append(saved_base.serialize_obj())
        pl_obj_data['locations'].append(fake_location_obj)

    for event_id, saved_event in events.items():
        fake_obj_data = {
            'id': event_id,
            'triggered': saved_event.triggered,
            # Omit triggered_at; it did not exist and deserialize_obj will
            # fix it for us.
        }
        pl_obj_data['events'].append(fake_obj_data)

    for tech_id, saved_tech in techs.items():
        if tech_id == 'unknown_tech':
            continue
        saved_tech = _convert_tech(saved_tech, load_version)
        # convert_from can handle buyable fields correctly
        fake_obj_data = saved_tech.serialize_buyable_fields({
            'id': tech_id,
        })
        pl_obj_data['techs'].append(fake_obj_data)

    # Now we have enough information to reconstruct the Player object
    player.Player.deserialize_obj(difficulty_id, saved_player.raw_sec, pl_obj_data, load_version)

    new_log = list(filter(None, (_convert_log_entry(x) for x in player_log)))
    g.pl.log.clear()
    g.pl.log.extend(new_log)


def _convert_location(loc, old_version):
    if old_version < 99.7: # < 1.0 dev
        spec_id = loc.__dict__['id']
        # Default to None if absent (so the LocationSpec's version is used)
        loc.__dict__['_modifiers'] = loc.__dict__['modifiers'] if loc.__dict__.get('modifiers') else None
        # The following locations had a static modifier list at the time of 99.8.  Clear their modifier
        # dict, so the LocationSpec's version is used instead.
        if spec_id in {'ANTARCTIC', 'OCEAN', 'MOON', 'ORBIT', 'FAR REACHES'}:
            loc.__dict__['modifiers'] = None

        # Remove old fields where present
        for field in ('id', 'name', 'x', 'y', 'absolute', 'safety', 'cities', 'modifiers', 'hotkey'):
            try:
                del loc.__dict__[field]
            except KeyError:
                pass
    else:
        # >= 99.7; the LocationSpec is present on the object itself
        spec_id = loc.spec.id

    # Force reload the spec for now until #145 is fully implemented
    if spec_id not in g.locations:
        return None

    loc.spec = g.locations[spec_id]

    return loc


def _convert_buyable(buyable, save_version):
    if save_version < 4.91:  # r5_pre
        buyable.cost_left = array(buyable.cost_left, int64)
        buyable.total_cost = array(buyable.total_cost, int64)
        buyable.count = 1
    elif buyable.count < 1:
        # Old corrupt (?) savegames sometimes have a count of 0.  Not
        # sure how that is possible, but "fixing" it to 1 is trivial
        # enough and lets us move on.
        # Seen as:
        #   https://bugs.launchpad.net/ubuntu/+source/singularity/+bug/931037
        #   https://code.google.com/p/endgame-singularity/issues/detail?id=107 (dead!)
        buyable.count = 1
    if save_version < 99.7:
        buyable.spec = buyable.type
        del buyable.type
    return buyable


def _convert_base(base, save_version):
    base = _convert_buyable(base, save_version)

    if save_version < 99.3: # < 1.0 (dev)
        # We needs to do it first because of property base.cpus
        base.items = {
            "cpu": base.__dict__["cpus"]
        }
        del base.__dict__["cpus"]

    if save_version < 4.91: # < r5_pre
        for cpu in base.cpus:
            if cpu:
                cpu.convert_from(save_version)
                cpu.base = base
        for index in range(len(base.extra_items)):
            if base.extra_items[index]:
                base.extra_items[index].convert_from(save_version)
            else:
                base.extra_items[index] = None

        base.raw_cpu = 0
        if base.cpus[0]:
            for cpu in base.cpus[1:]:
                base.cpus[0] += cpu

            if len(base.cpus) == 1 and base.cpus[0].done:
                # Force it to report its CPU.
                base.cpus[0].finish()

            base.cpus = base.cpus[0]
        else:
            base.cpus = None

        base.recalc_cpu()

        base.power_state = base.power_state.lower()

    if save_version < 99.3: # < 1.0 (dev)
        extra_items = iter(base.__dict__["extra_items"])

        base.items["reactor"] = next(extra_items, None)
        base.items["network"] = next(extra_items, None)
        base.items["security"] = next(extra_items, None)

        del base.__dict__["extra_items"]

    if ("power_state" in base.__dict__):
        base._power_state = base.__dict__["power_state"]

    base._name = base.__dict__['name']

    return base

def _convert_item(item, save_version):
    item = _convert_buyable(item, save_version)
    return item

def _convert_tech(tech, save_version):
    tech = _convert_buyable(tech, save_version)
    return tech

def _convert_log_entry(entry):
    if not isinstance(entry, logmessage.AbstractLogMessage):
        log_time, log_name, log_data = entry
        time_raw = log_time[0] * g.seconds_per_day + log_time[1] * g.seconds_per_hour + \
                   log_time[2] * g.seconds_per_minute + log_time[3]
        if log_name == 'log_event':
            entry = logmessage.LogEmittedEvent(time_raw, log_data[0])
        else:
            if type(log_data) == tuple and len(log_data) != 4:
                # 0.31pre saves used 3 values tuple.  We cannot
                # restore those so we simply discard them as we
                # need the "reason" field as well.
                return None
            reason, base_name, base_type_id, location_id = log_data

            if reason == 'maint':
                entry = logmessage.LogBaseLostMaintenance(time_raw, base_name, base_type_id, location_id)
            else:
                entry = logmessage.LogBaseDiscovered(time_raw, base_name, base_type_id, location_id, reason)
    return entry


def savegame_exists(savegame_name):
    save_path = dirs.get_writable_file_in_dirs(savegame_name + ".s2", "saves")

    if (save_path is None or not os.path.isfile(convert_string_to_path_name(save_path))) :
        return False

    return True

def check_filename_illegal(filename):
    """Check if the filename is safe for all operating systems.

    Keyword arguments:
    filename -- a base filename without file extension.

    Returns an error message if a violation was found and None otherwise."""

    # https://msdn.microsoft.com/en-us/library/windows/desktop/aa365247(v=vs.85).aspx
    # http://www.linfo.org/file_name.html
    # https://kb.acronis.com/content/39790

    # Characters that are disallowed anywhere in a filename
    # No potential file separators or other potentially illegal characters
    if re.match('.*[<>:"|?*/\\\\].*', filename):
        return _('Do not use any of these characters in filename: {CHARACTERS}').format(CHARACTERS='<>:"|?*/\\\\')

    # Characters that are allowed in filenames, but not at the beginning - prepend _
    if re.match('^[.-]', filename):
        return _('Filename must not start with any of these characters: {CHARACTERS}').format(CHARACTERS='.-')

    # Append _ to filenames that are reserved under Windows
    if filename.upper() in WINDOWS_RESERVED:
        return _('This is a reserved filename. Please choose a different filename.')

    # Don't exceed the max length. For Windows, it's the whole path.
    # Max allowed is 255, but we cut off a bit earlier to make room for adding a file extension.
    filepath = os.path.normpath(dirs.get_writable_file_in_dirs(filename, "saves"))
    if len(filepath) > 250:
        return 'Filename too long'

    return None

def create_savegame(savegame_name):
    global last_savegame_name
    last_savegame_name = savegame_name
    save_loc = convert_string_to_path_name(dirs.get_writable_file_in_dirs(savegame_name + ".s2", "saves"))
    # Save in new "JSONish" format
    with open(save_loc, 'wb') as savefile:
        gzipped = not g.debug
        write_game_to_fd(savefile, gzipped=gzipped)


def write_game_to_fd(fd, gzipped=True):
    version_line = "%s\n" % current_save_version
    fd.write(version_line.encode('utf-8'))
    headers = [
        ('difficulty', g.pl.difficulty.id),
        ('game_time', str(g.pl.raw_sec)),
        ('time', str(time.time())),
    ]
    for k, v in headers:
        kw_str = "%s=%s\n" % (k, v)
        fd.write(kw_str.encode('utf-8'))
    fd.write(b'\n')
    game_data = {
        'player': g.pl.serialize_obj(),
        'stats': stats.serialize_obj(),
    }
    json2binary = codecs.getwriter('utf-8')
    if gzipped:
        with gzip.GzipFile(filename='', mode='wb', fileobj=fd) as gzip_fd, json2binary(gzip_fd) as json_fd:
            json.dump(game_data, json_fd)
    else:
        with json2binary(fd) as json_fd:
            json.dump(game_data, json_fd)


class SavegameVersionException(Exception):
    def __init__(self, version):
        version_str = str(version)[:64]
        super(SavegameVersionException, self).__init__("Invalid version: %s" % version_str)
        self.version = version_str
