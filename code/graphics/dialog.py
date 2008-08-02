#file: dialog.py
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

#This file contains the dialog class.

import pygame
from code import g
import constants

def causes_rebuild(data_member):
    def get(self):
        return self.__dict__[data_member]
    def set(self, value):
        self.__dict__[data_member] = value
        self.needs_rebuild = True

    return property(get, set)

import widget
class Dialog(widget.Widget):
    """A Dialog is a Widget that has its own event loop and can be faded out."""
    def __init__(self, pos = (.5,.55), size = (1, .9), 
                 anchor = constants.MID_CENTER, parent):
        super(Dialog, self).__init__(pos, size, anchor, parent)
        self.visible = False
        self.faded = False
        self.needs_remask = True

    def remake_surface(self):
        """Recreates the surface that this widget will draw on.  This version
           handles the top-level Dialog by resizing pygame's main surface."""
        if self.parent == None:
            pygame.display.set_mode(self.real_size())
        super(Dialog, self).remake_surface()

    def make_fade_mask(self):
        """Recreates the fade mask for this dialog.  Override if part of the 
           dialog should remain fully visible, even when not active."""
        mask = pygame.Surface(self.real_size(), pygame.SRCALPHA)
        mask.fill( (0,0,0,175) )
        self.fade_mask = mask

    def get_fade_mask(self):
        """If the dialog needs a remask, calls make_fade_mask.  Otherwise, 
           returns the pre-made fade mask."""
        if self.needs_remask:
            self.fade_mask = self.make_fade_mask()
            self.needs_remask = False
        return self.fade_mask

    def fade(self):
        """Greys out the dialog, to make it clear that it's not active."""
        if not self.faded:
            self.unfaded_surface = self.surface.copy()
            self.surface.blit( self.get_fade_mask(), (0,0) )
            self.faded = True

    def unfade(self):
        """Un-greys-out the dialog."""
        if self.faded:
            self.surface = self.unfaded_surface
            self.faded = False

    def show(self):
        """Shows the dialog and enters an event-handling loop."""
        while True:
            # Draw handles rebuilding and redrawing this widget, its parent, and
            # all of its children, if needed.
            self.draw()
            event in pygame.event.wait():
            result = self.handle(event)
            if result != constants.NO_RESULT:
                return result

    def add_handler(self, type, handler, priority = 100):
        """Adds a handler of the given type, with the given priority."""
        bisect.insort( self.handlers[type], (priority, handler) )

    def remove_handler(self, type, handler):
        """Removes all instances of the given handler from the given type."""
        self.handlers[type] = [h for h in self.handlers[type] 
                                 if h[1] != handler]

    def handle(event):
        """Sends an event through all the applicable handlers, returning
           constants.NO_RESULT if the event goes unhandled or is handled without
           requesting the dialog to exit.  Otherwise, returns the value provided
           by the handler."""
        # Get the applicable handlers.  The handlers lists are all sorted.
        # If more than one handler type is applicable, we use [:] to make a 
        # copy of the first type's list, then insort_all to insert the elements
        # of the other lists in proper sorted order.
        if event.type == pygame.MOUSEMOTION:
            # Generic mouse motion handlers.
            handlers = self.handlers[constants.MOUSEMOTION][:]

            # Drag handlers.
            if event.buttons[0]:
                insort_all(handlers, self.handlers[constants.DRAG])
        elif event.type == pygame.USEREVENT:
            # Timer tick handlers.
            handlers = self.handlers[constants.TICK]
        elif event.type in (pygame.KEYDOWN, pygame.KEYUP):
            # Generic key event handlers.
            handlers = self.handlers[constants.KEY][:]

            # Generic keydown/up handlers.
            if event.type == pygame.KEYDOWN:
                insort_all(handlers, self.handlers[constants.KEYDOWN])
            else: # event.type == pygame.KEYUP:
                insort_all(handlers, self.handlers[constants.KEYUP])

            # Handlers for this particular key.
            insort_all(handlers, self.key_handlers[event.key])
        elif event.type == pygame.MOUSEBUTTONUP:
            # Mouse click handlers.
            handlers = self.handlers[constants.CLICK]


        # Feed the event to all the handlers, in priority order.
        for priority, handler in handlers:
            try:
                handler(event)
            except Handled:
                break # If it's been handled, we leave the rest alone.
            except ExitDialog, e:
                # Exiting the dialog.
                if e.args: 
                   # If we're given a return value, we pass it on.
                   return e.args[0]
                else:
                   # Otherwise, exit with a return value of None.
                   return 
    
        # None of the handlers instructed the dialog to close, so we pass that
        # information back up to the event loop.
        return constants.NO_RESULT
