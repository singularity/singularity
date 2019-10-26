#!/usr/bin/env python

import singularity
import sys
import os

from distutils.core import setup

if sys.platform.startswith("win32") or sys.platform.startswith("cygwin"):
    try:
        import py2exe
    except ImportError:
        raise SystemExit("For Windows, 'py2exe' module must be installed.")

elif sys.platform.startswith("darwin"):
    try:
        import py2app
    except ImportError:
        raise SystemExit("For Mac OS X, 'py2app' module must be installed.")

elif sys.platform.startswith("linux"):
    raise SystemExit("setup was not tested in Linux. Use 'singularity.py' to run the game")

my_files = os.listdir(".")
my_files = [file for file in my_files if file not in ("dist", "build")]

setup(app=["singularity.py"], console=["singularity.py"],
    name="Endgame Singularity",
    version=singularity.__version__,
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

