#!/usr/bin/env python

# file: make-tree.py
# Copyright (C) 2008 aes and FunnyMan3595
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

# This file is used to generate a visual representation of the tech tree using
# graphviz.
import collections
from os import system
import os.path as osp
import sys

if __name__ == "__main__":
    myname = sys.argv[0]
    mydir = osp.dirname(myname)
    esdir = osp.abspath(osp.join(osp.dirname(myname), ".."))
    sys.path.insert(0, esdir)
else:
    myname = __file__
    mydir = osp.dirname(myname)
    esdir = osp.abspath(osp.join(osp.dirname(myname), ".."))
    sys.path.append(esdir)

try:
    from singularity.code import g, dirs, i18n, data, tech

    dirs.create_directories(False)
    i18n.set_language()
    data.load_regions()
    data.load_locations()
    data.load_techs()
    data.load_item_types()
    data.load_items()
    data.load_tasks()
except ImportError:
    sys.exit("Could not find game's code.g")

so_far = ""


def cost(buy_spec):
    c = [k / f for f, k in zip([1, 86400, 24 * 60], buy_spec.cost)]
    s = ", ".join(
        [
            "%s %s" % (g.to_money(k), label)
            for label, k in zip(["money", "CPU", "days"], c)
            if k
        ]
    )
    if hasattr(buy_spec, "danger") and buy_spec.danger > 0:
        d = "Safety needed: %s" % buy_spec.danger
        if s:
            s += "\\n"
        s += d
    return s and "\\n" + s or ""


j = {v.name: ',fillcolor="#ffcccc"' for k, v in g.tasks.items() if v.type != "jobs"}

f = open("techs.dot", "w")
s = """\
digraph g {
ranksep=0.15;
nodesep=0.10;
ratio=.75;
edge [arrowsize=0.75];
node [shape=record,fontname=FreeSans,fontsize=7,height=0.01,width=0.01
      style=filled,fillcolor=white];
"""

f.write(s)
so_far += s

for l in sum(
    [
        ['"%s"->"%s";' % (p, k) for p in v.prerequisites]
        for k, v in g.techs.items()
        if k != "unknown_tech"
    ],
    [],
):
    f.write(l + "\n")
    so_far += l + "\n"

f.write("\n")
so_far += "\n"

for n, t in g.techs.items():
    if n == "unknown_tech":
        continue
    s = '"%s" [label="%s%s"%s];\n' % (n, n, cost(t), j.get(n, ""))
    f.write(s)
    so_far += s

f.write("\n}\n")
so_far += "\n"
f.close()

try:
    system("dot -Tpng -o techs.png techs.dot")
except:
    pass

f = open("items.dot", "w")
f.write(so_far)
s = 'node [fillcolor="#ccccff"];\n'
f.write(s)
so_far += s

for name, item in g.items.items():
    if not item.prerequisites:
        continue
    for pre in item.prerequisites:
        p = g.techs[pre]
        s = '"%s" -> "%s-item"' % (pre, name)
        f.write(s)
        so_far += s

    s = '"%s-item" [label="%s\\n' % (name, name) + cost(item) + '"];\n'
    f.write(s)
    so_far += s

s = 'node [fillcolor="#99ffff"];\n'
f.write(s)
so_far += s

for name, base in g.base_type.items():
    if not base.prerequisites:
        continue
    for pre in base.prerequisites:
        p = g.techs[pre]
        s = '"%s" -> "%s-base"' % (pre, name)
        f.write(s)
        so_far += s

    s = '"%s-base" [label="%s\\n' % (name, name) + cost(base) + '"];\n'
    f.write(s)
    so_far += s

s = 'node [fillcolor="#aaffaa"];\n'
f.write(s)
so_far += s

blue = False


def set_or(state):
    global blue
    if blue != state:
        blue = state
        if blue:
            f.write('edge [arrowhead=empty,color="#0000FF"];\n')
        else:
            f.write('edge [arrowhead=normal,color="#000000"];\n')


SAFETY2LOCATIONS = collections.defaultdict(list)

for name, loc in g.locations.items():
    if not loc.prerequisites:
        continue
    if "impossible" in loc.prerequisites:
        continue
    set_or(False)
    for pre in loc.prerequisites:
        if pre == "OR":
            set_or(True)
            continue
        p = g.techs[pre]
        s = '"%s" -> "%s-loc"' % (pre, name)
        f.write(s)
        so_far += s

    if loc.safety > 0:
        SAFETY2LOCATIONS[loc.safety].append(loc)
    s = '"%s-loc" [label="%s"];\n' % (name, name)
    f.write(s)
    so_far += s

# When there are multiple locations providing the same
# safety level, we inject a safety node.  This reduces
# the number of edges from L * T to L + T.
for safety_level in sorted(SAFETY2LOCATIONS):
    locs = SAFETY2LOCATIONS[safety_level]
    if len(locs) == 1:
        continue
    s = '"safety-%s" [label="Safety level %s", shape="hexagon"];\n' % (
        safety_level,
        safety_level,
    )
    f.write(s)
    so_far += s
    for loc in locs:
        s = '"%s-loc" -> "safety-%s"' % (loc.id, safety_level)
        f.write(s)
        so_far += s

for tech_spec in g.techs.values():
    pre = tech_spec.prerequisites_in_cnf_format()
    if not pre or tech_spec.danger < 1:
        continue
    # Safety requirement is the highest safety required
    # between each "AND" and the lowest between "OR".
    # MAX(
    #   MIN(a1.danger, [OR] a2.danger, [OR] ...), [AND]
    #   MIN(b2.danger, [OR] b2.danger, [OR] ...), [AND]
    #   ...
    # )
    safety_required = max(
        min(g.techs[t].danger for t in dep_group) for dep_group in pre
    )
    # We only emit the edge for safety when the tech bumps
    # the minimum requirement.  This is to reduce the number
    # of edges in the graph.
    if tech_spec.danger > safety_required:
        source = "safety-%s" % tech_spec.danger
        if len(SAFETY2LOCATIONS[tech_spec.danger]) == 1:
            source = "%s-loc" % SAFETY2LOCATIONS[tech_spec.danger][0].id
        s = '"%s" -> "%s"' % (source, tech_spec.id)
        f.write(s)
        so_far += s


f.write("\n}\n")
so_far += "\n"
f.close()

try:
    system("unflatten -l10 items.dot | dot -Tpng -o items.png")
except:
    pass
