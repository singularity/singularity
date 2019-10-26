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

from __future__ import absolute_import

import os
import sys
import errno


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
        {"parent": "files_home",        "path": "i18n",           }, # New XDG dir
        {"parent": "unix_files_home",   "path": "music",          },
        {"parent": "root",              "path": "i18n",           },
    ),
    ( {"name":"music", },
        {"parent": "files_home",        "path": "music",          }, 
        {"parent": "unix_files_home",   "path": "music",          },
        {"parent": "old_home",          "path": "music",          }, # Old .endgame dir
        {"parent": "root",              "path": "music",          },
    ),
    ( {"name":"sounds", },
        {"parent": "data",        "path": "sounds"          },
    ),
    ( {"name":"themes", "mandatory": True, "writable": True},
        {"parent": "files_home",        "path": "themes",         }, # New XDG dir
        {"parent": "unix_files_home",   "path": "themes",         }, # New XDG dir
        {"parent": "data",              "path": "themes",         },
    ),
    ( {"name":"saves", "writable": True},
        {"parent": "files_home",        "path": "saves",          }, # New XDG dir
        {"parent": "unix_files_home",   "path": "saves",          }, # New XDG dir
        {"parent": "config_home",       "path": "saves",          },
        {"parent": "unix_config_home",  "path": "saves",          }, # New XDG dir
        {"parent": "old_home",          "path": "saves",          }, # Old .endgame dir
        {"parent": "root",              "path": "saves",          }, # Single dir
    ),
    ( {"name":"pref", "writable": True},
        {"parent": "config_home",       "path": version_dir,      },
        {"parent": "unix_config_home",  "path": version_dir,      },
        {"parent": "config_home",       "path": "",               },
        {"parent": "unix_config_home",  "path": "",               },
        {"parent": "old_home",          "path": "",               }, # Old .endgame dir
        {"parent": "root",              "path": "",               }, # Single dir
    ),
    ( {"name":"log", "writable": True},
        {"parent": "vars_home",         "path": "log",            }, 
        {"parent": "unix_vars_home",    "path": "log",            }, 
        {"parent": "files_home",        "path": "log",            }, 
        {"parent": "unix_files_home",   "path": "log",            }, 
        {"parent": "unix_config_home",  "path": "log",            }, 
        {"parent": "old_home",          "path": "log",            }, # Old .endgame dir
        {"parent": "root",              "path": "log",            }, # Single dir
    ),
)

dirs_errs = []

def create_directories(force_single_dir):

    system = sys.platform

    # root dir: the install directory for E:S.
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    read_dirs["root"] = [root_dir]
    write_dirs["root"] = root_dir

    # config_home: user home directory that contains configuration.
    # file_home: user home directory that contains file created by the player.
    # vars_home: user home directory that contains file used by the program.

    if system == "win32" and not force_single_dir:
        
        # Create user directories using MSDN Specification.
        # See get_win_folder comments for more information.
        appdirs = get_win_folders()
        
        if (appdirs):
            roaming_appdir, local_appdir = appdirs

            roaming_dir_new = os.path.join(roaming_appdir, "singularity")
            local_dir_new = os.path.join(local_appdir,  "singularity")

            read_dirs["config_home"] = [local_dir_new]
            write_dirs["config_home"] = local_dir_new
            read_dirs["files_home"] = [roaming_dir_new]
            write_dirs["files_home"] = roaming_dir_new
            read_dirs["vars_home"] = [local_dir_new]
            write_dirs["vars_home"] = local_dir_new

    if system == 'darwin' and not force_single_dir:
        # Create user directories using File System Programming Guide.
        # See get_mac_library comments for more information.
        library = get_mac_library()
            
        if (library):
            library_dir_new = os.path.join(library, "singularity")
            
            read_dirs["config_home"] = [library_dir_new]
            write_dirs["config_home"] = library_dir_new
            read_dirs["files_home"] = [library_dir_new]
            write_dirs["files_home"] = library_dir_new
            read_dirs["vars_home"] = [library_dir_new]
            write_dirs["vars_home"] = library_dir_new

    # Always use unix path as fallback if HOME is present.
    if os.environ.has_key("HOME") and not force_single_dir:

        # Create user directories using XDG Base Directory Specification
        # For a smooth, trouble-free and most importantly *backward-compatible*
        # the old standard ~/.endgame is always read (created if needed).
        # Otherwise, by default new user directories are used and read first.

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
        read_dirs["unix_config_home"] = [pref_dir_new]
        write_dirs["unix_config_home"] = pref_dir_new
        read_dirs["unix_files_home"] = [files_dir_new]
        write_dirs["unix_files_home"] = files_dir_new
        read_dirs["unix_vars_home"] = [files_dir_new]
        write_dirs["unix_vars_home"] = files_dir_new

    # Now find dirs.
    for defs in dir_defs:
        properties = defs[0]
        name = properties["name"]
        writable = properties.get("writable", False)

        # Always set a default empty dirs list.
        read_dirs.setdefault(name, [])

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
                read_dirs[name].insert(0, the_dir)
            else:
                read_dirs[name].append(the_dir)

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

