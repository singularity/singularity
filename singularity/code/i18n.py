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

# Candidate for packaging: https://pypi.org/project/van.potomo/
# https://pypi.org/project/zest.pocompile/

try:
    import polib
except ImportError:
    import singularity.code.polib as polib

#Used to determine which data files to load.
#It is required that default language have all data files and all of them
# must have all available entries
default_language = "en_US"
#default_textdomain = 'messages'

# Prepare main locale dir
# TODO put this in the correct dir and do this in the dirs.py script. We need to rename the textdomains first."
main_localedir='singularity/locales'
if not os.path.isdir(main_localedir):
  os.makedirs(main_localedir)

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
    load_data_str()
    load_story_translations()

    #gettext.bindtextdomain('messages', localedir=None)
    gettext.bindtextdomain('messages', main_localedir)

    gettext.install('messages', main_localedir)




def load_messages():
    _load_po_file(g.messages, 'messages.po', use_context=False)


def load_data_str():
    _load_po_file(g.data_strings, 'data_str.po', use_context=True)
    _load_po_file(g.data_strings, 'knowledge.po', use_context=True, clear_translation_table=False)


def load_story_translations():
    _load_po_file(g.story_translations, 'story.po', use_context=True)


def _load_po_file(translation_table, pofilename, use_context=True, clear_translation_table=True):
    if clear_translation_table:
        translation_table.clear()

    files = dirs.get_readable_i18n_files(pofilename, language, default_language=False)

    for lang, pofile in files:
        try:
            po = polib.pofile(pofile) # TODO move this down to mo generation after everything has been redesigned

            # Use hash to check whether the.po file has changed, then generate .mo file as needed
            sha_base_filename = os.path.basename(os.path.dirname(pofile)) + '_' + os.path.basename(pofile)
            sha_filename = dirs.get_writable_file_in_dirs(sha_base_filename + ".sha1", "temp")

            previous_hash = ''
            new_hash = ''
            if os.path.exists(sha_filename):
                with open(sha_filename, 'r') as sha_file:
                    previous_hash = sha_file.read()

            with open(pofile, 'rb') as currentpo:
                new_hash = hashlib.sha1(currentpo.read()).hexdigest()

            # Ensure directory exists before writing
            locale_mo_dir = os.path.join(main_localedir, lang, 'LC_MESSAGES')
            if not os.path.isdir(locale_mo_dir):
                os.makedirs(locale_mo_dir)

            mofile_path = os.path.join(locale_mo_dir, os.path.basename(pofile).split('.')[0] + '.mo')

            # Create MO file and write new hash
            if new_hash != previous_hash or not os.path.exists(mofile_path):
                print("Installing translation file: " + mofile_path)
                po.save_as_mofile(mofile_path)
                with open(sha_filename, 'w') as sha_file:
                    sha_file.write(new_hash)

        except IOError:
            # silently ignore non-existing files
            continue
        for entry in po.translated_entries():
            key = (entry.msgctxt, entry.msgid) if entry.msgctxt and use_context else entry.msgid
            if entry.msgid_plural:
                translation_table[key] = entry.msgstr_plural
            else:
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

# TODO get rid
def translate(string):
    return gettext.gettext(string)
    if string in g.messages: s = g.messages[string]
    else:                    s = string

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

def get_plural_index(number):
    """Hard-coded plural rules.

    Only languages that don't follow the pattern 1, * need to be added here."""

    number = int(number)
    if language == "gd":
        # nplurals=4; plural=(n==1 || n==11) ? 0 : (n==2 || n==12) ? 1 : (n > 2 && n < 20) ? 2 : 3;
        if number == 1 or number == 11:
            return 0
        if number == 2 or number == 12:
            return 1
        if number > 0 and number < 20:
            return 2
        return 3
    elif language == "ru_RU":
        # nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2);
        if number % 10 == 1 and number % 100 != 11:
            return 0
        if number % 10 >= 2 and number % 10 <= 4 and (number % 100 < 10 or number % 100 >= 20):
            return 1
        return 2
    elif number == 1:
        return 0
    else:
        return 1

# TODO get rid
def translate_plural(singular, plural, number, *args, **kwargs):
    if singular in g.messages:
        try:
            s = g.messages[singular][get_plural_index(number)]
        except KeyError:
            sys.stderr.write(
                "Error translating '%s', plural '%s' for number %d in %r:\n  Missing index msgstr[%s] in translation\n"
                % (singular, plural, number, language_searchlist(default=False),
                  get_plural_index(number)))
            if number == 1: # Discard the translation
                s = singular
            else:
                s = plural
    elif number == 1:
        s = singular
    else:
        s = plural
    s = unicode(s).format(number)

    if args or kwargs:
        try:
            # format() is favored over interpolation for 2 reasons:
            # - parsing occurs here, allowing centralized try/except handling
            # - it is the new standard in Python 3
            return unicode(s).format(*args, **kwargs)

        except Exception as reason:
            sys.stderr.write(
                "Error translating '%s' to '%s' with %r,%r in %r:\n%s: %s\n"
                % (singular, s, args, kwargs, language_searchlist(default=False),
                   type(reason).__name__, reason))
            s = singular # Discard the translation

    return s

# Initialization code
try:
    import builtins
except ImportError:
    import __builtin__ as builtins

# TODO use this
#builtins.__dict__['_'] = gettext.gettext
# The official gettext version does not support any additional
# parameters.  We use a lambda to make the signature match the
# official gettext version to ease the transition to it.
builtins.__dict__['_'] = lambda x: translate(x)
# Mark string as translatable but defer translation until later.
builtins.__dict__['N_'] = lambda x: x
