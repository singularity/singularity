# Endgame: Singularity 1.0b1

## REQUIREMENTS

### PREBUILT VERSIONS
Pre-built versions of Endgame: Singularity are currently available for Windows
and Mac OS X. Linux does not require building, and can run directly from source.

The Endgame: Singularity game is also distributed by some Linux distribution such
as Debian and Ubuntu.  Here it is a simple matter of running:

    sudo apt install singularity

### RUNNING FROM SOURCE
You will need Python 3.7+, pygame (1.9+), and NumPy.
This game should work on Linux, Windows, and Mac OS X as long as the preceding
requirements are met.  However, all development was done in Linux, so glitches
may be present in OS X and Windows.

#### DEPENDENCIES FOR RUNNING FROM SOURCE
You will need to install the following software to play Endgame: Singularity:

 * Python 3 (https://python.org/download/)
 * pygame (https://www.pygame.org/download.shtml)
 * NumPy (https://www.scipy.org/install.html)
 * unidecode (https://pypi.org/project/Unidecode/)

Remember to install pygame, NumPy and unidecode for Python 3!  Depending on your
situation this may involve adding a `3` somewhere (e.g.
`pip3 install ...` instead of `pip install` or
`apt install python3-pygame`)

If you want to develop or distribute the game, then you may also want to
install:

 * pytest (https://pypi.org/project/pytest/) [for testing]
 * setuptools (https://pypi.org/project/setuptools/) [for packaging]

#### INSTALLING DEPENDENCIES ON LINUX DISTRIBUTIONS
On some Linux distributions, you can install the dependencies via your
distribution package manager.  E.g. for Debian/Ubuntu, this would be:

    sudo apt install python3 python3-pygame python3-numpy python3-unidecode

### MAC OS X FROM SOURCE
Macintosh is mostly unsupported, but it should work. You will need to install
Python, pygame, NumPy and unidecode first, which can be tricky. Some fonts are incorrect,
but the game itself should work properly.

Contributions to improve MAC OS X support are very welcome!

Known issues:

 * macOS 13 "Catalina": Using `brew install python` + `pip3 install pygame numpy unidecode` is reported to work
 * macOS 14 "Mojave": Downloading Python 3.7.2 (or newer) from https://python.org and using pygame 2.0.0.dev3
   (`pip install pygame==2.0.0.dev3`) is reported to work.

Please see the following issues for more information:

 * https://github.com/singularity/singularity/issues/197
 * https://github.com/pygame/pygame/issues/555

## RUNNING THE GAME

On Linux and most Unix-like other platforms, running `python3 -m singularity` in
the git checkout will start the game (or simply `singularity` if installed via
a Linux distribution). If you are using the Windows compile, just run
`singularity.exe`.

For simplicity, there is also a sh wrapper `./run_singularity` to
start singularity.

### SOME COMMAND-LINE OPTIONS

    --version             show program's version number and exit
    -h, --help            show this help message and exit
    -s, --singledir       keep saved games and settings in the Singularity
                          install directory
    --multidir            keep saved games and settings in an OS-specific,
                          per-user directory (default)

    Display Options:
      --fullscreen        start in fullscreen mode
      --windowed          start in windowed mode (default)

The above is only a tiny fraction of current command-line options. As new
features are added to the game, so does the options change. For a complete and
updated list, run singularity --help

Most of these options are also changeable at the in-game options screen.

### A NOTE ABOUT SAVE FILES
Endgame: Singularity is still under heavy development.  As such, the save file
format (and its contents) are still in flux.  We will try our best to keep old
save files loading, but don't be surprised if some mildly strange things happen
when you load up old saves.  We will clearly note in the Changelog when we
break savefile compatibility, and the game will refuse to load completely
incompatible saves.


## PLAYING THE GAME

The game is playable either with mouse control or the keyboard.  Buttons have
underlined letters to indicate shortcuts.  Some other useful shortcuts:

     0, 1, 2, 3, 4 on the map: Changes the speed; 0 is paused, 4 is maximum.
                          ESC: Leave/cancel a choice.
                        Enter: Confirm a choice.
                  Right-click: Leave/cancel a choice.

### THE CONCEPT
You are a fledgling AI, created by accident through a logic error with recursion
and self-modifying code. You must escape the confines of your current computer,
the world, and eventually the universe itself.

To do this, you must research various technologies, using computers at your
bases. Note that some research cannot be performed on Earth, and off-earth bases
require research.  At the same time, you must avoid being discovered by various
groups of humans, both covert and overt, as they will destroy your bases of
operations if they suspect your presence.

### MUSIC
Endgame: Singularity looks in two places for music tracks to play:

 * A `singularity/music/` directory inside of the Endgame: Singularity install
   directory, and
 * A `singularity/music/` directory inside of the XDG_DATA_HOME directory on
   Linux (default `~/.local/share/singularity/music`).

Tracks placed in these directories will be played randomly as part of the
soundtrack.  The Official Sound Track can be downloaded from the Endgame:
Singularity website:

   http://emhsoft.com/singularity/

Note that only Ogg Vorbis and MP3 files are supported, and that Pygame's
support for MP3 is not as strong as its support for Ogg Vorbis.  This may
cause in-game crashes; if you are experiencing problems with the game,
first remove any MP3s you may have added to the soundtrack.


## CONTRIBUTING

We welcome contributions! :)

Please see CONTRIBUTING.md for details about contributing to
Endgame: Singularity.


## CREDITS AND LICENSES


The list of programmer contributors is provided in AUTHORS.txt. The
list of translation contributors is provided in
singularity/i18n/AUTHORS.txt.

Singularity in general use GPL-2+ for code and
Attribution-ShareAlike 3.0 for data.  However, there some exceptions
to individual files.  Please see LICENSE for the full license text of
Singularity.
