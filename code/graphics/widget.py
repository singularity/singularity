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
from numpy import array

import g
import constants

def unmask(widget):
    """Causes the widget to exist above its parent's fade mask.  The widget's
       children will still be masked, unless they are unmasked themselves."""
    unmask_all(widget)
    widget.mask_children = True

def unmask_all(widget):
    """Causes the widget to exist above its parent's fade mask.  The widget's
       children will not be masked."""
    widget.self_mask = True
    widget.do_mask = lambda: None

def call_on_change(data_member, call_me, *args, **kwargs):
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
            call_me(self, *args, **kwargs)

    return property(get, set)

def set_on_change(data_member, set_me, set_value = True):
    """Creates a data member that sets another data member to a given value
       when changed."""
    return call_on_change(data_member, setattr, set_me, set_value)

def causes_rebuild(data_member):
    """Creates a data member that sets needs_rebuild to True when changed."""
    return set_on_change(data_member, "needs_rebuild")

def causes_redraw(data_member):
    """Creates a data member that sets needs_redraw to True when changed."""
    return set_on_change(data_member, "needs_redraw")

def causes_resize(data_member):
    """Creates a data member that sets needs_resize to True when changed."""
    return set_on_change(data_member, "needs_resize")

def causes_reposition(data_member):
    """Creates a data member that sets needs_reposition to True when changed."""
    return set_on_change(data_member, "needs_reposition")

def causes_update(data_member):
    """Creates a data member that sets needs_update to True when changed."""
    return set_on_change(data_member, "needs_update")

def propogate_need(data_member):
    """Creates a function that can be passed to call_on_change.  When the
       data member changes to True, needs_update is set, and the True value
       is passed to all descendants."""
    def do_propogate(self):
        if getattr(self, data_member, False):
            self.needs_update = True

            descendants = self.children[:]
            while descendants:
                child = descendants.pop()
                # Propogate to this child and its descendants, if needed.
                if not getattr(child, data_member, False):
                   setattr(child, data_member, True)
                   child._needs_update = True
                   descendants += child.children

    return do_propogate

