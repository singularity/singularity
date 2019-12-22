# Endgame: Singularity 1.0a1

## REQUIREMENTS

### PREBUILT VERSIONS
Pre-built versions of Endgame: Singularity are currently available for Windows
and Mac OS X. Linux does not require building, and can run directly from source

### RUNNING FROM SOURCE
You will need Python (2.7+ or 3.7+), pygame (1.9+), and NumPy.
This game should work on Linux, Windows, and Mac OS X as long as the preceding
requirements are met.  However, all development was done in Linux, so glitches
may be present in OS X and Windows.

### WINDOWS FROM SOURCE
You will need to install:

 * Python (http://python.org/download/)
 * pygame (http://www.pygame.org/download.shtml)
 * NumPy (http://www.scipy.org/Download)

Once these are installed, double-click on singularity.py to start the game.

### MAC OS X FROM SOURCE
Macintosh is mostly unsupported, but it should work. You will need to install
Python, pygame, and NumPy first, which can be tricky. Some fonts are incorrect,
but the game itself should work properly.


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

In the map screen (the screen with the world map), any location you can build
bases in is marked with the name, then the number of current bases in that
location. You start out with a base in North America. Also note that the cash
listing shows your current cash and your cash amount after all current
construction is complete.

After choosing a base, you will enter the base screen. Here you can change your
research goal, or build an item by clicking on the appropriate slot in the
center. (But note that your beginning base does not allow building.)

### MUSIC
Endgame: Singularity looks in two places for music tracks to play:

 * A music/ directory directly inside of the Endgame: Singularity install
   directory, and
 * A music/ directory inside of the preferences directory (~/.config/singularity
   in Linux, the install directory for Windows).

Tracks placed in these directories will be played randomly as part of the
soundtrack.  The Official Sound Track can be downloaded from the Endgame:
Singularity website:

   http://emhsoft.com/singularity/

Note that only Ogg Vorbis and MP3 files are supported, and that Pygame's
support for MP3 is not as strong as its support for Ogg Vorbis.  This may
cause in-game crashes; if you are experiencing problems with the game,
first remove any MP3s you may have added to the soundtrack.


## CONTRIBUTING

All suggestions, translations, code, etc. are welcomed, though it would be
wise to tell us before starting work on any large projects.  Join and/or
send mail to endgame-singularity@googlegroups.com for more details.

### CONTRIBUTING TRANSLATIONS
To add a new translation, please use the 'traduko' and 'gettext-singularity'
tools in utils/ dir. Their --help option should walk you through its usage.
If you have any questions contact us at endgame-singularity-dev@googlegroups.com
Note that the resulting file will be licensed either under the CC-BY-SA 3.0
license (for *.dat files created with traduko) or the game's code license
(for the *.po files created by gettext-singularity), both described below.

 * Website: http://www.emhsoft.com/singularity/
 * IRC Room: #singularity on irc.oftc.net (port 6667)

## CREDITS AND LICENSES


The list of programmer contributors is provided in AUTHORS.txt. The
list of translation contributors is provided in
singularity/i18n/AUTHORS.txt.

Singularity in general use GPL-2+ for code and
Attribution-ShareAlike 3.0 for data.  However, there some exceptions
to individual files.  Please see LICENSE for the full license text of
Singularity.
