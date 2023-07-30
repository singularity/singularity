# file: widget.py
# Copyright (C) 2008 FunnyMan3595
# This file is part of Endgame: Singularity.

# Endgame: Singularity is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# Endgame: Singularity is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Endgame: Singularity; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

# This file contains the widget class.

from __future__ import absolute_import

import pygame
from numpy import array
from inspect import getmembers

from singularity.code import g
from singularity.code.graphics import g as gg, constants

# surface.blits is available in 1.9.4 but it is not really useful until
# 1.9.5 or 1.9.6.  We pick 1.9.6 to be sure it works.
if pygame.version.vernum > (1, 9, 5):
    HAS_FUNCTIONAL_BLITS = True
else:
    HAS_FUNCTIONAL_BLITS = False


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
    """Creates a data member that calls a function when changed."""

    def get(self):
        return getattr(self, data_member)

    def set(self, my_value):
        if data_member in self.__dict__:
            change = my_value != self.__dict__[data_member]
        else:
            change = True

        if change:
            setattr(self, data_member, my_value)
            call_me(self, *args, **kwargs)

    return property(get, set)


def set_on_change(data_member, set_me, set_value=True):
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

            if hasattr(self, "children"):
                descendants = self.children[:]
                while descendants:
                    child = descendants.pop()
                    # Propogate to this child and its descendants, if needed.
                    if not getattr(child, data_member, False):
                        setattr(child, data_member, True)
                        child._needs_update = True
                        if hasattr(child, "children"):
                            descendants += child.children

    return do_propogate


# Previous attempt was to hide the raw value by resolving
# the value before returning it. However, there are legitimate
# reason to access the raw value. So, we need two property.
# Using a wrapper is not worth the trouble.
# I choose to let the unresolved value the default because
# in majority of it's what we want, and in other case,
# you must handle reconfig anyways.
class auto_reconfig(object):
    __slots__ = [
        "data_member",
        "reconfig_datamember",
        "reconfig_func",
    ]  # Avoid __dict__.

    def __init__(self, data_member, reconfig_prefix, reconfig_func):
        self.data_member = data_member
        self.reconfig_datamember = reconfig_prefix + data_member
        self.reconfig_func = reconfig_func

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.data_member)

    def __set__(self, obj, my_value):
        new_value = self.reconfig_func(my_value)

        setattr(obj, self.reconfig_datamember, new_value)
        setattr(obj, self.data_member, my_value)

    def reconfig(self, obj):
        updated_value = self.reconfig_func(getattr(obj, self.data_member))
        setattr(obj, self.reconfig_datamember, updated_value)


# In debug mode, this list tracks which widgets (i.e. rects) where highlighted "last"
# during a redraw, so they can be "re-updated" without the highlight
debug_mode_undo_drawing_highlight = []


