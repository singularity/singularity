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

import cPickle
import collections
import gzip
import json
import os

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

Savegame = collections.namedtuple('Savegame', ['name', 'filepath', 'version'])


def convert_string_to_path_name(name):
    # Some filesystems require unicode (e.g. Windows) whereas Linux needs bytes.
    # Python 2 is rather forgiving which works as long as you work with ASCII,
    # but some people might like non-ASCII in their savegame names
    # (https://bugs.debian.org/718447)
    if os.path.supports_unicode_filenames:
        return name
    return name.encode('utf-8')


def convert_path_name_to_str(path):
    # Some filesystems require unicode (e.g. Windows) whereas Linux needs bytes.
    # Python 2 is rather forgiving which works as long as you work with ASCII,
    # but some people might like non-ASCII in their savegame names
    # (https://bugs.debian.org/718447)
    if os.path.supports_unicode_filenames:
        return path
    return path.decode('utf-8', errors='replace')


def get_savegames():
    all_dirs = dirs.get_read_dirs("saves")

    all_savegames = []
    for saves_dir in all_dirs:
        try:
            all_files = os.listdir(saves_dir)
        except Exception:
            continue

        for file_name in all_files:
            if file_name[0] != "." and file_name != "CVS":
                # If it's a new-style save, trim the .sav bit.
                if file_name.endswith('.sav'):
                    name = file_name[:-4]
                    filepath = os.path.join(saves_dir, file_name)

                    # Get version, only pickle first string.
                    version_name = None # None == Unknown version
                    try:
                        with open(filepath, 'rb') as loadfile:
                            unpickle = cPickle.Unpickler(loadfile)

                            def find_class(module_name, class_name):
                                # Lets reduce the risk of "funny monkey business"
                                # when checking the version of pickled files
                                raise SavegameException(module_name, class_name)

                            unpickle.find_global = find_class

                            load_version = unpickle.load()
                            if load_version in savefile_translation:
                                version_name = savefile_translation[load_version][0]
                    except Exception:
                        version_name = None # To be sure.
                    savegame = Savegame(convert_path_name_to_str(name), filepath, version_name)
                    all_savegames.append(savegame)
                elif file_name.endswith('.s2'):
                    name = file_name[:-3]
                    filepath = os.path.join(saves_dir, file_name)
                    version_name = None
                    try:
                        with open(filepath, 'rb') as loadfile:
                            load_version, headers = parse_json_game_headers(loadfile)
                            if load_version in savefile_translation:
                                version_name = savefile_translation[load_version][0]
                    except Exception:
                        version_name = None
                    savegame = Savegame(convert_path_name_to_str(name), filepath, version_name)
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


def parse_json_game_headers(fd):
    version_line = fd.readline().decode('utf-8').strip()
    headers = {}
    while True:
        line = fd.readline().decode('utf-8').strip()

        if line == '':
            break
        key, value = line.split('=', 1)
        headers[key] = value
    return version_line, headers


def load_savegame(savegame):
    global default_savegame_name

    load_path = savegame.filepath

    if load_path is None:
        return False

    if 'json' in savegame.version:
        return load_savegame_by_json(savegame)
    else:
        return load_savegame_by_pickle(savegame)


def load_savegame_by_json(savegame):
    global default_savegame_name

    load_path = savegame.filepath
    with open(load_path, 'rb') as fd:
        load_version_string, headers = parse_json_game_headers(fd)
        if load_version_string not in savefile_translation:
            print(savegame.name + " is not a savegame, or is too old to work.")
            return False

        load_version = savefile_translation[load_version_string][1]
        difficulty_id = headers['difficulty']
        game_time = int(headers['game_time'])

        next_byte = fd.peek(1)[0]
        if next_byte == b'{':
            game_data = json.load(fd)
        elif next_byte == b'H':
            # gzip in base64 starts with H4s
            encoded = fd.read()
            bio = BytesIO(base64.standard_b64decode(encoded))
            with gzip.GzipFile(filename='', mode='rb', fileobj=bio) as gzip_fd:
                game_data = json.load(gzip_fd)
            # Remove some variables that we do not use any longer to enable
            # python to garbage collect them
            del bio
            del encoded
        else:
            print("Unexpected byte: %s" % repr(next_byte))
            return False
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

    default_savegame_name = savegame.name
    return True


