#!/usr/bin/env python

#file: make-tree.py
#Copyright (C) 2008 aes and FunnyMan3595
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

#This file is used to generate a visual representation of the tech tree using
#graphviz.

from os import system
from os.path import realpath
import sys

try:
    sys.path.insert(0, ".")
    from code import g
except ImportError:
    print "Run this from the main Singularity directory, as utils/make-tree.py"
    raise SystemExit

so_far = ""

def abbr(s):
    l = (("Advanced ", "Adv "),
         ("Project: ","P:"),
         ("Manipulation","Mnp"),
         ("Autonomous","Aut"),
         ("Computing","Cpu"),
         ("Quantum","Qu"),
         ("Personal Identification","P-Id"))
    for f,t in l: s = s.replace(f, t)
    return s

def cost(c):
    c = [ k/f for f,k in zip([1000, 86400, 24*60], c)]
    s = ', '.join(['%s %s' % (g.to_money(k), label) for label,k in zip(["money", "CPU", "days"], c) if k])
    return s and '\\n'+s or ''

j = dict([ (v[1],',fillcolor="#ffcccc"') for k,v in g.jobs.items() ])

f = file("techs.dot", 'w')
s = ("""\
digraph g {
ranksep=0.15;
nodesep=0.10;
edge [arrowsize=0.75];
node [shape=record,fontname=FreeSans,fontsize=7,height=0.01,width=0.01
      style=filled,fillcolor=white];
subgraph s {
rank=source;
""")

s += ";\n".join('"%s"' % k for k,v in g.techs.items() if not v.prerequisites) + ";\n}\n"
f.write(s)
so_far += s

for l in sum([ [ '"%s"->"%s";' % (p,k)
                 for p in v.prerequisites ]
              for k,v in g.techs.items() if k != "unknown_tech"],
             []):
    f.write(l+'\n')
    so_far += l+'\n'

f.write('\n')
so_far += '\n'

for n,t in g.techs.items():
    if n == "unknown_tech": continue
    s  = '"%s" [label="%s' % (n, abbr(n)) + cost(t.cost_left)
    s += '"'+ j.get(n,'') + '];\n'
    f.write(s)
    so_far += s

f.write("\n};\n")
so_far += '\n'
f.close()

try:    system("dot -Tpng -o techs.png techs.dot")
except: pass

f = file('items.dot','w')
f.write(so_far)
s = 'node [fillcolor="#ccccff"];\n'
f.write(s)
so_far += s

g.load_items()
for name,item in g.items.items():
    if not item.prerequisites: continue
    for pre in item.prerequisites:
        p = g.techs[pre]
        s = '"%s" -> "%s-item"' % (pre, name)
        f.write(s)
        so_far += s

    s  = '"%s-item" [label="%s\\n' % (name, name) + cost(item.cost) + '"];\n'
    f.write(s)
    so_far += s

s = 'node [fillcolor="#99ffff"];\n'
f.write(s)
so_far += s

g.load_bases()
for name,base in g.base_type.items():
    if not base.prerequisites: continue
    for pre in base.prerequisites:
        p = g.techs[pre]
        s = '"%s" -> "%s-base"' % (pre, name)
        f.write(s)
        so_far += s

    s  = '"%s-base" [label="%s\\n' % (name, name) + cost(base.cost) + '"];\n'
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

g.load_locations()
for name,loc in g.locations.items():
    if not loc.prerequisites: continue
    if "unknown_tech" in loc.prerequisites:
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

    s  = '"%s-loc" [label="%s"];\n' % (name, name)
    f.write(s)
    so_far += s

f.write("\n};\n")
so_far += '\n'
f.close()

try:    system("dot -Tpng -o items.png items.dot")
except: pass
