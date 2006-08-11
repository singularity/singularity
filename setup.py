# setup.py
from distutils.core import setup
import py2exe

setup(console=["singularity.py"],
      name="Endgame Singularity",
	version="0.25",
	description="A simulation of a true AI",
	author="Evil Mr Henry",
	author_email="evilmrhenry@emhsoft.net",
	url = "http://www.emhsoft.net/singularity/index.html",
	license = "GPL")
