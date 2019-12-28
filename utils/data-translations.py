#!/usr/bin/env python
#

import sys
import os.path
from io import open
import ConfigParser

try:
    import polib
except ImportError:
    import singularity.code.polib as polib


def get_esdir(myname):
    esdir = os.path.abspath(os.path.dirname(os.path.dirname(myname)))
    return esdir


def build_option_parser():
    import argparse

    description = '''Find data strings and save them for translation.'''

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-o", "--output", dest="output", default=None,
                        help="PO/POT File output", metavar="FILE")

    return parser.parse_args()


def main():
    args = build_option_parser()
    generate_translations(args.output)


def generate_translations(output_file):
    esdir = get_esdir(__file__)

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

    datadir = os.path.join(esdir, "singularity", "data")
    file_list = os.listdir(datadir)

    for filename in sorted(file_list):
        if not filename.endswith("_str.dat"):
            continue
        
        filepath = os.path.join(datadir, filename)

        with open(filepath, encoding='utf-8') as fd:
            config = ConfigParser.RawConfigParser()
            config.readfp(fd)

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

    po.save(output_file)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
