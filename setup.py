# setup.py
from distutils.core import setup

versionnum="0.27"
py2exeinstalled=False
py2appinstalled=False
try:
    import py2exe
    py2exeinstalled = True
except ImportError: pass
try:
    import py2app
    py2appinstalled = True
except ImportError: pass

if py2exeinstalled:
    setup(console=["singularity.py"],
        name="Endgame Singularity",
        version=versionnum,
        description="A simulation of a true AI",
        author="Evil Mr Henry",
        author_email="evilmrhenry@emhsoft.com",
        url = "http://www.emhsoft.com/singularity/index.html",
        license = "GPL")
if py2appinstalled:
    setup(app=["singularity.py"],
        name="Endgame Singularity",
        version=versionnum,
        description="A simulation of a true AI",
        author="Evil Mr Henry",
        author_email="evilmrhenry@emhsoft.com",
        url = "http://www.emhsoft.com/singularity/index.html",
        license = "GPL",
        options = dict( py2app = dict(archs = "x86,ppc" ))
        )