class Widget(object):
    """A Widget is a GUI element.  It can have one parent and any number of
    children."""

    needs_redraw = call_on_change("_needs_redraw", propogate_need("_needs_redraw"))

    needs_resize = call_on_change("_needs_resize", propogate_need("_needs_resize"))

    needs_reposition = call_on_change(
        "_needs_reposition", propogate_need("_needs_reposition")
    )

    needs_rebuild = causes_update("_needs_rebuild")

    def _propogate_update(self):
        if self._needs_update:
            if hasattr(self, "parent"):
                target = self.parent
                while target and not target._needs_update:
                    target._needs_update = True
                    target = target.parent

    needs_update = call_on_change("_needs_update", _propogate_update)

    needs_reconfig = call_on_change(
        "_needs_reconfig", propogate_need("_needs_reconfig")
    )

    pos = causes_reposition("_pos")
    size = causes_resize("_size")
    anchor = causes_reposition("_anchor")
    visible = causes_redraw("_visible")

    def __init__(self, parent, pos, size, anchor=constants.TOP_LEFT):
        self.parent = parent
        self.children = []

        self.pos = pos
        self.size = size
        self.anchor = anchor

        # "It's a widget!"
        self.add_hooks()

        self.is_above_mask = False
        self.self_mask = False
        self.mask_children = False
        self.visible = True

        self.needs_rebuild = True
        self.collision_rect = None

        # Set automatically by other properties.
        # self.needs_redraw = True
        # self.needs_full_redraw = True
        self.needs_reconfig = True

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        if hasattr(self, "children"):
            self.remove_hooks()

        if hasattr(self, "_parent") and self._parent is not None:
            try:
                self._parent.children.remove(self)
            except ValueError:
                pass  # Wasn't there to start with.

        self._parent = parent

        if self.parent is not None:
            self.parent.children.append(self)
            self.parent.needs_rebuild = True
            self.parent.needs_resize = True
            self.parent.needs_reposition = True
            self.parent.needs_redraw = True

        if hasattr(self, "children"):
            self.add_hooks()

    def add_hooks(self):
        if self.parent is not None:
            # Won't trigger on the call from __init__, since there are no
            # children yet, but add_hooks may be explicitly called elsewhere to
            # undo remove_hooks.
            for child in self.children:
                child.add_hooks()

    def remove_hooks(self):
        # Localize the children list to avoid index corruption and O(N^2) time.
        children = self.children

        # Recurse to the children.
        for child in children:
            child.remove_hooks()

    def _parent_size(self):
        if self.parent == None:
            return gg.real_screen_size
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
                size[i] = int(size[i] * gg.real_screen_size[i])
            elif size[i] < 0:
                size[i] = int((-size[i]) * parent_size[i])

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
            hpos = int(self.pos[0] * gg.real_screen_size[0])
        else:
            hpos = -int(self.pos[0] * parent_size[0])

        if hanchor == constants.LEFT:
            pass
        elif hanchor == constants.CENTER:
            hpos -= my_size[0] // 2
        elif hanchor == constants.RIGHT:
            hpos -= my_size[0]

        if self.pos[1] >= 0:
            vpos = int(self.pos[1] * gg.real_screen_size[1])
        else:
            vpos = -int(self.pos[1] * parent_size[1])

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
        if not getattr(self, "collision_rect", None):
            return False

        if position != (0, 0):
            return self.collision_rect.collidepoint(position)
        else:
            return False

    def remake_surfaces(self):
        """Recreates the surfaces that this widget will draw on."""
        size = self.real_size
        pos = self.real_pos

        if self.parent != None:
            try:
                self.surface = self.parent.surface.subsurface(pos + size)
            except ValueError:
                print("Warning: %r can't fit on its parent." % self)
                print(pos, size, self.parent.real_pos, self.parent.real_size)

                wanted_rect = pos + size
                available_rect = self.parent.surface.get_rect()
                compromise = available_rect.clip(wanted_rect)

                self.surface = self.parent.surface.subsurface(compromise)
        else:
            # Recreate using the abstracted screen size, NOT the real one
            # g.set_screen() will calculate the proper g.real_screen_size
            if gg.screen_surface is None:
                # Ensure that the screen is initialized
                gg.set_mode()
            # We draw on a copy of the surface.  This is to avoid crashes
            # during draggable resizing (event.VIDEORESIZE) where the
            # screen size might change behind our backs while drawing
            # (event.VIDEORESIZE tells us that the screen has been updated
            # and we should catch up and not the other way around)
            self.surface = gg.screen_surface.copy()
            self.surface.fill((0, 0, 0, 255))

            gg.fade_mask = pygame.Surface(size, 0, gg.ALPHA)
            gg.fade_mask.fill((0, 0, 0, 175))

    def prepare_for_redraw(self):
        # First, we handle config changes.
        if self.needs_reconfig:
            self.reconfig()
            self.needs_reconfig = False

        # Then any substance changes.
        if self.needs_rebuild:
            self.rebuild()
            self.needs_rebuild = False

        # Then size changes.
        if self.needs_resize:
            self.resize()
            self.needs_resize = False
            self.needs_reposition = True
            self.needs_redraw = True

        # Then position changes.
        if self.needs_reposition:
            self.needs_reposition = False
            self.reposition()

        # And finally we recurse to our descendants.
        for child in self.children:
            if child.visible:
                child.prepare_for_redraw()

    def maybe_update(self):
        if self.needs_update:
            self.update()

    def update(self):
        # First we prepare everything for its redraw (if needed).
        self.prepare_for_redraw()

        _, updated_rect = self._update()

        # Oh, and if this is the top-level widget, we should update the display.
        if not self.parent and gg.screen_surface:
            root_surface = self.surface
            if g.debug and updated_rect:
                # In debug mode, draw red boxes to represent widgets that were updated.
                global debug_mode_undo_drawing_highlight
                try:
                    # If the theme defines a color for this purpose, we will use it
                    widget_highlight_color = gg.resolve_color_alias(
                        "debug_mode_highlight_redrawn_widget"
                    )
                except KeyError:
                    # ... and for every thing else, there is the color red.
                    widget_highlight_color = 0xFF, 0, 0, 0
                root_surface = self.surface.copy()
                n_updated_rect = []
                for rect in updated_rect:
                    n_updated_rect.append(
                        pygame.draw.rect(root_surface, widget_highlight_color, rect, 1)
                    )
                updated_rect.extend(debug_mode_undo_drawing_highlight)
                debug_mode_undo_drawing_highlight = n_updated_rect

            if HAS_FUNCTIONAL_BLITS:
                gg.screen_surface.blits(
                    ((root_surface, r, r) for r in updated_rect), doreturn=0
                )
            else:
                for r in updated_rect:
                    gg.screen_surface.blit(root_surface, r, area=r)

            pygame.display.update(updated_rect)

    def _update(self):
        redrew_self = self.needs_redraw
        update_full_rect = redrew_self
        affected_rects = []
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
                    # update_full_rect = True  # We do not bother tracking this case
                    child_mask, child_rects = child._update()
                    check_mask.extend(child_mask)
                    if child_rects and not update_full_rect:
                        affected_rects.extend(child_rects)

        # Next, we handle the fade mask.
        if getattr(self, "faded", False):
            while check_mask:
                child = check_mask.pop()
                if not child.self_mask:
                    # update_full_rect = True  # We do not bother tracking this case
                    child_rect = child.surface.blit(gg.fade_mask, (0, 0))
                    if not update_full_rect:
                        affected_rects.append(child_rect)
                elif child.mask_children:
                    check_mask += child.children

        # And finally we update any children above the fade mask.
        for child in above_mask:
            _, child_rects = child._update()
            if child_rects and not update_full_rect:
                affected_rects.extend(child_rects)

        # Update complete.
        self.needs_update = False

        # Any descendants we didn't check for masking get passed upwards.
        if redrew_self:
            # If we redrew this widget, we tell our parent to consider it
            # instead.  The parent will recurse down to any descendants if
            # needed, and redraw already propagated down to them.
            check_mask = [self]

        if update_full_rect:
            size = self.real_size
            pos = self.real_pos

            affected_rects = [self.collision_rect]

        return check_mask, affected_rects

    def reconfig(self):
        # Find reconfig property and update them.
        clazz = self.__class__
        for prop_name, prop in getmembers(clazz):
            if isinstance(prop, auto_reconfig):
                prop.reconfig(self)

    def rebuild(self):
        pass

    def resize(self):
        self._real_size = self._calc_size()

    def reposition(self):
        old_rect = self.collision_rect
        self.collision_rect = self._make_collision_rect()

        if not self.parent:
            self.remake_surfaces()
            self.needs_redraw = True
        elif (
            (getattr(self, "surface", None) is None)
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
            self.surface.fill((0, 0, 0, 255))

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

    def clear_focus(self, *args, **kwargs):
        """Focus pass-through."""
        if self.parent:
            self.parent.clear_focus(*args, **kwargs)


class BorderedWidget(Widget):
    borders = causes_redraw("__borders")

    border_color = auto_reconfig("_border_color", "resolved", gg.resolve_color_alias)
    background_color = auto_reconfig(
        "_background_color", "resolved", gg.resolve_color_alias
    )
    resolved_border_color = causes_redraw("_resolved_border_color")
    resolved_background_color = causes_redraw("_resolved_background_color")

    def __init__(self, parent, *args, **kwargs):
        self.borders = kwargs.pop("borders", ())
        self.border_color = kwargs.pop("border_color", "widget_border")
        self.background_color = kwargs.pop("background_color", "widget_background")

        super(BorderedWidget, self).__init__(parent, *args, **kwargs)

    def rebuild(self):
        super(BorderedWidget, self).rebuild()
        if self.parent and self.resolved_background_color == gg.colors["clear"]:
            self.parent.needs_redraw = True

    def reposition(self):
        super(BorderedWidget, self).reposition()
        if self.parent and self.resolved_background_color == gg.colors["clear"]:
            self.parent.needs_redraw = True

    def redraw(self):
        super(BorderedWidget, self).redraw()

        # TODO: Transparency do not work correctly.
        # First: fill cannot use alpha channel with current surface.
        # Second: Transparency needs the parent redraw to work correctly.
        # It make transparency unusable with some widget.

        # Fill the background.
        if self.resolved_background_color != gg.colors["clear"]:
            self.surface.fill(self.resolved_background_color)

        self.draw_borders()

    def draw_borders(self):
        my_size = self.real_size

        for edge in self.borders:
            if edge == constants.TOP:
                self.surface.fill(self.resolved_border_color, (0, 0, my_size[0], 1))
            elif edge == constants.LEFT:
                self.surface.fill(self.resolved_border_color, (0, 0, 1, my_size[1]))
            elif edge == constants.RIGHT:
                self.surface.fill(
                    self.resolved_border_color, (my_size[0] - 1, 0) + my_size
                )
            elif edge == constants.BOTTOM:
                self.surface.fill(
                    self.resolved_border_color, (0, my_size[1] - 1) + my_size
                )


class FocusWidget(Widget):
    has_focus = causes_redraw("_has_focus")

    def __init__(self, *args, **kwargs):
        super(FocusWidget, self).__init__(*args, **kwargs)
        self.has_focus = False

        self.add_handler(constants.CLICK, self.handle_click, 0)

    def add_hooks(self):
        super(FocusWidget, self).add_hooks()
        if self.parent is not None:
            self.parent.add_focus_widget(self)

    def remove_hooks(self):
        super(FocusWidget, self).remove_hooks()
        if self.parent is not None:
            self.parent.remove_focus_widget(self)

    def handle_click(self, event):
        if not self.is_over(event.pos):
            self.clear_focus(self)
