# setup.py
from distutils.core import setup

versionnum="0.28_pre"
try:
    import py2exe
except ImportError:
    try:
        import py2app
    except ImportError:
        raise SystemExit, "py2exe or py2app must be installed."

import os
my_files = os.listdir(".")
my_files = [file for file in my_files if file not in ("dist", "build")]

setup(app=["singularity.py"], console=["singularity.py"],
    name="Endgame Singularity",
    version=versionnum,
    description="A simulation of a true AI",
    author="Evil Mr Henry",
    author_email="evilmrhenry@emhsoft.com",
    url = "http://www.emhsoft.com/singularity/index.html",
    license = "GPL",
    options = dict( py2app = dict(archs = "x86,ppc",
                                  resources = ",".join(my_files)
                                  ),
                    py2exe = dict(compressed = True,
                                  bundle_files = 1
                                  )
                    )
    )