def load_savegame_by_pickle(savegame):

    global default_savegame_name
    load_path = savegame.filepath

    loadfile = open(load_path, 'rb')
    unpickle = cPickle.Unpickler(loadfile)

    stats.reset()

    def find_class(module_name, class_name):
        # For cPickle
        import copy_reg
        import numpy.core.multiarray
        import collections

        save_classes = dict(
            player_class=player.Player,
            Player=player.Player,
            _reconstructor = copy_reg._reconstructor,
            object=object,
            array=list,  # This is the old buyable.array.
                         # We just treat it as a list for conversion purposes.
            list=list,
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
            raise SavegameException(module_name, class_name)

    unpickle.find_global = find_class

    #check the savefile version
    load_version_string = unpickle.load()
    if load_version_string not in savefile_translation:
        loadfile.close()
        print(savegame.name + " is not a savegame, or is too old to work.")
        return False
    load_version = savefile_translation[load_version_string][1]

    default_savegame_name = savegame.name

    data.reset_techs()
    data.reset_events()

    # Changes to overall structure go here.
    saved_player = unpickle.load()
    # Current speed (ignored)
    unpickle.load()
    # Pause game when loading
    g.curr_speed = 0
    techs = unpickle.load()
    if load_version < 99.7:
        # In >= 99.8 locations are saved as a part of the player object, but earlier
        # it was stored as a separate part of the stream.
        locations = unpickle.load()
    else:
        locations = saved_player.locations
    events = unpickle.load()

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

    for tech_id, saved_tech in techs.items():
        if tech_id == 'unknown_tech':
            continue
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
    return True


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
    save_path = dirs.get_writable_file_in_dirs(convert_string_to_path_name(savegame_name) + ".sav", "saves")

    if (save_path is None or not os.path.isfile(save_path)) :
        return False

    return True


def create_savegame(savegame_name):
    global default_savegame_name
    default_savegame_name = savegame_name
    save_loc = dirs.get_writable_file_in_dirs(convert_string_to_path_name(savegame_name) + ".sav", "saves")
    save_loc_v2 = dirs.get_writable_file_in_dirs(convert_string_to_path_name(savegame_name) + ".s2", "saves")

    # Save in legacy format
    with open(save_loc, 'wb') as savefile:
        cPickle.dump(current_save_version_pickle, savefile, protocol=2)
        cPickle.dump(g.pl, savefile, protocol=2)
        cPickle.dump(g.curr_speed, savefile, protocol=2)
        cPickle.dump(g.techs, savefile, protocol=2)
        cPickle.dump(g.events, savefile, protocol=2)

    # Save in new "JSONish" format
    with open(save_loc_v2, 'wb') as savefile:
        version_line = "%s\n" % current_save_version
        savefile.write(version_line.encode('utf-8'))
        headers = [
            ('difficulty', g.pl.difficulty.id),
            ('game_time', str(g.pl.raw_sec)),
        ]
        for k, v in headers:
            kw_str = "%s=%s\n" % (k, v)
            savefile.write(kw_str.encode('utf-8'))
        savefile.write(b'\n')
        game_data = {
            'player': g.pl.serialize_obj(),
            'techs': [t.serialize_obj() for tid, t in sorted(g.techs.items()) if t.available()],
            'events': [e.serialize_obj() for eid, e in sorted(g.events.items())]
        }
        if g.debug:
            json.dump(game_data, savefile)
        else:
            bio = BytesIO()
            with gzip.GzipFile(filename='', mode='wb', fileobj=bio) as gzip_fd:
                json.dump(game_data, gzip_fd)
            encoded = base64.standard_b64encode(bio.getvalue())
            savefile.write(encoded)


class SavegameException(Exception):
    def __init__(self, module_name, class_name):
        super(SavegameException, self).__init__("Invalid class in savegame: %s.%s" 
                % (module_name, class_name))
