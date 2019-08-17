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
import sys

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

from io import open, BytesIO
import base64

from code import g, mixer, dirs, player, group, data, logmessage
from code import base, tech, item, event, location, buyable, difficulty, effect
from code.stats import itself as stats

default_savegame_name = u"Default Save"

#savefile version; update whenever the data saved changes.
current_save_version_pickle = "singularity_savefile_99.7"
current_save_version = "singularity_savefile_99.8"
savefile_translation = {
    "singularity_savefile_r4":      ("0.30",         4   ),
    "singularity_savefile_r5_pre":  ("0.30",         4.91),
    "singularity_savefile_0.31pre": ("1.0 (dev)",   31   ),
    "singularity_savefile_99":      ("1.0 (dev)",   99   ),
    "singularity_savefile_99.1":    ("1.0 (dev)",   99.1 ),
    "singularity_savefile_99.2":    ("1.0 (dev)",   99.2 ),
    "singularity_savefile_99.3":    ("1.0 (dev)",   99.3 ),
    "singularity_savefile_99.4":    ("1.0 (dev)",   99.4 ),
    "singularity_savefile_99.5":    ("1.0 (dev)",   99.5 ),
    "singularity_savefile_99.6":    ("1.0 (dev)",   99.6 ),
    "singularity_savefile_99.7":    ("1.0 (dev)",   99.7 ),
    "singularity_savefile_99.8":    ("1.0 (dev+json)",   99.8 ),
}

Savegame = collections.namedtuple('Savegame', ['name', 'filepath', 'version', 'load_file'])


# TODO: We should use a persistent internal ID that is immune to us renaming
# human visible IDs.
ID_REMAPPING = {
    'tech/Fusion Reactor': 'Fusion Power'
}


def convert_id(id_type, id_value, loading_from_game_version):
    return ID_REMAPPING.get("%s/%s" % (id_type, id_value), id_value)


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
                        version_name = savefile_translation[version_line][0]
            except Exception:
                version_name = None # To be sure.

            savegame = Savegame(convert_path_name_to_str(name), filepath, version_name, load_file)
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
        raise SavegameException(module_name, class_name)

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
    global default_savegame_name

    load_path = savegame.filepath

    if load_path is None:
        raise RuntimeError("savegame without valid path")
    
    with open(load_path, 'rb') as fd:
        savegame.load_file(fd)

    default_savegame_name = savegame.name

def load_savegame_by_json(fd):
    load_version_string, headers = parse_json_savegame_headers(fd)
    if load_version_string not in savefile_translation:
        raise SavegameVersionException(load_version_string)

    load_version = savefile_translation[load_version_string][1]
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
    data.reset_techs()
    data.reset_events()

    # Pause game when loading
    g.curr_speed = 0
    pl_data = game_data['player']
    player.Player.deserialize_obj(difficulty_id, game_time, pl_data, load_version)
    for key, cls in [
        ('techs', tech.Tech),
        ('events', event.Event),
    ]:
        for obj_data in game_data[key]:
            cls.deserialize_obj(obj_data, load_version)

    for b in g.all_bases():
        if b.done:
            b.recalc_cpu()
    g.pl.recalc_cpu()

    data.reload_all_mutable_def()


def load_savegame_by_pickle(loadfile):

    stats.reset()

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


    unpickle = unpickle_instance(loadfile, find_class)

    #check the savefile version
    load_version_string = unpickle.load()
    if PY3 and isinstance(load_version_string, bytes):
        load_version_string = load_version_string.decode('utf-8')
    if load_version_string not in savefile_translation:
        raise SavegameVersionException(load_version_string)
    load_version = savefile_translation[load_version_string][1]

    data.reset_techs()
    data.reset_events()

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
        'groups': [{'id': grp_id, 'suspicion': grp.suspicion} for grp_id, grp in saved_player.groups.items()]
    }

    for loc_id, saved_location in locations.items():
        # Fixup modifiers and simplify some code below.
        saved_location.convert_from(load_version)
        if saved_location.spec.id == location.DEAD_LOCATION_SPEC.id:
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
            # Note: We do not convert the "studying" field.  Savegames so old that
            # they still rely on that field will lose the CPU allocations.
            saved_base.convert_from(load_version)
            for my_item in saved_base.all_items():
                my_item.convert_from(load_version)
            fake_base_objs.append(saved_base.serialize_obj())
        pl_obj_data['locations'].append(fake_location_obj)

    # Now we have enough information to reconstruct the Player object
    player.Player.deserialize_obj(difficulty_id, saved_player.raw_sec, pl_obj_data, load_version)

    for orig_tech_id, saved_tech in techs.items():
        if orig_tech_id == 'unknown_tech':
            continue
        tech_id = convert_id('tech', orig_tech_id, load_version)
        # convert_from can handle buyable fields correctly
        saved_tech.convert_from(load_version)
        fake_obj_data = saved_tech.serialize_buyable_fields({
            'id': tech_id,
        })
        tech.Tech.deserialize_obj(fake_obj_data, load_version)
    for event_id, saved_event in events.items():
        fake_obj_data = {
            'id': event_id,
            'triggered': saved_event.triggered,
            # Omit triggered_at; it did not exist and deserialize_obj will
            # fix it for us.
        }
        event.Event.deserialize_obj(fake_obj_data, load_version)

    new_log = [_convert_log_entry(x) for x in player_log]
    g.pl.log.clear()
    g.pl.log.extend(new_log)

    for b in g.all_bases():
        if b.done:
            b.recalc_cpu()
    g.pl.recalc_cpu()

    data.reload_all_mutable_def()

    # Play the appropriate music
    if g.pl.apotheosis:
        mixer.play_music("win")
    else:
        mixer.play_music("music")

    loadfile.close()


def _convert_log_entry(entry):
    if not isinstance(entry, logmessage.AbstractLogMessage):
        log_time, log_name, log_data = entry
        time_raw = log_time[0] * g.seconds_per_day + log_time[1] * g.seconds_per_hour + \
                   log_time[2] * g.seconds_per_minute + log_time[3]
        if log_name == 'log_event':
            entry = logmessage.LogEmittedEvent(time_raw, log_data[0])
        else:
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


def create_savegame(savegame_name):
    global default_savegame_name
    default_savegame_name = savegame_name
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
    ]
    for k, v in headers:
        kw_str = "%s=%s\n" % (k, v)
        fd.write(kw_str.encode('utf-8'))
    fd.write(b'\n')
    game_data = {
        'player': g.pl.serialize_obj(),
        'techs': [t.serialize_obj() for tid, t in sorted(g.techs.items()) if t.available()],
        'events': [e.serialize_obj() for eid, e in sorted(g.events.items())]
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
        super(SavegameException, self).__init__("Invalid version: %s" % version_str)
        self.version = version_str
