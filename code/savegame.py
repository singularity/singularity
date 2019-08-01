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
import os

from code import g, mixer, dirs, player, group, data
from code import base, tech, item, event, location, buyable, difficulty, effect


default_savegame_name = u"Default Save"

#savefile version; update whenever the data saved changes.
current_save_version = "singularity_savefile_99.7"
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
        except RuntimeError:
            continue

        for file_name in all_files:
            if file_name[0] != "." and file_name != "CVS":
                # If it's a new-style save, trim the .sav bit.
                if len (file_name) > 4 and file_name[-4:] == ".sav":
                    name = file_name[:-4]
                    filepath = os.path.join(saves_dir, file_name)

                    # Get version, only pickle first string.
                    version_name = None # None == Unknown version
                    try:
                        with open(filepath, 'rb') as loadfile:
                            unpickle = cPickle.Unpickler(loadfile)

                            load_version = unpickle.load()
                            if load_version in savefile_translation:
                                version_name = savefile_translation[load_version][0]
                    except RuntimeError:
                        version_name = None # To be sure.
                    savegame = Savegame(convert_path_name_to_str(name), filepath, version_name)
                    all_savegames.append(savegame)

    return all_savegames


def delete_savegame(savegame):
    load_path = savegame.filepath

    if load_path is None:
        return False

    try:
        os.remove(load_path)
    except RuntimeError:
        return False

def load_savegame(savegame):
    global default_savegame_name

    load_path = savegame.filepath

    if load_path is None:
        return False

    loadfile = open(load_path, 'rb')
    unpickle = cPickle.Unpickler(loadfile)

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
        print savegame.name + " is not a savegame, or is too old to work."
        return False
    load_version = savefile_translation[load_version_string][1]

    default_savegame_name = savegame.name

    # Changes to overall structure go here.
    g.pl = unpickle.load()
    g.curr_speed = unpickle.load()
    g.techs = unpickle.load()
    if load_version < 99.7:
        # In >= 99.8 locations are saved as a part of the player object, but earlier
        # it was stored as a separate part of the stream.
        g.pl.locations = unpickle.load()
    g.events = unpickle.load()

    # Changes to individual pieces go here.
    if load_version != savefile_translation[current_save_version]:
        g.pl.convert_from(load_version)
        for my_group in g.pl.groups.values():
            my_group.convert_from(load_version)
        for my_tech in g.techs.values():
            my_tech.convert_from(load_version)
        for my_event in g.events.values():
            my_event.convert_from(load_version)

    data.reload_all_mutable_def()

    # Play the appropriate music
    if g.pl.apotheosis:
        mixer.play_music("win")
    else:
        mixer.play_music("music")

    loadfile.close()
    return True


def savegame_exists(savegame_name):
    save_path = dirs.get_writable_file_in_dirs(convert_string_to_path_name(savegame_name) + ".sav", "saves")

    if (save_path is None or not os.path.isfile(save_path)) :
        return False

    return True


def create_savegame(savegame_name):
    global default_savegame_name
    default_savegame_name = savegame_name
    save_loc = dirs.get_writable_file_in_dirs(convert_string_to_path_name(savegame_name) + ".sav", "saves")
    with open(save_loc, 'wb') as savefile:
        cPickle.dump(current_save_version, savefile)
        cPickle.dump(g.pl, savefile)
        cPickle.dump(g.curr_speed, savefile)
        cPickle.dump(g.techs, savefile)
        cPickle.dump(g.events, savefile)


class SavegameException(Exception):
    def __init__(self, module_name, class_name):
        super(SavegameException, self).__init__("Invalid class in savegame: %s.%s" 
                % (module_name, class_name))
