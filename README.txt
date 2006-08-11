Endgame: Singularity 0.25

Requirements:
Recent versions of Python, pygame, and SDL_image. This game should work on
Linux, Windows, and Mac OS X as long as the preceding requirements are met.
However, all development was done in Linux, so glitches may be present in
OS X and Windows.

Windows:
You will need to install Python (http://python.org/download/) and Pygame:
(http://www.pygame.org/download.shtml). Once these are installed, double-click
on singularity.py to start the game. Alternatively, use the Windows compile.

Running the game:
on Linux, running the shell script "Endgame_Linux" will start the game. On
other platforms, type "python singularity.py".
Allowed arguments: -fullscreen, -640, -800, -1024, -1280, -nosound,
-language [language], -grab, -singledir

Explanation of options:
-fullscreen: runs game in fullscreen.
-640, -800, -1024, -1280: change the resolution to 640x480, 800x600,
	1024x768, or 1280x960.
-nosound: no sound. May allow playing the game without SDL_mixer.
-language: Change the language. Currently only English (-language en_US) and
	Spanish (-language es_AR) are included.
-grab: Activate a mouse grab. This prevents the mouse from exiting the game
	window.
-singledir: By default, Endgame saves in ~/.endgame/saves on *nix platforms.
	Setting this forces the Windows behavior of keeping everything within
	a single directory.

Note about save files:
Endgame: Singularity is still under heavy development.  As such, the save file
format (and its contents) are still in flux.  We will try our best to keep old
save files loading, but don't be surprised if some mildly strange things happen
when you load up old saves.  We will clearly note in the Changelog when we
break savefile compatibility, and the game will refuse to load completely
incompatible saves.

Playing the game:
Use mouse control. Buttons have underlined letters to indicate shortcuts.
Also, the following shortcut keys may prove useful:
0, 1, 2, 3, 4 in map screen: change the speed. 0 is pause, 4 is fastest.
ESC and Enter in various screens: leave or confirm a choice.
Right-click in a screen: cancel a dialog or leave a screen.
P, R, N, S in base screen: Change the base items.
	(Type the first letter of the component you want to change.)

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


Credits:
Evil Mr Henry
Phil Bordelon
Borg[MDQ] (translation into Spanish)
Adam Bark (reduced-CPU Clock class)

Contributing:
All suggestions, translations, code, etc. are welcomed, though it would be
wise to tell us before starting work on any large projects. Contact
evilmrhenry@emhsoft.net for more details.

Contributing translations:
To add a new translation, make copies of all *_en_US files in the data
subdirectory, renaming the copies to *_name_of_language. For each file,
translate all strings except id to the new language, and test with the
-language name_of_language option. It is expected to use the CC
Attribution-ShareAlike license. (Since the files you are translating
are under that license, I'm not sure you could get away with a different
license.)

Code License:
Copyright (C) 2005,2006 Evil Mr Henry and Phil Bordelon

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

Portions Copyright (C) 2005 Adam Bark.  See code/clock.py for details.

Data License:
The sounds, the text files, and the icons in the data subdirectory are under
the Creative Commons Licence "Attribution-ShareAlike 2.5":

You are free:

    * to copy, distribute, display, and perform the work
    * to make derivative works
    * to make commercial use of the work

Under the following conditions:
Attribution. You must attribute the work in the manner specified by the author or licensor.
Share Alike. If you alter, transform, or build upon this work, you may distribute the resulting work only under a license identical to this one.

    * For any reuse or distribution, you must make clear to others the license terms of this work.
    * Any of these conditions can be waived if you get permission from the copyright holder.

See the file Attribution-ShareAlike 2.5.html for the legal-quality license.


Graphic License:
The image of the earth is NASA's "The Blue Marble: Land Surface, Ocean Color
and Sea Ice".
http://visibleearth.nasa.gov/view_rec.php?vev1id=11612

NASA Terms of Use

For all non-private uses, NASA's Terms Of Use are as follows:

   1. The imagery is free of licensing fees
   2. NASA requires that they be provided a credit as the owners of the imagery

Visible Earth Addendum

Beyond the NASA Terms, the Visible Earth team requests, but does not require:

   1. The Visible Earth be provided a credit as the location that the imagery was found at
   2. A URL be provided, either to the Visible Earth
      (http://visibleearth.nasa.gov/) or to the page providing the link to the used image.



The boxy font used is "Acknowledge", by Brian Kent, modified in order to have the
numbers fixed-width.
http://www.aenigmafonts.com/fonts/fontsa.html

Terms of use:
Feel free to use any of my fonts. All of my Fonts are Freeware and you can use
them any way you want to (Personal use, Commercial use, or whatever).


The other font used is Bitstream Vera Sans:

Copyright
=========

Copyright (c) 2003 by Bitstream, Inc. All Rights Reserved. Bitstream
Vera is a trademark of Bitstream, Inc.

Permission is hereby granted, free of charge, to any person obtaining
a copy of the fonts accompanying this license ("Fonts") and associated
documentation files (the "Font Software"), to reproduce and distribute
the Font Software, including without limitation the rights to use,
copy, merge, publish, distribute, and/or sell copies of the Font
Software, and to permit persons to whom the Font Software is furnished
to do so, subject to the following conditions:

The above copyright and trademark notices and this permission notice
shall be included in all copies of one or more of the Font Software
typefaces.

The Font Software may be modified, altered, or added to, and in
particular the designs of glyphs or characters in the Fonts may be
modified and additional glyphs or characters may be added to the
Fonts, only if the fonts are renamed to names not containing either
the words "Bitstream" or the word "Vera".

This License becomes null and void to the extent applicable to Fonts
or Font Software that has been modified and is distributed under the
"Bitstream Vera" names.

The Font Software may be sold as part of a larger software package but
no copy of one or more of the Font Software typefaces may be sold by
itself.

THE FONT SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO ANY WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT
OF COPYRIGHT, PATENT, TRADEMARK, OR OTHER RIGHT. IN NO EVENT SHALL
BITSTREAM OR THE GNOME FOUNDATION BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, INCLUDING ANY GENERAL, SPECIAL, INDIRECT, INCIDENTAL,
OR CONSEQUENTIAL DAMAGES, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF THE USE OR INABILITY TO USE THE FONT
SOFTWARE OR FROM OTHER DEALINGS IN THE FONT SOFTWARE.

Except as contained in this notice, the names of Gnome, the Gnome
Foundation, and Bitstream Inc., shall not be used in advertising or
otherwise to promote the sale, use or other dealings in this Font
Software without prior written authorization from the Gnome Foundation
or Bitstream Inc., respectively. For further information, contact:
fonts at gnome dot org.
