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

import os, sys, collections, numbers, itertools, traceback
import g, code.g, dialog

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

    if (not current == None and theme.id != current.id):
        theme.update()
    current = theme

def current_variants():
    variants = [None]

    # Add language variants
    import code.i18n
    lang_list = code.i18n.language_searchlist()
    for lang in lang_list:
        variants.insert(0, lang)

    return variants

class Theme(object):
    def __init__(self, id, dir):
        super(Theme, self).__init__()
        self.id = id
        self.dir = dir
        self._parents = [default_theme] if id != default_theme else []
        self._variants = {}

    def search_variant(self):
        file_list = os.listdir(self.dir)

        # First with None variant.
        yield((None, os.path.join(self.dir, "theme.dat")))

        for filename in file_list:
            (name, ext) = os.path.splitext(filename)

            # We only want theme_*.dat.
            if name.startswith("theme_") and len(name) > 6 and ext in ['.dat']:
                variant = name[6:]

                yield((variant, os.path.join(self.dir, filename)))

    def iter_variants(self):
        """ Iterate through variants."""

        for variant in self._variants:
            yield(self._variants[variant])

    def set_variant(self, variant_theme):
        self._variants[variant_theme.variant] = variant_theme

    def find_files(self):
        """find all files in current theme:
             images in <theme.dir>/images
             fonts in <theme.dir>/fonts
        """

        base_variant = self._variants[None]

        image_dir = os.path.join(self.dir, 'images')
        image_list = os.listdir(image_dir)
        for image_filename in image_list:

            # We only want JPGs and PNGs.
            if os.path.splitext(image_filename)[1].lower() in ['.png', '.jpg']:

                filetitle = os.path.splitext(image_filename)[0]
                base_variant.image_infos[filetitle] = os.path.join(image_dir, image_filename)

        # Add fonts dir
        font_dir = os.path.join(self.dir, "fonts")
        for variant_theme in self.iter_variants():
            for font in variant_theme.font_infos:
                variant_theme.font_infos[font] = os.path.join(font_dir, variant_theme.font_infos[font]) 

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

    def init_cache(self):
        g.images.clear()
        # Manually delete font to avoid the font limitation. 
        for font in g.fonts.itervalues(): del font
        g.fonts.clear()
        g.colors.clear()

        # Iterate from current variants.
        for variant in current_variants():

            # If the variant theme exist...
            if (variant in self._variants):
                self._variants[variant].init_cache()

            # Let's inherit from parents.
            for parent in self.iter_parents():
                if (variant in parent._variants):
                    parent._variants[variant].init_cache()

    def update(self):
        self.init_cache()
        dialog.Dialog.top.needs_reconfig = True

    @property
    def name(self):
        # Iterate from current variants.
        for variant in current_variants():
            if variant in self._variants:
                name = self._variants[variant].name
                if name is not None:
                    return name

        return self.id

class VariantTheme(object):

    def __init__(self, variant):
        self.variant = variant
        self.name = None
        self.image_infos = {}
        self.font_infos = {}
        self.color_infos = {}

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
        # Only set if the previous variant themes or parents didn't.

        # Set images
        for image_name, image_filename in self.image_infos.iteritems():
            if (image_name not in g.images):
                g.images[image_name] = g.load_image(image_filename)

        # Set font
        for font_name, font_filename in self.font_infos.iteritems():
            if (font_name not in g.fonts):
                g.fonts[font_name] = g.load_font(font_filename)

        # Set colors
        for color_name, color in self.color_infos.iteritems():
            if (color_name not in g.colors):
                g.colors[color_name] = color
