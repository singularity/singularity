from code import g
from os import system

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
    s = ' '.join(['%c%d' % (ch,int(k)) for ch,k in zip('$cw', c) if k])
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
""")
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
        s = '"%s" -> "%s"' % (pre, name)
        f.write(s)
        so_far += s

for name,item in g.items.items():
    if not item.prerequisites: continue
    s  = '"%s" [label="%s\\n' % (name, name) + cost(item.cost) + '"];\n'
    f.write(s)
    so_far += s

f.write("\n};\n")
so_far += '\n'
f.close()

try:    system("dot -Tpng -o items.png items.dot")
except: pass
