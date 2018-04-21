#file: theme.py
#Copyright (C) 2005,2006,2008 Evil Mr Henry, Phil Bordelon, and FunnyMan3595
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

#This file contains the theme class.

import g, code.g
import sys, collections, numbers, itertools, traceback

default_theme = 'default'

current = None
themes = collections.OrderedDict()

def get_theme_list():
    return [themes[k].name for k in themes]

def get_theme_pos():
    return (i[0] for i in enumerate(themes) if i[1] == current).next()

def set_theme(key):
    global current
    theme = None

    if isinstance(key, numbers.Number):
        try:
            theme = next(itertools.islice(themes.itervalues(), key, key + 1))
        except StopIteration:
            pass

    elif isinstance(key, basestring):
        try:
            theme = themes[key]
        except KeyError:
            pass

    elif key is None:
        theme = themes[default_theme]

    if theme is None:
        sys.stderr.write("WARNING: The key '%s' does not exist in theme dictionnary. Use default theme.\n" % key)
        theme = themes[default_theme]

    if theme.id != current:
        if not current == None:
            theme.update()
        current = theme.id

class Theme(object):
    def __init__(self, id):
        super(Theme, self).__init__()
        self.id = id

    def update(self):
        g.load_images(code.g.data_dir)
        # TODO: Theme should not call map_screen directly.
        code.g.map_screen.on_theme()



