#file: dialog.py
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

#This file contains the dialog class.

import bisect
import pygame

import constants
import g
import widget

def causes_remask(data_member):
    """Creates a data member that sets needs_remask to True when changed."""
    return widget.set_on_change(data_member, "needs_remask")

def insort_all(sorted_list, items):
    for item in items:
        bisect.insort(sorted_list, item)

class Dialog(widget.Widget):
    """A Dialog is a Widget that has its own event loop and can be faded out."""

    top = None # The top-level dialog.

    faded = widget.causes_redraw("_faded")

    def __init__(self, parent, pos = (.5,.55), size = (1, .9), 
                 anchor = constants.MID_CENTER):
        super(Dialog, self).__init__(parent, pos, size, anchor)
        self.visible = False
        self.faded = False
        self.has_mask = True
        self.needs_remask = True

        self.handlers = {}
        self.key_handlers = {}

    def make_top(self):
        """Makes this dialog be the top-level dialog."""
        if self.parent != None:
            raise ValueError, \
                  "Dialogs with parents cannot be the top-level dialog."
        else:
            Dialog.top = self

    def remake_surfaces(self):
        """Recreates the surfaces that this widget will draw on.  This version
           handles the top-level Dialog via pygame's main surface."""
        super(Dialog, self).remake_surfaces()
        if self.parent == None:
            self.surface = pygame.display.set_mode(self.surface.get_size())

    def make_fade_mask(self):
        """Recreates the fade mask for this dialog.  Override if part of the 
           dialog should remain fully visible, even when not active."""
        mask = pygame.Surface(self.real_size, 0, g.ALPHA)
        mask.fill( (0,0,0,175) )
        return mask

    def get_fade_mask(self):
        """If the dialog needs a remask, calls make_fade_mask.  Otherwise, 
           returns the pre-made fade mask."""
        if self.needs_remask:
            self._fade_mask = self.make_fade_mask()
            self.needs_remask = False
        return self._fade_mask

    fade_mask = property(get_fade_mask)

    def do_mask(self):
        """Greys out the dialog when faded, to make it clear that it's not 
           active."""
        if self.faded:
            self.surface.blit( self.get_fade_mask(), (0,0) )

    def show(self):
        """Shows the dialog and enters an event-handling loop."""
        self.visible = True
        while True:
            # Redraw handles rebuilding and redrawing all widgets, as needed.
            Dialog.top.redraw()
            event = pygame.event.wait()
            result = self.handle(event)
            if result != constants.NO_RESULT:
                self.visible = False
                return result

    def add_handler(self, type, handler, priority = 100):
        """Adds a handler of the given type, with the given priority."""
        bisect.insort( self.handlers.setdefault(type, []), 
                       (priority, handler) )

    def remove_handler(self, type, handler):
        """Removes all instances of the given handler from the given type."""
        self.handlers[type] = [h for h in self.handlers.get(type, [])
                                 if h[1] != handler]

    def add_key_handler(self, key, handler, priority = 100):
        """Adds a key handler to the given key, with the given priority."""
        bisect.insort( self.key_handlers.setdefault(key, []), 
                       (priority, handler) )

    def remove_key_handler(self, key, handler):
        """Removes all instances of the given handler from the given key."""
        self.key_handlers[key] = [h for h in self.handlers.get(key, []) 
                                    if h[1] != handler]

    def handle(self, event):
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
            handlers = self.handlers.get(constants.MOUSEMOTION, [])[:]

            # Drag handlers.
            if event.buttons[0]:
                insort_all(handlers, self.handlers.get(constants.DRAG, []))
        elif event.type == pygame.USEREVENT:
            # Timer tick handlers.
            handlers = self.handlers.get(constants.TICK, [])
        elif event.type in (pygame.KEYDOWN, pygame.KEYUP):
            # Generic key event handlers.
            handlers = self.handlers.get(constants.KEY, [])[:]

            if event.type == pygame.KEYDOWN:
                # Generic keydown handlers.
                insort_all(handlers, self.handlers.get(constants.KEYDOWN, []))

                # Unicode-based keydown handlers for this particular key.
                insort_all(handlers, self.key_handlers.get(event.unicode, []))
            else: # event.type == pygame.KEYUP:
                # Generic keyup handlers.
                insort_all(handlers, self.handlers.get(constants.KEYUP, []))

                # Unicode-based keyup handling not available.
                # pygame doesn't bother defining .unicode on KEYUP events.

            # Keycode-based handlers for this particular key.
            insort_all(handlers, self.key_handlers.get(event.key, []))
        elif event.type == pygame.MOUSEBUTTONUP:
            # Mouse click handlers.
            handlers = self.handlers.get(constants.CLICK, [])
        elif event.type == pygame.QUIT:
            raise SystemExit
        else:
            handlers = []


        # Feed the event to all the handlers, in priority order.
        for priority, handler in handlers:
            try:
                handler(event)
            except constants.Handled:
                break # If it's been handled, we leave the rest alone.
            except constants.ExitDialog, e:
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
