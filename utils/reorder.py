#!/usr/bin/env python
#file: utils/reorder.py
#Copyright (C) 2008 FunnyMan3595
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

#This file contains a script that re-orders .dat files which have been scrambled
#by traduko.
from __future__ import print_function
import re, sys

if len(sys.argv) != 3:
    print("Re-orders a localized .dat file to match the corresponding en_US file.")
    print("Creates a new file with the suffix .reorder.")
    print()
    print("Reorder attempts to avoid losing anything, but USE WITH CAUTION.")
    print("I strongly recommend placing the file under source control BEFORE using this.")
    print()
    print("Run from the data directory.")
    print("Usage: ../utils/reorder.py file_name language")
    print("e.g. ../utils/reorder.py bases de_DE")
    sys.exit(1)

which = sys.argv[1]
lang = sys.argv[2]

section_re = re.compile(r"^\[([^\]]*)]$")
entry_re = re.compile(r"^([^=]*)=.*$")

order_file = open("%s_en_US.dat" % which)
source_file = open("%s_%s.dat" % (which, lang))
dest_file = open("%s_%s.dat.reorder" % (which, lang), "w")

order_lines = order_file.readlines()
source_lines = source_file.readlines()

source_dict = {}
section = None
for line in source_lines:
    pre_comment = line.split("#")[0].strip()
    if pre_comment:
        section_match = section_re.search(pre_comment)
        if section_match:
            section = section_match.groups()[0].strip()
            source_dict[section] = {}
            continue
        if section == None:
            raise SystemExit("Source line appears before any section header: %s" % line)
        entry_match = entry_re.search(pre_comment)
        if entry_match:
            key = entry_match.groups()[0].strip()
            source_dict[section][key] = line
        else:
            raise SystemExit("Source line not understood: %s")

section = None
for line in order_lines:
    pre_comment = line.split("#")[0].strip()
    if pre_comment:
        section_match = section_re.search(pre_comment)
        if section_match:
            if section != None:
                for k, line in source_dict[section].iteritems():
                    dest_file.write(line)
                dest_file.write("\n")
            section = section_match.groups()[0].strip()
            if section not in source_dict:
                raise SystemExit("Order section missing from source: %s" % section)
            dest_file.write(line)
            continue
        if section == None:
            raise SystemExit("Order line appears before any section header: %s" % line)
        entry_match = entry_re.search(pre_comment)
        if entry_match:
            key = entry_match.groups()[0].strip()
            if key not in source_dict[section]:
                raise SystemExit("Order entry missing from source section %s: %s" % (section, key))
            dest_file.write(source_dict[section].pop(key))
        else:
            raise SystemExit("Order line not understood: %s")

if section != None:
    for k, line in source_dict[section].iteritems():
        dest_file.write(line)
    dest_file.write("\n")
