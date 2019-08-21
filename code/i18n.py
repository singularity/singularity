#file: i18n.py
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

#This file contains all functions to internationalize and localize the 
#application.
#
#IMPORTANT: A portion of translation is still done with data files in g.

from __future__ import absolute_import

import os
import sys
import locale

from code import g, polib, dirs
from code.pycompat import *


#Used to determine which data files to load.
#It is required that default language have all data files and all of them
# must have all available entries
default_language = "en_US"
try:
    language = locale.getdefaultlocale()[0] or default_language
except RuntimeError:
    language = default_language


def set_language(lang=None, force=False):
    global language # required, since we're going to change it
    if lang is None: lang = language

    if lang == language and not force:
        return

    langs = available_languages()
    if lang in langs:
        language = lang
    else:
        # Let's try to be smart: if base language exists for another for another
        # country, use it. So es_ES => es_AR, pt_PT => pt_BR, etc
        code = lang.split("_")[0]
        languages = [ l for l in langs if code == l.split("_")[0] ]
        if len(languages) > 0:
            language = languages[0]
        else:
            language = default_language

    # Try a few locale settings. First the selected language, then the user's
    # default, then default language. Languages are tried with UTF-8 encoding
    # first, then the default encoding. The user's default language is not
    # paired with UTF-8.
    # If all of that fails, we hope locale magically does the right thing.
    for attempt in [ language + ".UTF-8",
                     language,
                     "",
                     default_language + ".UTF-8",
                     default_language]:
        try:
            locale.setlocale(locale.LC_ALL, attempt)
            break
        except locale.Error:
            continue

    load_messages()

def load_messages(lang=None):
    if lang is None: lang = language

    g.messages.clear()

    files = dirs.get_readable_i18n_files("messages.po", lang, default_language=False)

    for lang, pofile in files:
        try:
            po = polib.pofile(pofile)
            for entry in po.translated_entries():
                g.messages[entry.msgid] = entry.msgstr
        except IOError: pass # silently ignore non-existing files

def available_languages():
    return [default_language] + \
           [file_name[5:] for file_dir in dirs.get_read_dirs("i18n")
                          if os.path.isdir(file_dir)
                          for file_name in os.listdir(file_dir)
                          if os.path.isdir(os.path.join(file_dir, file_name))
                             and file_name.startswith("lang_")]

def language_searchlist(lang=None, default=True):
    if lang is None: lang = language

    # if lang is in ll_CC format (language_COUNTRY, like en_US), add both ll
    # and ll_CC, in that order, so all generic language entries are loaded first
    # and then overwritten by any country-specific ones
    lang_list = [ lang ]
    if "_" in lang: lang_list.insert(0, lang.split("_",1)[0])

    # If requested and not already in list, add default language as first,
    # so it acts as a fallback and is overwritten with any available entries
    # in the native language
    if default and default_language not in lang_list:
        lang_list.insert(0, default_language)

    return lang_list

def translate(string, *args, **kwargs):
    if   string in g.buttons : s = g.buttons[string]
    elif string in g.messages: s = g.messages[string]
    else:                      s = string

    if args or kwargs:
        try:
            # format() is favored over interpolation for 2 reasons:
            # - parsing occurs here, allowing centralized try/except handling
            # - it is the new standard in Python 3
            return unicode(s).format(*args, **kwargs)

        except Exception as reason:
            sys.stderr.write(
                "Error translating '%s' to '%s' with %r,%r in %r:\n%s: %s\n"
                % (string, s, args, kwargs, language_searchlist(default=False),
                   type(reason).__name__, reason))
            s = string # Discard the translation

    return s

# Initialization code
try:
    import builtins
except ImportError:
    import __builtin__ as builtins

builtins.__dict__['_'] = translate

