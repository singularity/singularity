#file: image.py
#Copyright (C) 2008 FunnyMan3595
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

#This file contains the image widget.

import pygame

import constants
import g
import widget

class Image(widget.Widget):
    image = widget.causes_rebuild("_image")

    def __init__(self, parent, pos, size = (1, 1), 
                 anchor = constants.TOP_LEFT, image = None):
        super(Image, self).__init__(parent, pos, size, anchor)
        
        self.image = image

    def _calc_size(self):
        size = list( super(Image, self)._calc_size() )
        if size[0] == size[1] == 0:
            raise ValueError, "One image dimension must be specified!"

        image_size = self.image.get_size()
        ratio = image_size[0] / float(image_size[1])
        if size[0] == 0:
            size[0] = int(size[1] * ratio)
        elif size[1] == 0:
            size[1] = int(size[0] / ratio)

        return tuple(size)

    def rebuild(self):
        super(Image, self).rebuild()
        scaled_image = pygame.transform.scale(self.image, self.real_size)
        self.internal_surface.blit(scaled_image, (0,0))