class Widget(object):
    """A Widget is a GUI element.  It can have one parent and any number of
       children."""

    needs_redraw = call_on_change("_needs_redraw",
                                  propogate_need("_needs_redraw"))

    needs_resize = call_on_change("_needs_resize",
                                  propogate_need("_needs_resize"))

    needs_reposition = call_on_change("_needs_reposition",
                                      propogate_need("_needs_reposition"))

    needs_rebuild = causes_update("_needs_rebuild")

    def _propogate_update(self):
        if self._needs_update:
            target = self.parent
            while target and not target._needs_update:
                target._needs_update = True
                target = target.parent

    needs_update = call_on_change("_needs_update", _propogate_update)

    pos = causes_reposition("_pos")
    size = causes_resize("_size")
    anchor = causes_reposition("_anchor")
    visible = causes_redraw("_visible")

    def __init__(self, parent, pos, size, anchor = constants.TOP_LEFT):
        self.parent = parent
        self.children = []

        self.pos = pos
        self.size = size
        self.anchor = anchor

        # "It's a widget!"
        if self.parent:
            self.add_hooks()

        self.is_above_mask = False
        self.self_mask = False
        self.mask_children = False
        self.visible = True

        self.needs_rebuild = True
        self.collision_rect = None

        # Set automatically by other properties.
        #self.needs_redraw = True
        #self.needs_full_redraw = True

    def add_hooks(self):
        self.parent.children.append(self)

        # Won't trigger on the call from __init__, since there are no children
        # yet, but add_hooks may be explicitly called elsewhere to undo
        # remove_hooks.
        for child in self.children:
            child.add_hooks()

    def remove_hooks(self):
        # We copy the children list to avoid index corruption.
        for child in self.children[:]:
            child.remove_hooks()

        # Remove the children at the end, so that their own removals propogate.
        self.parent.children.remove(self)

    def _parent_size(self):
        if self.parent == None:
            return g.screen_size
        else:
            return self.parent.real_size

    def _calc_size(self):
        """Internal method.  Calculates and returns the real size of this
           widget.

           Override to create a dynamically-sized widget."""
        parent_size = self._parent_size()
        size = list(self.size)
        for i in range(2):
            if size[i] > 0:
                size[i] = int(size[i] * g.screen_size[i])
            elif size[i] < 0:
                size[i] = int( (-size[i]) * parent_size[i] )

        return tuple(size)

    def get_real_size(self):
        """Returns the real size of this widget.

           To implement a dynamically-sized widget, override _calc_size, which
           will be called whenever the widget is resized, and set needs_resize
           when appropriate."""
        return self._real_size

    real_size = property(get_real_size)

    def get_real_pos(self):
        """Returns the real position of this widget on its parent."""
        vanchor, hanchor = self.anchor
        parent_size = self._parent_size()
        my_size = self.real_size

        if self.pos[0] >= 0:
            hpos = int(self.pos[0] * g.screen_size[0])
        else:
            hpos = - int(self.pos[0] * parent_size[0])

        if hanchor == constants.LEFT:
            pass
        elif hanchor == constants.CENTER:
            hpos -= my_size[0] // 2
        elif hanchor == constants.RIGHT:
            hpos -= my_size[0]

        if self.pos[1] >= 0:
            vpos = int(self.pos[1] * g.screen_size[1])
        else:
            vpos = - int(self.pos[1] * parent_size[1])

        if vanchor == constants.TOP:
            pass
        elif vanchor == constants.MID:
            vpos -= my_size[1] // 2
        elif vanchor == constants.BOTTOM:
            vpos -= my_size[1]

        return (hpos, vpos)

    real_pos = property(get_real_pos)

    def _make_collision_rect(self):
        """Creates and returns a collision rect for this widget."""
        pos = array(self.real_pos)
        if self.parent:
            pos += self.parent.collision_rect[:2]

        return pygame.Rect(pos, self.real_size)

    def is_over(self, position):
        if position != (0,0):
            return self.collision_rect.collidepoint(position)
        else:
            return False

    def remake_surfaces(self):
        """Recreates the surfaces that this widget will draw on."""
        size = self.real_size
        pos = self.real_pos

        if self.parent != None:
            self.surface = self.parent.surface.subsurface(pos + size)
        else:
            if g.fullscreen:
                flags = pygame.FULLSCREEN
            else:
                flags = 0
            self.surface = pygame.display.set_mode(size, flags)
            self.surface.fill( (0,0,0,255) )

            g.fade_mask = pygame.Surface(size, 0, g.ALPHA)
            g.fade_mask.fill( (0,0,0,175) )

    def prepare_for_redraw(self):
        # First we handle any substance changes.
        if self.needs_rebuild:
            self.rebuild()

        # Then size changes.
        if self.needs_resize:
            self.resize()

        # Then position changes.
        if self.needs_reposition:
            self.reposition()

        # And finally we recurse to our descendants.
        for child in self.children:
            if child.needs_update and child.visible:
                child.prepare_for_redraw()

    def maybe_update(self):
        if self.needs_update:
            self.update()

    def update(self):
        # First we prepare everything for its redraw (if needed).
        self.prepare_for_redraw()

        self._update()

        # Oh, and if this is the top-level widget, we should flip the display.
        if not self.parent:
            pygame.display.flip()

    def _update(self):
        redrew_self = self.needs_redraw
        if self.needs_redraw:
            self.redraw()

        # Then we update any children below our fade mask.
        check_mask = []
        above_mask = []
        for child in self.children:
            if child.needs_update and child.visible:
                if child.is_above_mask:
                    above_mask.append(child)
                else:
                    check_mask += child._update()

        # Next, we handle the fade mask.
        if getattr(self, "faded", False):
            while check_mask:
                child = check_mask.pop()
                if not child.self_mask:
                    child.surface.blit(g.fade_mask, (0,0))
                elif child.mask_children:
                    check_mask += child.children

        # And finally we update any children above the fade mask.
        for child in above_mask:
            child._update()

        # Update complete.
        self.needs_update = False

        # Any descendants we didn't check for masking get passed upwards.
        if redrew_self:
            # If we redrew this widget, we tell our parent to consider it
            # instead.  The parent will recurse down to any descendants if
            # needed, and redraw already propogated down to them.
            check_mask = [self]

        return check_mask

    def rebuild(self):
        self.needs_rebuild = False

    def resize(self):
        self._real_size = self._calc_size()
        self.needs_resize = False
        self.needs_reposition = True
        self.needs_redraw = True

    def reposition(self):
        self.needs_reposition = False
        old_rect = self.collision_rect
        self.collision_rect = self._make_collision_rect()

        if not self.parent:
            self.remake_surfaces()
            self.needs_redraw = True
        elif (   (getattr(self, "surface", None) is None)
              or (old_rect is None)
              or (self.surface.get_parent() is not self.parent.surface)
              or (not self.collision_rect.contains(old_rect))
             ):
            self.remake_surfaces()
            self.parent.needs_redraw = True
        elif self.collision_rect != old_rect:
            self.remake_surfaces()
            self.needs_redraw = True


    def redraw(self):
        self.needs_redraw = False
        if self.parent is None:
            self.surface.fill((0,0,0,255))

    def add_handler(self, *args, **kwargs):
        """Handler pass-through."""
        if self.parent:
            self.parent.add_handler(*args, **kwargs)

    def remove_handler(self, *args, **kwargs):
        """Handler pass-through."""
        if self.parent:
            self.parent.remove_handler(*args, **kwargs)

    def add_key_handler(self, *args, **kwargs):
        """Handler pass-through."""
        if self.parent:
            self.parent.add_key_handler(*args, **kwargs)

    def remove_key_handler(self, *args, **kwargs):
        """Handler pass-through."""
        if self.parent:
            self.parent.remove_key_handler(*args, **kwargs)

    def add_focus_widget(self, *args, **kwargs):
        """Focus pass-through."""
        if self.parent:
            self.parent.add_focus_widget(*args, **kwargs)

    def remove_focus_widget(self, *args, **kwargs):
        """Focus pass-through."""
        if self.parent:
            self.parent.remove_focus_widget(*args, **kwargs)

    def took_focus(self, *args, **kwargs):
        """Focus pass-through."""
        if self.parent:
            self.parent.took_focus(*args, **kwargs)


