#!/usr/bin/env python

import singularity

from setuptools import setup, find_packages

setup(
    name="Endgame-Singularity",
    version=singularity.__version__,
    description="A simulation of a true AI",
    author="Evil Mr Henry",
    author_email="evilmrhenry@emhsoft.com",
    url = "http://www.emhsoft.com/singularity/index.html",
    license = "GPL",
    classifiers=[
        'Intended Audience :: End Users/Desktop',
        'Topic :: Games/Entertainment',

        'License :: OSI Approved :: GNU General Public License (GPL)',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    packages = find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
      'numpy',
      'pygame',
    ],
    entry_points={
        'gui_scripts': [
            'singularity=singularity:main',
        ],
    },
)
