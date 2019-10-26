#file: prerequisite.py
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

#This file contains the Prequisite class.

from __future__ import absolute_import

from singularity.code import g


class Prerequisite(object):

    def __init__(self, prerequisites):
        self.prerequisites = prerequisites

    def available(self):
        or_mode = False
        assert type(self.prerequisites) == list
        for index, prerequisite in enumerate(self.prerequisites):
            if prerequisite == "impossible":
                assert len(self.prerequisites) == 1
                return False
            if prerequisite == "OR":
                assert index == 0
                or_mode = True
            if prerequisite in g.pl.techs and g.pl.techs[prerequisite].done:
                if or_mode:
                    return True
            else:
                if not or_mode:
                    return False
        # If we're not in OR mode, we met all our prerequisites.  If we are, we
        # didn't meet any of the OR prerequisites.
        return not or_mode

    def prerequisites_in_cnf_format(self):
        """Transform the Prerequisites into Conjunctive Normal Form (CNF)

        This is mostly useful for unit tests.  A quick primer on CNF form is:

            { {X}, {Y1, Y2}, {Z} } is read as (X) AND (Y1 OR Y2) AND (Z)

        Special cases used here:
            * None implies that there is no solution (only happens if the
              data file uses "impossible"
            * Empty (outer) set implies no prerequisites.

        Note that the dependency format of singularity's data files currently
        only support simple relations that are always AND'ed or always OR'ed
        together.

        :return: None if the prerequisites is explicitly marked "impossible".
        Otherwise, a set of sets that denote the dependencies required to
        satisfy this prerequisite.  If the outer set is empty set, then
        there are no prerequisites for this instance.
        """
        # Format: { {X}, {Y1, Y2}, {Z} } => (X) AND (Y1 OR Y2) AND (Z)
        if len(self.prerequisites) == 0:
            return frozenset()
        if self.prerequisites[0] == 'impossible':
            return None
        if self.prerequisites[0] == 'OR':
            return frozenset([frozenset(x for x in self.prerequisites[1:])])
        return frozenset(frozenset([x]) for x in self.prerequisites)
