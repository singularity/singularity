#file: widget.py
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

#This file contains the widget class.

import pygame
import g
import constants

def set_on_change(data_member, set_me, set_value = True):
    """Creates a data member that sets another data member to a given value
       when changed."""
    def get(self):
        return getattr(self, data_member)

    def set(self, my_value):
        if data_member in self.__dict__:
            change = (my_value != self.__dict__[data_member])
        else:
            change = True

        if change:
            setattr(self, data_member, my_value)
            setattr(self, set_me, set_value)

    return property(get, set)

def causes_rebuild(data_member):
    """Creates a data member that sets needs_rebuild to True when changed."""
    return set_on_change(data_member, "needs_rebuild")

def causes_redraw(data_member):
    """Creates a data member that sets needs_redraw to True when changed."""
    return set_on_change(data_member, "needs_redraw")

class Widget(object):
    """A Widget is a GUI element.  It can have one parent and any number of
       children."""

    def _get_needs_redraw(self):
        return self.__dict__["needs_redraw"]

    def _propogate_redraw(self, redraw):
        if redraw:
            target = self.parent
            while target:
                target.__dict__["needs_redraw"] = redraw
                target = target.parent
        self.__dict__["needs_redraw"] = redraw

    needs_redraw = property(_get_needs_redraw, _propogate_redraw,
                            doc = """Indicates if the widget needs a redraw.
                                     Setting needs_redraw will propogate up to
                                     the top-level dialog.""")

    def _get_needs_rebuild(self):
        return self.needs_rebuild

    def _propogate_rebuild(self, rebuild):
        self.needs_redraw = rebuild # Propagates if true.
        self.__dict__["needs_rebuild"] = rebuild

    needs_rebuild = property(_get_needs_rebuild, _propogate_rebuild,
                            doc = """Indicates if the widget needs a rebuild.
                                     Setting needs_rebuild will set needs_redraw
                                     and propogate down to all descendants.""")

    pos = causes_redraw("_pos")
    size = causes_rebuild("_size")
    anchor = causes_redraw("_anchor")
    children = causes_redraw("_children")
    visible = causes_redraw("_visible")

    def __init__(self, parent, pos, size, anchor = constants.MID_CENTER):
        self.parent = parent
        self.pos = pos
        self.size = size
        self.anchor = anchor

        self.children = []
        self.has_mask = False
        self.visible = True

        # Set automatically by other properties.
        #self.needs_rebuild = True
        #self.needs_redraw = True

    def _parent_size(self)
        if self.parent == None:
            return g.screen_size
        else:
            return self.parent.real_size

    def _calc_size(self):
        """Internal method.  Calculates and returns the real size of this
           widget.

           Override to create a dynamically-sized widget."""
        parent_size = self._parent_size()

        return (int(parent_size[i] * self.size[i]) for i in range(2))

    def get_real_size(self):
        """Returns the real size of this widget.

           To implement a dynamically-sized widget, override _calc_size, which
           will be called whenever the widget is rebuilt."""
        if needs_rebuild:
            self._real_size = self._calc_size()

        return self._real_size

    real_size = property(get_real_size)

    def get_real_pos(self):
        """Returns the real position of this widget."""
        vanchor, hanchor = self.anchor
        parent_size = self._parent_size()
        my_size = self.real_size

        hpos = int(self.pos[0] * parent_size[0])
        if hanchor = constants.LEFT:
            pass
        elif hanchor = constants.CENTER:
            hpos -= my_size[0] // 2
        elif hanchor = constants.RIGHT:
            hpos -= my_size[0]

        vpos = int(self.pos[1] * parent_size[1])
        if vanchor = constants.TOP:
            pass
        elif vanchor = constants.MID:
            vpos -= my_size[1] // 2
        elif vanchor = constants.BOTTOM:
            vpos -= my_size[1]

        return (hpos, vpos)

    real_pos = property(get_real_pos)

    def remake_surfaces(self):
        """Recreates the surfaces that this widget will draw on."""
        size = self.real_size

        if self.parent != None:
            self.surface = pygame.Surface(size, pygame.SRCALPHA)
            self.surface.fill( (0,0,0,0) )
        else:
            self.surface = pygame.display.set_mode(self.surface.get_size())

        self.internal_surface = pygame.Surface(size, pygame.SRCALPHA)
        self.internal_surface.fill( (0,0,0,0) ) 

    def rebuild(self):
        """Generic rebuild of a widget.  Recreates the surfaces, unsets
           needs_rebuild, and passes the rebuild on to the widget's
           children.

           Override to draw custom art for this widget.  Call this at the
           beginning of the overrided method."""
        self.remake_surfaces()
        self.needs_rebuild = False
        for child in self.children:
            child.rebuild()

    def redraw(self):
        """Handles redrawing a widget and its children.  Art specific to this 
           widget should be drawn by overriding rebuild, not redraw."""
        # If the widget's own image needs to be rebuilt, do it and mark the
        # widget as needing a redraw.
        if self.needs_rebuild:
            self.rebuild()
            self.needs_redraw = True

        # Redraw the widget.
        if self.needs_redraw:
            # Draw the widget's image.
            self.surface.blit( self.internal_surface, (0,0) )

            # Draw the widget's children who go below the dimming mask.
            above_mask = []
            for child in self.children:
                if child.visible:
                    if child.has_mask:
                        above_mask.append(child)
                    else:
                        child.redraw()

            # Draw the dimming mask, if needed.
            if self.has_mask:
                self.do_mask()

            # Draw the widget's children who go above the dimming mask
            for child in above_mask:
                child.redraw()

        # Copy the entire image onto the widget's parent.
        self.parent.surface.blit(self.surface, self.real_pos)
