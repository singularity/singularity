#file: dirs.py
#Copyright (C) 2008 Evil Mr Henry, Phil Bordelon, and FunnyMan3595
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

#This file contains all functions to find and create singularity directory.
#Get the proper folder on Linux/Win/Mac, and possibly others.
#Assumes that all platforms that have HOME and XDG_CONFIG_HOME defined have them
# defined properly.

import os
import sys
import errno

import g

read_dirs = {}
write_dirs = {}

# Used to differentiate between version.
version_dir = '1.0'

""" Definition of generated directories for E:S
    Directories are grouped with a symbolic name.

    The first object define generic propriety of the directories:
    'writable' for writable directory.

    Following objects define a potential directory:
    'mandatory' means the absence of directory is a fatal error.
    'parent' allows to definite a directory with another.
    (Note: only parent with one directory are handled )
    'path' is the relative path of directory.

    Directories are read is the order there are defined, else the write
    directory first.
    By default it is the first writable directory found.
    Writable directory is never mandatory, but will be created if possible.
"""
dir_defs = (
    ( {"name":"data", "mandatory": True},
        {"parent": "root",        "path": "data",           },
    ),
    ( {"name":"i18n", "writable": True},
        {"parent": "files_home",  "path": "i18n",           }, # New XDG dir
        {"parent": "root",        "path": "i18n",           },
    ),
    ( {"name":"music", },
        {"parent": "files_home",  "path": "music",          }, # New XDG dir
        {"parent": "old_home",    "path": "music",          }, # Old .endgame dir
        {"parent": "root",        "path": "music",          },
    ),
    ( {"name":"sounds", },
        {"parent": "data",        "path": "sounds"          },
    ),
    ( {"name":"themes", "mandatory": True, "writable": True},
        {"parent": "files_home",  "path": "themes",         }, # New XDG dir
        {"parent": "data",        "path": "themes",         },
    ),
    ( {"name":"saves", "writable": True},
        {"parent": "files_home",  "path": "saves",          }, # New XDG dir
        {"parent": "config_home", "path": "saves",          },
        {"parent": "old_home",    "path": "saves",          }, # Old .endgame dir
        {"parent": "root",        "path": "saves",          }, # Single dir
    ),
    ( {"name":"pref", "writable": True},
        {"parent": "config_home", "path": version_dir,      },
        {"parent": "config_home", "path": "",               },
        {"parent": "old_home",    "path": "",               }, # Old .endgame dir
        {"parent": "root",        "path": "",               }, # Single dir
    ),
    ( {"name":"log", "writable": True},
        {"parent": "files_home",  "path": "log",            }, # New XDG dir
        {"parent": "config_home", "path": "log",            },
        {"parent": "old_home",    "path": "log",            }, # Old .endgame dir
        {"parent": "root",        "path": "log",            }, # Single dir
    ),
)

dirs_errs = []

def create_directories(force_single_dir):

    # root dir: the install directory for E:S.
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    read_dirs["root"] = [root_dir]
    write_dirs["root"] = root_dir

    # config_home: user home directory that contains configuration.
    # file_home: user home directory that contains file created by the player.
    config_home = None
    files_home = None

    # TODO: Use Windows and MAC data and config directories.

    # Create user directories using XDG Base Directory Specification
    # For a smooth, trouble-free and most importantly *backward-compatible*
    # the old standard ~/.endgame is always read (created if needed).
    # Otherwise, by default new user directories are used and read first.
    if os.environ.has_key("HOME") and not force_single_dir:

        home = os.environ["HOME"]
        xdg_config_home = os.environ.get('XDG_CONFIG_HOME') or \
                          os.path.join(home, '.config')
        xdg_data_home = os.environ.get('XDG_DATA_HOME') or \
                        os.path.join(home, '.local/share')

        # TODO: Add XDG_*_DIRS to read dirs.

        pref_dir_new = os.path.join(xdg_config_home, "singularity")
        files_dir_new = os.path.join(xdg_data_home,  "singularity")
        dir_old = os.path.join(home, ".endgame")

        read_dirs["old_home"] = [dir_old]
        write_dirs["old_home"] = dir_old
        read_dirs["config_home"] = [pref_dir_new]
        write_dirs["config_home"] = pref_dir_new
        read_dirs["files_home"] = [files_dir_new]
        write_dirs["files_home"] = files_dir_new

    # Now find dirs.
    for defs in dir_defs:
        properties = defs[0]
        name = properties["name"]
        writable = properties.get("writable", False)

        for item in defs[1:]:

            # No parent directory, abort.
            if (item["parent"] not in read_dirs or read_dirs[item["parent"]] is None):
                continue

            parent_dir = read_dirs[item["parent"]][0]
            the_dir = os.path.join(parent_dir, item["path"])

            # Make directory if no writable directory exists.
            if (writable and name not in write_dirs):
                try:
                    makedirs_if_not_exist(the_dir)
                except Exception:
                    # We don't have permission to write here. Abort.
                    continue

            # Must always be a readable directory.
            if not os.path.isdir(the_dir) or not os.access(the_dir, os.R_OK):
                continue

            # Write dir is the first writable dir found.
            if (writable and (name not in write_dirs)
                         and os.access(the_dir, os.W_OK)):
                write_dirs[name] = the_dir

                # Always read writable dir first.
                read_dirs.setdefault(name, []).insert(0, the_dir)
            else:
                read_dirs.setdefault(name, []).append(the_dir)

    dirs_err = False

    # Check if we at least one directory for mandatory.
    for defs in dir_defs:
        properties = defs[0]
        name = properties["name"]

        if (name not in read_dirs and properties.get("mandatory", False)):
            sys.stderr.write("ERROR: No readable directory found for '%s'\n"
                             % (name,))
            dirs_err = True

    if (dirs_err):
        sys.exit(1)

def get_read_dirs(dir_name):
    """ Return a list a readable directories. """
    global read_dirs
    return read_dirs[dir_name]

def get_readable_file_in_dirs(filename, dir_name, outer_paths=None):
    global read_dirs
    dirs = read_dirs[dir_name]

    for read_dir in dirs:
        real_path = os.path.join(read_dir, filename)

        if outer_paths is not None:
            outer_paths.append(real_path)

        if os.path.isfile(real_path):
            return real_path

    return None

def get_write_dir(dir_name):
    """ Return the default writable directory """
    global write_dirs
    return write_dirs[dir_name]

def get_writable_file_in_dirs(filename, dir_name, outer_paths=None):
    global write_dirs
    write_dir = write_dirs[dir_name]

    if (write_dir is not None):
        real_path = os.path.join(write_dir, filename)

        if outer_paths is not None:
            outer_paths.append(real_path)

        return real_path
    else:
        return None

def get_readable_i18n_files(filename, lang=None, default_language=True, outer_paths=None):
    files = []

    lang_list = g.language_searchlist(lang, default=default_language)

    for lang in lang_list:
        i18n_dirs = (os.path.join(d, "lang_" + lang) for d in get_read_dirs("i18n")) \
                    if (lang != g.default_language) else get_read_dirs("data")

        for i18n_dir in i18n_dirs:
            real_path = os.path.join(i18n_dir, filename)

            if outer_paths is not None:
                outer_paths.append(real_path)

            if os.path.isfile(real_path):
                files.append((lang, real_path))

    return files

def makedirs_if_not_exist(directory):
    try:
        os.makedirs(directory, mode=0700)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