class BorderedWidget(Widget):
    borders = causes_redraw("_borders")
    border_color = causes_redraw("_border_color")
    background_color = causes_redraw("_background_color")

    def __init__(self, parent, *args, **kwargs):
        self.parent = parent
        self.children = []
        self.borders = kwargs.pop("borders", ())
        self.border_color = kwargs.pop("border_color", g.colors["white"])
        self.background_color = kwargs.pop("background_color", g.colors["blue"])

        super(BorderedWidget, self).__init__(parent, *args, **kwargs)

    def rebuild(self):
        super(BorderedWidget, self).rebuild()
        if self.parent and self.background_color == g.colors["clear"]:
            self.parent.needs_redraw = True

    def reposition(self):
        super(BorderedWidget, self).reposition()
        if self.parent and self.background_color == g.colors["clear"]:
            self.parent.needs_redraw = True

    def redraw(self):
        super(BorderedWidget, self).redraw()

        # Fill the background.
        if self.background_color != g.colors["clear"]:
            self.surface.fill( self.background_color )

        self.draw_borders()

    def draw_borders(self):
        # Draw borders
        my_size = self.real_size
        horiz = (my_size[0], 1)
        vert = (1, my_size[0])

        for edge in self.borders:
            if edge == constants.TOP:
                self.surface.fill(self.border_color, (0, 0, my_size[0], 1) )
            elif edge == constants.LEFT:
                self.surface.fill(self.border_color, (0, 0, 1, my_size[1]) )
            elif edge == constants.RIGHT:
                self.surface.fill(self.border_color, 
                                  (my_size[0]-1, 0) + my_size)
            elif edge == constants.BOTTOM:
                self.surface.fill(self.border_color, 
                                  (0, my_size[1]-1) + my_size)


class FocusWidget(Widget):
    has_focus = causes_redraw("_has_focus")
    def __init__(self, *args, **kwargs):
        super(FocusWidget, self).__init__(*args, **kwargs)
        self.has_focus = True
        self.took_focus(self)

    def add_hooks(self):
        super(FocusWidget, self).add_hooks()
        self.parent.add_focus_widget(self)

    def remove_hooks(self):
        super(FocusWidget, self).remove_hooks()
        self.parent.remove_focus_widget(self)
