#!/usr/bin/env python
#

import sys
import os.path
from io import open
import ConfigParser

def get_esdir(myname):
    mydir  = os.path.dirname(myname)
    esdir  = os.path.abspath(os.path.join(os.path.dirname(myname), '../..'))
    return esdir

def build_option_parser():
    import argparse

    description = '''Find data strings and save them for translation.'''

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-d", "--directory", dest="directory", default=None,
    help="Use E:S root directory DIR (default dirname(__file__)/../..)", metavar="DIR")
    parser.add_argument("-l", "--lang", dest="lang", default=None,
    help="Add translation for language", metavar="LANG")
    parser.add_argument("-o", "--output", dest="output", default=None,
    help="PO/POT File output", metavar="FILE")

    return parser.parse_args()

def main():
    args = build_option_parser()
    
    global esdir
    if (args.directory):
        esdir = osp.abspath(args.directory)
    else:
        esdir = get_esdir(sys.argv[0])
    
    generate_translations(args.output, args.lang)

def generate_translations(output_file, lang):
    esdir = get_esdir(__file__)
    sys.path.insert(0, esdir)

    try:
        import polib
    except ImportError:
        import singularity.code.polib as polib

    with open(output_file, "w+", encoding='utf-8') as fd:
        fd.write(u"""
# SOME DESCRIPTIVE TITLE.
# Copyright (C) YEAR THE PACKAGE'S COPYRIGHT HOLDER
# This file is distributed under the same license as the singularity package.
# FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.
# 
msgid ""
msgstr ""
"Project-Id-Version: singularity 1\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: 2019-08-21 09:52+0200\\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"
"Language-Team: LANGUAGE <LL@li.org>\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=CHARSET\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Language: \\n"
""")

    po = polib.pofile(output_file)

    datadir = esdir + "/data"
    file_list = os.listdir(datadir)

    for filename in file_list:
        if not filename.endswith("_str.dat"):
            continue
        
        filepath = datadir + "/" +  filename
        
        try:
            fd = open(filepath, encoding='utf-8')
            config = ConfigParser.RawConfigParser()
            config.readfp(fd)
            
            lang_fd = None
            if lang is not None:
                lang_file = esdir + "/i18n/lang_" + lang + "/" + filename
        
                try:
                    lang_fd = open(lang_file, encoding='utf-8')
                    lang_config = ConfigParser.RawConfigParser()
                    lang_config.readfp(lang_fd)
                except Exception:
                    if lang_fd is not None:
                        lang_fd.close()
                    lang_fd = None

            for section_id in config.sections():
                for option in config.options(section_id):
                    ctxt = "[" + section_id + "] " + option
                    text = config.get(section_id, option).strip()
                    
                    entry = po.find(text, msgctxt=ctxt)

                    if not entry:
                        entry = polib.POEntry()
                        po.append(entry)

                    entry.msgid = text
                    entry.msgctxt = ctxt
                    entry.msgstr = ""

                    if lang_fd is not None:
                        try:
                            tr_text = lang_config.get(section_id, option).strip()
                            entry.msgstr = tr_text
                        except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
                            entry.msgstr = ""

        finally:
            if fd is not None:
                fd.close()
            if lang_fd is not None:
                lang_fd.close()


    po.save(output_file)

if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        import traceback
        ex_type, ex, tb = sys.exc_info()
        print(ex)
        traceback.print_tb(tb)
        sys.exit(1)
    except KeyboardInterrupt:
        pass
    except SystemExit as ex:
        raise ex
