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
import os, sys, collections, numbers, itertools, traceback

default_theme = 'default'

current = None
themes = collections.OrderedDict()

def get_theme_list():
    return [themes[k].name for k in themes]

def get_theme_pos():
    return (i[0] for i in enumerate(themes) if i[1] == current.id).next()

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
        current = theme

class Theme(object):
    def __init__(self, id, dir):
        super(Theme, self).__init__()
        self.id = id
        self.dir = dir
        self.name = ""
        self._parents = [default_theme] if id != default_theme else []
        self.image_infos = {}
        self.font_infos = {}
        self.color_infos = {}

    def find_files(self):
        """find all files in current theme:
             images in <theme.dir>/images
             fonts in <theme.dir>/fonts
        """

        image_dir = os.path.join(self.dir, 'images')
        image_list = os.listdir(image_dir)
        for image_filename in image_list:

            # We only want JPGs and PNGs.
            if os.path.splitext(image_filename)[1].lower() in ['.png', '.jpg']:

                filetitle = os.path.splitext(image_filename)[0]
                self.image_infos[filetitle] = os.path.join(image_dir, image_filename)

        # Add fonts dir
        font_dir = os.path.join(self.dir, "fonts")
        for font in self.font_infos:
            self.font_infos[font] = os.path.join(font_dir, self.font_infos[font]) 

    def inherit(self, *args):
        for arg in args:
            if (type(arg) == list):
                self._parents.extend(arg)
            else:
                self._parents.append(arg)

        # Remove duplicate parent.
        list(dict.fromkeys(self._parents))

        # TODO: Detect cycling inheritance.

    @property
    def parents(self):
        return self._parents

    def iter_parents(self):
        """ Iterate through parents and ancestors.
            Always return parent's parent before next parent in line.
            
            Note: This function needs no cycling exists between parents.
        """
        for parent_id in self._parents:
            parent = themes[parent_id]
            yield(parent)
            for ancestor in parent.iter_parents():
                yield(ancestor)

    def set_font(self, font_name, value):
        self.font_infos[font_name] = value

    def set_color(self, color_name, value):
        if (value.startswith('#')):
            h = value.lstrip('#')
            rgba = tuple(int(h[i:i+2], 16) for i in (0, 2, 4, 6))
            self.color_infos[color_name] = rgba
        else:
            # Alias color.
            self.color_infos[color_name] = value

    def init_cache(self):
        g.images.clear()
        g.fonts.clear()
        g.colors.clear()

        # Load images from self
        for image_name, image_filename in self.image_infos.iteritems():
            g.images[image_name] = g.load_image(image_filename)

        # Let's inherit images from parents.
        # Only set the image if the theme or previous parents didn't.
        for parent in self.iter_parents():
            for image_name, image_filename in parent.image_infos.iteritems():
                if (image_name not in g.images):
                    g.images[image_name] = g.load_image(image_filename)

        for image_name, image_filename in self.image_infos.iteritems():
            g.images[image_name] = g.load_image(image_filename)

        # Load font from self
        for font_name, font_filename in self.font_infos.iteritems():
            g.fonts[font_name] = g.load_font(font_filename)

        # Let's inherit fonts from parents.
        # Only set the font if the theme or previous parents didn't.
        for parent in self.iter_parents():
            for font_name, font_filename in parent.font_infos.iteritems():
                if (font_name not in g.fonts):
                    g.fonts[font_name] = g.load_font(font_filename)

        # Update colors from self
        for color_name, color in self.color_infos.iteritems():
            g.colors[color_name] = color

        # Let's inherit colors from parents.
        # Only set the color if the theme or previous parents didn't.
        for parent in self.iter_parents():
            for color_name, color in parent.color_infos.iteritems():
                if (color_name not in g.fonts):
                    g.colors[color_name] = color

        # Resolve aliased colors
        for color_name, color in g.colors.iteritems():
            g.colors[color_name] = g.resolve_color_alias(color)

    def update(self):
        self.init_cache()
        # TODO: Theme should not call map_screen directly.
        code.g.map_screen.on_theme()
    
