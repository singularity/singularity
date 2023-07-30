# file: knowledge.py
# Copyright (C) 2020 Niels Thykier
# This file is part of Endgame: Singularity.

# Endgame: Singularity is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# Endgame: Singularity is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Endgame: Singularity; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

# This file contains the Knowledge class.
from singularity.code.data import get_def_translation


class KnowledgeArea(object):
    def __init__(self, id, name, help_entries):
        self.id = id
        self.untranslated_name = name
        self.help_entries = help_entries

    @property
    def name(self):
        return get_def_translation(self.id, "name", self.untranslated_name)


class KnowledgeHelpEntry(object):
    def __init__(self, parent_id, id, name, description):
        self.parent_id = parent_id
        self.id = id
        self.untranslated_name = name
        self.untranslated_description = description

    @property
    def _full_id(self):
        return "%s/%s" % (self.parent_id, self.id)

    @property
    def name(self):
        return get_def_translation(self._full_id, "name", self.untranslated_name)

    @property
    def description(self):
        return get_def_translation(
            self._full_id, "description", self.untranslated_description
        )