def get_readable_i18n_files(filename, lang=None, default_language=True, 
        localized_item=True, only_last=False, outer_paths=None):
    from code import i18n
    files = []

    lang_list = i18n.language_searchlist(lang, default=default_language)

    for lang in lang_list:
        i18n_dirs = (os.path.join(d, "lang_" + lang) for d in get_read_dirs("i18n")) \
                    if (lang != i18n.default_language) else get_read_dirs("data")

        for i18n_dir in i18n_dirs:
            real_path = os.path.join(i18n_dir, filename)

            if outer_paths is not None:
                outer_paths.append(real_path)

            if os.path.isfile(real_path):
                if localized_item:
                    files.append((lang, real_path))
                else:
                    files.append(real_path)

    if (only_last):
        return files[-1]
    else:
        return files

def makedirs_if_not_exist(directory):
    try:
        os.makedirs(directory, mode=0o0700)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

def get_csidl(app_dir):
    if app_dir == "local":
        return 28 # CSIDL_LOCAL_APPDATA roaming app data
    if app_dir == "roaming":
        return 26 # CSIDL_APPDATA non-roaming app data
    if app_dir == "home":
        return 26 # CSIDL_PERSONAL non-roaming app data
        
class GUID(ctypes.Structure):   # [1]
    _fields_ = [
        ("Data1", wintypes.DWORD),
        ("Data2", wintypes.WORD),
        ("Data3", wintypes.WORD),
        ("Data4", wintypes.BYTE * 8)
    ] 

    def __init__(self, l, w1, w2, b):
        self.Data1 = l
        self.Data2 = w1
        self.Data3 = w2
        self.Data4[:] = tuple((b & (0xff << pos * 8)) >> pos * 8 for pos in range(7, -1, -1))
        

def get_folder_id(app_dir):
    if app_dir == "local":
        return GUID(0xF1B32785, 0x6FBA, 0x4FCF, 0x9D557B8E7F157091) # non-roaming app data
    if app_dir == "roaming":
        return GUID(0x3EB685DB, 0x65F9, 0x4CF6, 0xA03AE3EF65729F3D) # roaming app data
    if app_dir == "home":
        return GUID(0x5E6C858F, 0x0E22, 0x4760, 0x9AFEEA3317B67173) # profile dir

shell32_function = (
    'SHGetKnownFolderPath'
    'SHGetFolderPathW'
    'SHGetFolderPathA'
    'SHGetSpecialFolderPathW'
    'SHGetSpecialFolderPathA'
)

def shell32_SHGetKnownFolderPath(func, app_dir):
    buf = ctypes.c_wchar_p()
    if func(ctypes.byref(ctypes.byref(get_folder_id(app_dir))), 0, 0, ctypes.byref(buf)):
        return buf.value
    return None

def shell32_SHGetFolderPathW(func, app_dir):
    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH + 1)
    if func(0, get_csidl(app_dir), 0 """SHGFP_TYPE_CURRENT""", buf):
        return buf.value
    return None

def shell32_SHGetFolderPathA(func, app_dir):
    buf = ctypes.create_string_buffer(ctypes.wintypes.MAX_PATH + 1)
    if func(0, get_csidl(app_dir), 0 """SHGFP_TYPE_CURRENT""", buf)):
        return buf.value
    return None

def shell32_SHGetSpecialFolderPathW(func, app_dir):
    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH + 1)
    if func(0, buf, get_csidl(app_dir), True):
        return buf.value
    return None

def shell32_SHGetSpecialFolderPathA(func, app_dir):
    buf = ctypes.create_string_buffer(ctypes.wintypes.MAX_PATH + 1)
    if (func(0, buf, get_csidl(app_dir), True)):
        return buf.value
    return None

