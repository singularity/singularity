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

import hashlib
import gettext
import os
import sys
import locale

from singularity.code import g, dirs
from singularity.code.pycompat import *

try:
    import polib
except ImportError:
    import singularity.code.polib as polib

#Used to determine which data files to load.
#It is required that default language have all data files and all of them
# must have all available entries
default_language = "en_US"

gettext_language = None

# Prepare main locale dir
main_localedir = None

# We have to use lazy initialization, otherwise the tests will break
def _get_main_localedir():
    global main_localedir
    if main_localedir is None:
        main_localedir = dirs.get_writable_file_in_dirs('locale', 'i18n')
    return main_localedir


TEXTDOMAIN_PREFIX = 'singularity_'

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

    load_data_str()
    load_story_translations()

    _load_mo_file('messages.po')

    # Switch gettext language
    gettext_language = gettext.translation(TEXTDOMAIN_PREFIX + 'messages', _get_main_localedir(), languages=[lang], fallback=True)
    gettext_language.install()

    # Update builtins with the new language
    builtins.__dict__['_'] = gettext_language.gettext
    builtins.__dict__['ngettext'] = gettext_language.ngettext

    # Define available text domains
    # Since pgettext is only available from Python 3.8 onwards, we use our own custom code for the data translations.
    # https://bugs.python.org/issue2504
    gettext.bindtextdomain(TEXTDOMAIN_PREFIX + 'messages', main_localedir)


def _load_mo_file(pofilename):

    files = dirs.get_readable_i18n_files(pofilename, language, default_language=False)

    for lang, pofile in files:
        try:
            po = polib.pofile(pofile)

            # Use hash to check whether the.po file has changed, then generate .mo file as needed
            sha_base_filename = os.path.basename(os.path.dirname(pofile)) + '_' + os.path.basename(pofile)
            sha_filename = dirs.get_writable_file_in_dirs(sha_base_filename + ".sha1", "i18n")

            previous_hash = ''
            new_hash = ''
            if os.path.exists(sha_filename):
                with open(sha_filename, 'r') as sha_file:
                    previous_hash = sha_file.read()

            with open(pofile, 'rb') as currentpo:
                new_hash = hashlib.sha1(currentpo.read()).hexdigest()

            # Ensure directory exists before writing
            locale_mo_dir = os.path.join(_get_main_localedir(), lang, 'LC_MESSAGES')
            if not os.path.isdir(locale_mo_dir):
                os.makedirs(locale_mo_dir)

            mofile_path = os.path.join(locale_mo_dir, TEXTDOMAIN_PREFIX + os.path.basename(pofile).split('.')[0] + '.mo')

            # Create MO file and write new hash
            if new_hash != previous_hash or not os.path.exists(mofile_path):
                print("Installing translation file: " + mofile_path)
                po.save_as_mofile(mofile_path)
                with open(sha_filename, 'w') as sha_file:
                    sha_file.write(new_hash)

        except IOError:
            # silently ignore non-existing files
            continue


def load_data_str():
    _load_po_file(g.data_strings, 'data_str.po', use_context=True)
    _load_po_file(g.data_strings, 'knowledge.po', use_context=True, clear_translation_table=False)


def load_story_translations():
    _load_po_file(g.story_translations, 'story.po', use_context=True)


# There's no pgettext available for Python < 3.8,
# so we use custom code for data translations
def _load_po_file(translation_table, pofilename, use_context=True, clear_translation_table=True):
    if clear_translation_table:
        translation_table.clear()

    files = dirs.get_readable_i18n_files(pofilename, language, default_language=False)

    for lang, pofile in files:
        try:
            po = polib.pofile(pofile)
        except IOError:
            # silently ignore non-existing files
            continue
        for entry in po.translated_entries():
            key = (entry.msgctxt, entry.msgid) if entry.msgctxt and use_context else entry.msgid
            translation_table[key] = entry.msgstr



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


def lex_sorting_form(name):
    """For lexicographic sorting when languages use characters not in 7-bit ASCII. e.g. é or ü.

    Use like this:

    listdata.sort(key=lambda an_object: i18n.lex_sorting_form(an_object.name))"""

    # Collator returns wrong keys for DE locale
    if language == 'de' or language.startswith('de_'):
        name = name.replace('Ä', 'Ae').replace('ä', 'ae').replace('Ö', 'Oe').replace('ö', 'oe').replace('Ü', 'Ue').replace('ü', 'ue')

    return locale.strxfrm(name)

# Initialization code
try:
    import builtins
except ImportError:
    import __builtin__ as builtins
builtins.__dict__['_'] = gettext.gettext
builtins.__dict__['ngettext'] = gettext.ngettext
# Mark string as translatable but defer translation until later.
builtins.__dict__['N_'] = lambda x: x
