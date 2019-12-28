#!/usr/bin/env python
#

import sys
import os.path
from io import open
from singularity.code.pycompat import *

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
    generator = generate_data_str_translations()
    write_po_file(generator, args.output)


def write_po_file(po_entries, output_file):

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
"Language: \\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=CHARSET\\n"
"Content-Transfer-Encoding: 8bit\\n"
""")

    po = polib.pofile(output_file)
    for text, ctxt in po_entries:
        entry = po.find(text, msgctxt=ctxt)

        if not entry:
            entry = polib.POEntry()
            po.append(entry)

        entry.msgid = text
        entry.msgctxt = ctxt
        entry.msgstr = ""

    po.save(output_file)


def generate_data_str_translations():
    esdir = get_esdir(__file__)

    datadir = os.path.join(esdir, "singularity", "data")
    file_list = os.listdir(datadir)

    for filename in sorted(file_list):
        if not filename.endswith("_str.dat"):
            continue
        
        filepath = os.path.join(datadir, filename)

        with open(filepath, encoding='utf-8') as fd:
            config = RawConfigParser()
            config.read_file(fd)

            for section_id in config.sections():
                for option in config.options(section_id):
                    ctxt = "[" + section_id + "] " + option
                    text = config.get(section_id, option).strip()
                    yield (text, ctxt)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