def get_win_folders():

    # First try to import ctypes to call c win32 function.
    # win32 function is the correct way to get win folder.
    # but python is not shipped on windows with pywin32
    # Let's do the hard way.
    try:
        import ctypes
        import ctypes.wintypes
    except:
        if g.debug: sys.stderr.write("WARNING: Impossible to load ctypes modules\n")

    if 'ctypes' in sys.modules:
        for func_name in win32_function:
            try:
                func = ctypes.windll.shell32.getattr(func_name)
                
                handler = globals().get("shell32_%s" % func_name)
                
                local_appdir = handler(func, 'local')
                roaming_appdir = handler(func, 'roaming')
                
                if (roaming_appdir is not None and local_appdir is not None)
                    return (roaming_appdir, local_appdir)
                else:
                    if g.debug: sys.stderr.write("WARNING: '%s' shell32 function fails for local and roaming\n" % func_name)
            except:
                if g.debug: sys.stderr.write("WARNING: Impossible to use '%s' shell32 function\n" % func_name)

    # ctypes doesn't work, let find the APPDATA environnement variables.
    if os.environ.has_key("APPDATA") and os.environ.has_key("LOCALAPPDATA"):
        
        local_appdir = os.environ.has_key("LOCALAPPDATA")
        roaming_appdir = os.environ.has_key("APPDATA")

        return (roaming_appdir, local_appdir)
    else:
        if g.debug: sys.stderr.write("WARNING: APPDATA and LOCALAPPDATA environment not present \n")

    # Ok, we could try to get home user directories.
    # Get it to all different way.
    home_dirs = []

    if 'ctypes' in sys.modules:
        for func_name in win32_function:
            try:
                func = ctypes.windll.shell32.getattr(func_name)
                
                handler = globals().get("shell32_%s" % func_name)
                
                profiledir = handler(func, 'home')
                
                if profiledir is not None:
                    home_dirs.append(profiledir)
                else:
                    if g.debug: sys.stderr.write("WARNING: '%s' shell32 function fails for home\n" % func_name)
            except:
                if g.debug: sys.stderr.write("WARNING: Impossible to use '%s' shell32 function for home\n" % func_name)

    if os.environ.has_key("USERPROFILE")
        home_dirs.append(os.environ.get("USERPROFILE"))
    else:
        if g.debug: sys.stderr.write("WARNING: USERPROFILE environment not present \n")

    if os.environ.has_key("HOMEPATH") and os.environ.has_key("HOMEDRIVE")
        home_dirs.append(os.environ.get("HOMEDRIVE") + os.environ.get("HOMEPATH"))
    else:
        if g.debug: sys.stderr.write("WARNING: HOMEPATH and HOMEDRIVE environment not present \n")

    if os.environ.has_key("USERNAME")
        home_dirs.append("C:\\Users\\" + os.environ.get("USERNAME"))
        home_dirs.append("C:\\Documents and Settings\\" + os.environ.get("USERNAME"))
    else:
        if g.debug: sys.stderr.write("WARNING: USERNAME environment not present \n")

    # Now we can check if we find AppData.
    for home in home_dirs:
        local_appdir = os.path.join(home, "AppData", "Local")
        roaming_appdir = os.path.join(home, "AppData", "Roaming")
    
        if (os.path.is_dir(local_appdir) and os.path.is_dir(roaming_appdir))
            return (roaming_appdir, local_appdir)

    # We can check the old ApplicationData
    for home in home_dirs:
        appdir = os.path.join(home, "Application Data")
    
        if (os.path.is_dir(appdir))
            return (appdir, appdir)

    # Ok, let just use the user directory.
    for home in home_dirs:
        if (os.path.is_dir(home))
            return (home, home)

    # Now, next we could be check the registry.
    # But it's not good idea.
    # 1) Registry shell32 are considered as unreliable
    # 2) If we can't use win32 for shell32, why could we use it for registry ?

    return False

def get_mac_library():
    
    try:
        import ctypes
        import ctypes.util
    except:
        if g.debug: sys.stderr.write("WARNING: Impossible to load ctypes modules\n")

    if 'ctypes' in sys.modules:
        try:
            NSApplicationSupportDirectory = 14
            NSUserDomainMask = 1
            
            Foundation = ctypes.cdll.LoadLibrary("Foundation.framework/Foundation")
            CoreFoundation = ctypes.cdll.LoadLibrary("CoreFoundation.framework/CoreFoundation");

            NSSearchPathForDirectoriesInDomains = Foundation.NSSearchPathForDirectoriesInDomains
            CFRelease = CoreFoundation.CFRelease
            CFArrayGetCount = CoreFoundation.CFArrayGetCount
            CFArrayGetValueAtIndex = CoreFoundation.CFArrayGetValueAtIndex
            CFStringGetLength = CoreFoundation.CFStringGetLength
            CFStringGetMaximumSizeForEncoding = CoreFoundation.CFStringGetMaximumSizeForEncoding
            CFStringGetCString = CoreFoundation.CFStringGetCString

            kCFStringEncodingUTF8 = 0x08000100

            result = False

            paths = NSSearchPathForDirectoriesInDomains(directory, domainMask, expand)

            if paths and CFArrayGetCount(paths) > 0:
                # TODO: Use all search paths found.

                path = CFArrayGetValueAtIndex(paths, 0)

                length = CFStringGetLength(path);
                maxSize = CFStringGetMaximumSizeForEncoding(length, kCFStringEncodingUTF8) + 1;

                buf = create_string_buffer(maxSize)
                if CFStringGetCString(path, buf, sizeof(buf), kCFStringEncodingUTF8):
                    result = buf.raw.decode('utf-8').rstrip('\0')
                del buf

            CFRelease(paths)

            if result: return result
            if g.debug: sys.stderr.write("WARNING: '%s' fondation function fails for library\n" % func_name)
        except:
            if g.debug: sys.stderr.write("WARNING: Impossible to use '%s' fondation function\n" % func_name)

    # Only fallback is hardcoded dir in HOME
    if os.environ.has_key("HOME"):
        return os.path.join(os.environ.get("HOME"), "Library", "Application Support")

    return False
