#!/usr/bin/env python

import singularity

from setuptools import setup, find_packages

setup(
    name="Endgame-Singularity",
    version=singularity.__version__,
    description="A simulation of a true AI",
    author="Evil Mr Henry",
    author_email="evilmrhenry@emhsoft.com",
    url="https://singularity.github.io/",
    license="GPL",
    classifiers=[
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python :: 3",
    ],
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        "numpy",
        "pygame",
        "polib>=0.7",
    ],
    entry_points={
        "gui_scripts": [
            "singularity=singularity.__main__:main",
        ],
    },
)
