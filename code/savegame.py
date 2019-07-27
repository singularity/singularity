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

import cPickle
import collections
import os

import g, mixer, dirs, player

#name given when the savegame button is pressed. This is changed when the
#game is loaded or saved.
from code import group

default_savegame_name = "Default Save"

#savefile version; update whenever the data saved changes.
current_save_version = "singularity_savefile_99.6"
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
}

Savegame = collections.namedtuple('Savegame', ['name', 'filepath', 'version'])

def get_savegames():
    all_dirs = dirs.get_read_dirs("saves")

    all_savegames = []
    for saves_dir in all_dirs:
        try:
            all_files = os.listdir(saves_dir)
        except:
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
                        loadfile = open(filepath, 'r')
                        unpickle = cPickle.Unpickler(loadfile)

                        load_version = unpickle.load()
                        if load_version in savefile_translation:
                            version_name = savefile_translation[load_version][0]
                    except:
                        version_name = None # To be sure.

                    savegame = Savegame(name, filepath, version_name)
                    all_savegames.append(savegame)

    return all_savegames


def delete_savegame(savegame):
    load_path = savegame.filepath

    if load_path is None:
        return False

    try:
        os.remove(load_path)
    except:
        return False

def load_savegame(savegame):
    global default_savegame_name

    load_path = savegame.filepath

    if load_path is None:
        return False

    loadfile = open(load_path, 'r')
    unpickle = cPickle.Unpickler(loadfile)

    def find_class(module_name, class_name):
        # For cPickle
        import copy_reg
        import numpy.core.multiarray
        import collections
        import player, base, tech, item, event, location, buyable, difficulty, effect
        save_classes = dict(
            player_class=player.Player,
            Player=player.Player,
            _reconstructor = copy_reg._reconstructor,
            object=object,
            array=list,  # This is the old buyable.array.
                         # We just treat it as a list for conversion purposes.
            list=list,
            Location=location.Location,
            Tech=tech.Tech,
            event_class=event.Event,
            Event=event.Event,
            group=group.Group,
            Group=group.Group,
            GroupClass=group.GroupClass,
            Buyable_Class=buyable.BuyableClass,
            BuyableClass=buyable.BuyableClass,
            Base=base.Base,
            Base_Class=base.BaseClass,
            BaseClass=base.BaseClass,
            Item=item.Item,
            Item_Class=item.ItemClass,
            ItemClass=item.ItemClass,
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
    loaded_techs = unpickle.load()
    loaded_locations = unpickle.load()
    g.events = unpickle.load()

    import data
    # Reload the techs from the data files.  This ensures we always have *all*
    # the technologies from the current version of the game.  We will then merge
    # relevant state from the save game into the g.techs table below.
    data.load_techs()
    data.load_locations()

    # Changes to individual pieces go here.
    if load_version != savefile_translation[current_save_version]:
        g.pl.convert_from(load_version)
        for my_location in loaded_locations.values():
            for my_base in my_location.bases:
                my_base.convert_from(load_version)
                for my_item in my_base.all_items():
                    my_item.convert_from(load_version)
        for my_group in g.pl.groups.values():
            my_group.convert_from(load_version)
        for my_tech in loaded_techs.values():
            my_tech.convert_from(load_version)
        for my_event in g.events.values():
            my_event.convert_from(load_version)

    # Merge relevant parts of the restored techs into the g.techs structure
    for tech_id, tech_from_savegame in loaded_techs.items():
        if tech_id not in g.techs:
            # Discard obsolete tech
            continue
        tech = g.techs[tech_id]
        # Restore the "done" flag.  We do not use finish, because the effect is
        # already applied on the player job (and finish then apply it again).
        tech.done = tech_from_savegame.done
        # Properly set the "cost_paid" to match.
        if tech.done:
            tech.cost_paid = tech.total_cost
        else:
            tech.cost_paid = tech_from_savegame.cost_paid

    for location_id, location_from_savegame in loaded_locations.items():
        location = g.locations.get(location_id)
        if location is None:
            # Discard bases at (now) unknown locations.
            continue
        # We avoid "add_base" because savegames have pre-applied bonuses
        location.bases.extend(location_from_savegame.bases)

    data.reload_all_mutable_def()

    # Play the appropriate music
    if g.pl.apotheosis:
        mixer.play_music("win")
    else:
        mixer.play_music("music")

    loadfile.close()
    return True

def savegame_exists(savegame_name):
    save_path = dirs.get_writable_file_in_dirs(savegame_name + ".sav", "saves")

    if (save_path is None or not os.path.isfile(save_path)) :
        return False

    return True

def create_savegame(savegame_name):
    global default_savegame_name
    default_savegame_name = savegame_name

    save_loc = dirs.get_writable_file_in_dirs(savegame_name + ".sav", "saves")
    savefile = open(save_loc, 'w')

    cPickle.dump(current_save_version, savefile)
    cPickle.dump(g.pl, savefile)
    cPickle.dump(g.curr_speed, savefile)
    cPickle.dump(g.techs, savefile)
    cPickle.dump(g.locations, savefile)
    cPickle.dump(g.events, savefile)

    savefile.close()

class SavegameException(Exception):
    def __init__(self, module_name, class_name):
        super(SavegameException, self).__init__("Invalid class in savegame: %s.%s" 
                % (module_name, class_name))
