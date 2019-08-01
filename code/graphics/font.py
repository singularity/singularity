#file: font.py
#Copyright (C) 2005,2006,2007,2008 Evil Mr Henry, Phil Bordelon, Brian Reid,
#                        and FunnyMan3595
#This file is part of Endgame: Singularity.

#Endgame: Singularity is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 2 of the License, or
#(at your option) any later version.

#Endgame: Singularity is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with Endgame: Singularity; if not, write to the Free Software
#Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

#This file contains class to handle font.

import pygame

class FontList(object):
    """ List object used to store font
    
    We use a lazy loader for fonts to reduce the file descriptor pressure
    Each font item apparently reserves a file descriptor (see GH#156)
    """

    def __init__(self, filename, max_size=100):
        self._filename = filename
        self._font_cache = {}
        self._max_size = max_size

    def __len__(self):
        return self._max_size

    def __contains__(self, item):
        return 0 <= item < self._max_size

    def __getitem__(self, item):
        font = self._font_cache.get(item)
        if font is None:
            if item < 0 or self._max_size <= item:
                raise IndexError(item)
            font = pygame.font.Font(self._filename, item)
            self._font_cache[item] = font
        return font
