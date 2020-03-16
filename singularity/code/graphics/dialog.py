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

from __future__ import absolute_import

import bisect
import time
import pygame
import operator

from singularity.code.graphics import g, constants, widget, text, button, listbox


KEYPAD = {pygame.K_KP1: 1, pygame.K_KP2: 2, pygame.K_KP3: 3, pygame.K_KP4: 4,
          pygame.K_KP5: 5, pygame.K_KP6: 6, pygame.K_KP7: 7, pygame.K_KP8: 8,
          pygame.K_KP9: 9}


def insort_right_w_key(a, x, lo=0, hi=None, key=lambda v: v):
    """Insert item x in list a, and keep it sorted assuming a is sorted.

    If x is already in a, insert it to the right of the rightmost x.

    Optional args lo (default 0) and hi (default len(a)) bound the
    slice of a to be searched.

    (Basically bisect.insort_right but with support for a key function)
    """

    if lo < 0:
        raise ValueError('lo must be non-negative')
    if hi is None:
        hi = len(a)
    x_key = key(x)
    while lo < hi:
        mid = (lo+hi)//2
        mid_key = key(a[mid])
        if x_key < mid_key:
            hi = mid
        else:
            lo = mid+1
    a.insert(lo, x)


def move_mouse(dxy):
    (dx, dy) = dxy
    old_x, old_y = pygame.mouse.get_pos()
    x = old_x+dx
    y = old_y+dy
    pygame.mouse.set_pos((x, y))

def fake_click(down):
    if down:
        type = pygame.MOUSEBUTTONDOWN
    else:
        type = pygame.MOUSEBUTTONUP
    click_event = pygame.event.Event(type, {'button': 1, 'pos': pygame.mouse.get_pos()})
    pygame.event.post(click_event)

def fake_key(key):
    down_event = pygame.event.Event(pygame.KEYDOWN,
                                    {'key': key, 'unicode': None})
    up_event = pygame.event.Event(pygame.KEYUP, {'key': key, 'unicode': None})
    pygame.event.post(down_event)
    pygame.event.post(up_event)

def handle_ebook(event):
    key = KEYPAD[event.key]
    new_key = None

    if event.type == pygame.KEYDOWN:
        if key == 2:
            move_mouse((0,10))
        elif key == 4:
            move_mouse((-10,0))
        elif key == 6:
            move_mouse((10,0))
        elif key == 8:
            move_mouse((0,-10))

    if key == 1:
        fake_click(event.type == pygame.KEYDOWN)
    elif key == 3:
        new_key = constants.XO1_X
    elif key == 9:
        new_key = constants.XO1_O
    elif key == 7:
        new_key = constants.XO1_SQUARE

    if new_key is not None:
        new_event = pygame.event.Event(event.type, {'key': new_key, 'unicode': None})
        pygame.event.post(new_event)

def call_dialog(dialog, parent=None):
    parent_dialog = None
    target = parent
    while target:
        if isinstance(target, Dialog):
            parent_dialog = target
            break
        target = target.parent

    if parent_dialog:
        parent_dialog.lost_focus()

    retval = dialog.show()

    if parent_dialog:
        parent_dialog.regained_focus()

    Dialog.top.needs_redraw = True

    return retval


def insort_all(sorted_list, items):
    for item in items:
        insort_right_w_key(sorted_list, item, key=operator.itemgetter(0))


class Dialog(text.Text):
    """A Dialog is a Widget that has its own event loop and can be faded out."""

    top = None # The top-level dialog.

    faded = widget.causes_redraw("_faded")

    # Used for detecting double-clicks.
    #            (time, (x, y), button)
    last_click = (0,    (0, 0), -1    )

    def __init__(self, parent=None, pos=(.5, .1), size=(1, .9),
                 anchor=constants.TOP_CENTER, **kwargs):
        kwargs.setdefault("background_color", (0, 0, 0, 0))
        kwargs.setdefault("borders", ())
        super(Dialog, self).__init__(parent, pos, size, anchor, **kwargs)
        self.visible = False
        self.faded = False
        self.is_above_mask = True
        self.self_mask = True
        self.needs_remask = True

        self.needs_timer = None

        self.handlers = {}
        self.key_handlers = {}

        self.add_handler(constants.CLICK, self.fake_escape, 200)

    def lost_focus(self):
        self.key_down = None
        self.faded = True
        self.stop_timer()

    def fake_escape(self, event):
        if event.button == 3:
            fake_key(pygame.K_ESCAPE)
            raise constants.Handled

    def regained_focus(self):
        self.faded = False
        self.start_timer()
        self.fake_mouse()

    def make_top(self):
        """Makes this dialog be the top-level dialog."""
        if self.parent != None:
            raise ValueError("Dialogs with parents cannot be the top-level dialog.")
        else:
            Dialog.top = self

    def remake_surfaces(self):
        """Recreates the surfaces that this widget will draw on."""
        super(Dialog, self).remake_surfaces()

    def start_timer(self, force = False):
        if self.needs_timer == None:
            self.needs_timer = bool(self.handlers.get(constants.TICK, False))
        if self.needs_timer or force:
            pygame.time.set_timer(pygame.USEREVENT, 1000 // g.FPS)

    def stop_timer(self):
        pygame.time.set_timer(pygame.USEREVENT, 0)

    def reset_timer(self):
        self.stop_timer()
        self.start_timer()

    def show(self):
        """Shows the dialog and enters an event-handling loop."""
        from singularity.code.mixer import play_music

        self.visible = True
        self.key_down = None
        self.needs_rebuild = True
        self.start_timer()

        # Pretend to jiggle the mouse pointer, to force buttons to update their
        # selected state.
        Dialog.top.maybe_update()
        self.fake_mouse()

        # Force a timer tick at the start to make sure everything's initialized.
        if self.needs_timer:
            self.handle(pygame.event.Event(pygame.USEREVENT))
            Dialog.top.maybe_update()
            pygame.display.flip()

        while True:
            # Update handles updates of all kinds to all widgets, as needed.
            Dialog.top.maybe_update()
            play_music()
            event = pygame.event.wait()
            result = self.handle(event)
            if result != constants.NO_RESULT:
                break
        self.stop_timer()
        self.visible = False
        return result

    def add_handler(self, type, handler, priority = 100):
        """Adds a handler of the given type, with the given priority."""
        insort_right_w_key(self.handlers.setdefault(type, []),
                           (priority, handler), key=operator.itemgetter(0))

    def remove_handler(self, type, handler):
        """Removes all instances of the given handler from the given type."""
        self.handlers[type] = [h for h in self.handlers.get(type, [])
                                 if h[1] != handler]

    def add_key_handler(self, key, handler, priority=100):
        """Adds a key handler to the given key, with the given priority."""
        insort_right_w_key(self.key_handlers.setdefault(key, []),
                           (priority, handler), key=operator.itemgetter(0))

    def remove_key_handler(self, key, handler):
        """Removes all instances of the given handler from the given key."""
        self.key_handlers[key] = [h for h in self.key_handlers.get(key, [])
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
        handlers = []
        if event.type == pygame.MOUSEMOTION:
            # Compress multiple MOUSEMOTION events into one.
            # Note that the pos will be wrong, so pygame.mouse.get_pos() must
            # be used instead.
            time.sleep(1. / g.FPS)
            pygame.event.clear(pygame.MOUSEMOTION)

            # Generic mouse motion handlers.
            handlers = self.handlers.get(constants.MOUSEMOTION, [])[:]

            # Drag handlers.
            if event.buttons[0]:
                insort_all(handlers, self.handlers.get(constants.DRAG, []))
        elif event.type == pygame.USEREVENT:
            # Clear excess timer ticks.
            pygame.event.clear(pygame.USEREVENT)

            # Timer tick handlers.
            handlers = self.handlers.get(constants.TICK, [])

            # Generate repeated keys.
            if self.key_down:
                self.repeat_counter += 1
                if self.repeat_counter >= 5:
                    self.repeat_counter = 0
                    self.handle(self.key_down)
        elif event.type in (pygame.KEYDOWN, pygame.KEYUP):
            
            # TODO: Dynamize global key handlers.
            # TODO: Allows customization of global key handlers.
            # Important: Global key handlers should always be a combination 
            # of two keys or F# keys.
            if event.key == pygame.K_RETURN and pygame.key.get_mods() & pygame.KMOD_ALT:
                if event.type == pygame.KEYDOWN:
                    g.set_fullscreen(not g.fullscreen)
                    Dialog.top.needs_resize = True

            elif event.key == pygame.K_F5:
                if event.type == pygame.KEYDOWN:
                    import singularity.code.graphics.theme as theme
                    if theme.current:
                        import singularity.code.data as data
                        theme_id = theme.current.id
                        data.load_themes()
                        theme.set_theme(theme_id, force_reload=True)

            elif event.type == pygame.KEYDOWN:
                # Generic keydown handlers.
                insort_all(handlers, self.handlers.get(constants.KEYDOWN, []))

                # Generic key event handlers.
                insort_all(handlers, self.handlers.get(constants.KEY, []))

                if event.unicode:
                    # Unicode-based keydown handlers for this particular key.
                    insort_all(handlers, self.key_handlers.get(event.unicode, []))
                # Keycode-based handlers for this particular key.
                insort_all(handlers, self.key_handlers.get(event.key, []))

                # Begin repeating keys.
                if self.key_down is not event:
                    self.key_down = event
                    self.repeat_counter = -10
                    self.start_timer(force = True)
            else: # event.type == pygame.KEYUP:
                # Stop repeating keys.
                self.key_down = None
                self.reset_timer()

                # Generic keyup handlers.
                insort_all(handlers, self.handlers.get(constants.KEYUP, []))

            # OLPC XO-1 ebook mode.
            if g.ebook_mode and event.key in KEYPAD:
                handlers = [(0, handle_ebook)]
        elif event.type == pygame.MOUSEBUTTONUP:
            # Handle mouse scrolls by imitating PageUp/Dn
            if event.button in (4, 5):
                if event.button == 4:
                    key = pygame.K_PAGEUP
                else:
                    key = pygame.K_PAGEDOWN
                fake_key(key)
                return constants.NO_RESULT

            # Mouse click handlers.
            handlers = [] + self.handlers.get(constants.CLICK, [])

            when = time.time()
            where = event.pos
            what = event.button

            old_when, old_where, old_what = self.last_click
            self.last_click = when, where, what

            if what == old_what and when - old_when < .5:
                # Taxicab distance.
                dist = (abs(where[0] - old_where[0]) +
                        abs(where[1] - old_where[1]))

                if dist < 10:
                    # Add double-click handlers, but keep the click handlers.
                    insort_all(handlers,
                               self.handlers.get(constants.DOUBLECLICK, []))
        elif event.type == pygame.QUIT:
            raise SystemExit

        return self.call_handlers(handlers, event)

    def fake_mouse(self):
        """Fakes a MOUSEMOTION event.  MOUSEMOTION handlers must be able to
           handle a None event, in order to support this method."""
        handlers = self.handlers.get(constants.MOUSEMOTION, [])[:]
        self.call_handlers(handlers, event=None)

    def on_close_dialog(self):
        pass

    def call_handlers(self, handlers, event):
        # Feed the event to all the handlers, in priority order.
        for __, handler in handlers:
            try:
                handler(event)
            except constants.Handled:
                break # If it's been handled, we leave the rest alone.
            except constants.ExitDialog as e:
                # Exiting the dialog.
                self.on_close_dialog()
                if e.args:
                    # If we're given a return value, we pass it on.
                    return e.args[0]
                else:
                    # Otherwise, exit with a return value of None.
                    return

        # None of the handlers instructed the dialog to close, so we pass that
        # information back up to the event loop.
        return constants.NO_RESULT


class FocusDialog(Dialog):
    def __init__(self, *args, **kwargs):
        self.focus_list = []
        self.current_focus = None

        super(FocusDialog, self).__init__(*args, **kwargs)

        self.add_key_handler(pygame.K_TAB, self.change_focus, 0)

    def add_focus_widget(self, widget):
        self.focus_list.append(widget)

    def remove_focus_widget(self, widget):
        try:
            self.focus_list.remove(widget)
        except ValueError:
            pass

    def took_focus(self, widget):
        if self.current_focus is not None and self.current_focus is not widget:
            self.current_focus.has_focus = False
        self.current_focus = widget
        widget.has_focus = True

    def clear_focus(self, widget):
        if self.current_focus is not None and self.current_focus is widget:
            self.current_focus.has_focus = False
            self.current_focus = None

    def change_focus(self, event):

        if len(self.focus_list) == 0:
            raise constants.Handled
        elif len(self.focus_list) == 1:
            
            has_focus = not self.focus_list[0].has_focus
            self.focus_list[0].has_focus = has_focus
            
            if has_focus:
                self.current_focus = self.focus_list[0]
            else:
                self.current_focus = None
                
            raise constants.Handled

        backwards = bool(pygame.key.get_mods() & pygame.KMOD_SHIFT)

        if self.current_focus is not None:
            self.current_focus.has_focus = False

        if self.current_focus not in self.focus_list:
            if backwards:
                index = len(self.focus_list) - 1
            else:
                index = 0
        else:
            old_index = self.focus_list.index(self.current_focus)
            if backwards:
                index = old_index - 1 # Correctly wraps to -1
            else:
                index = old_index + 1
                if index > len(self.focus_list):
                    index = 0
        
        if index == -1 or index == len(self.focus_list):
            self.current_focus = None
        else:
            self.current_focus = self.focus_list[index]
            self.current_focus.has_focus = True

        raise constants.Handled


class NullDialog(Dialog):
    """NullDialog, for when you absolutely, positively need to do nothing at
       all."""
    def show(self):
        pass


class TopDialog(Dialog):
    """A Dialog that sets itself as the top-level dialog.
       It must not have a parent, or exception will occur"""
    def __init__(self, *args, **kwargs):
        super(TopDialog, self).__init__(*args, **kwargs)
        self.size = (1, 1)
        self.pos = (0, 0)
        self.anchor = constants.TOP_LEFT
        self.make_top()


class TextDialog(Dialog):
    def __init__(self, parent, pos=(.5, .1), size=(.45, .5),
                 anchor=constants.TOP_CENTER, **kwargs):
        kwargs.setdefault("valign", constants.TOP)
        kwargs.setdefault("align", constants.LEFT)
        kwargs.setdefault("shrink_factor", .88)
        kwargs.setdefault("background_color", "text_dialog_background")
        kwargs.setdefault("border_color", "text_dialog_border")
        kwargs.setdefault("borders", constants.ALL)

        super(TextDialog, self).__init__(parent, pos, size, anchor, **kwargs)


class YesNoDialog(TextDialog):
    """A Dialog with YES and NO buttons which exits the dialog with True and
    False return values, respectively.
    """
    def __init__(self, parent, *args, **kwargs):
        self.parent = parent

        yes_type = kwargs.pop("yes_type", N_("&YES"))
        no_type = kwargs.pop("no_type", N_("&NO"))
        self.invert_enter = kwargs.pop("invert_enter", False)
        self.invert_escape = kwargs.pop("invert_escape", False)

        super(YesNoDialog, self).__init__(parent, *args, **kwargs)

        self.yes_button = button.ExitDialogButton(self, (-.1, -.99), (-.3, -.1),
                                                  text=yes_type,
                                                  autotranslate=True,
                                                  anchor=constants.BOTTOM_LEFT,
                                                  exit_code=True, default=False)

        self.no_button = button.ExitDialogButton(self, (-.9, -.99), (-.3, -.1),
                                                 text=no_type,
                                                 autotranslate=True,
                                                 anchor=constants.BOTTOM_RIGHT,
                                                 exit_code=False, default=False)

        self.add_key_handler(pygame.K_RETURN, self.on_return)
        self.add_key_handler(pygame.K_KP_ENTER, self.on_return)
        self.add_key_handler(pygame.K_ESCAPE, self.on_escape)

    def on_return(self, event):
        if event and event.type == pygame.KEYUP:
            return
        if self.invert_enter:
            self.no_button.activate_with_sound(event)
        else:
            self.yes_button.activate_with_sound(event)

    def on_escape(self, event):
        if event and event.type == pygame.KEYUP:
            return
        if self.invert_escape:
            self.yes_button.activate_with_sound(event)
        else:
            self.no_button.activate_with_sound(event)


class MessageDialog(TextDialog):
    """A Dialog with an OK button that exits the dialog, return value of None"""

    def __init__(self, parent, **kwargs):
        self.parent = parent

        ok_type = kwargs.pop("ok_type", N_("&OK"))

        super(MessageDialog, self).__init__(parent, **kwargs)

        self.ok_button = button.ExitDialogButton(self, (-.5, -.99), (-.3, -.1),
                                                 autotranslate=True,
                                                 text=ok_type,
                                                 anchor=constants.BOTTOM_CENTER)

        self.add_key_handler(pygame.K_RETURN, self.on_return)
        self.add_key_handler(pygame.K_KP_ENTER, self.on_return)

    def on_return(self, event):
        if event.type == pygame.KEYUP: return
        self.ok_button.activate_with_sound(event)


class TextEntryDialog(TextDialog, FocusDialog):

    def __init__(self, parent, pos=(-.50, -.50), size=(.50, .10),
                 anchor=constants.MID_CENTER, **kwargs):
        kwargs.setdefault('wrap', False)
        kwargs.setdefault("shrink_factor", 1)
        kwargs.setdefault("text_size", 20)
        self.default_text = kwargs.pop("default_text", "")
        ok_type = kwargs.pop("ok_type", N_("&OK"))
        cancel_type = kwargs.pop("cancel_type", N_("&CANCEL"))
        super(TextEntryDialog, self).__init__(parent, pos, size, anchor, **kwargs)

        self.text_field = text.EditableText(self, (0, -.50), (-.71, -.50),
                                            borders=constants.ALL,
                                            base_font="normal")

        self.ok_button = button.FunctionButton(self, (-.72, -.50), (-.14, -.50),
                                               autotranslate=True,
                                               text=ok_type,
                                               function=self.return_text)
        self.cancel_button = button.FunctionButton(self, (-.86, -.50), (-.14, -.50),
                                                   autotranslate=True,
                                                   text=cancel_type,
                                                   function=self.return_nothing)

        self.add_key_handler(pygame.K_RETURN, self.return_text)
        self.add_key_handler(pygame.K_KP_ENTER, self.return_text)
        self.add_key_handler(pygame.K_ESCAPE, self.return_nothing)

    def show(self):
        self.text_field.text = self.default_text
        self.text_field.cursor_pos = len(self.default_text)
        return super(TextEntryDialog, self).show()

    def return_nothing(self, event=None):
        if event and event.type == pygame.KEYUP:
            return
        raise constants.ExitDialog("")

    def return_text(self, event=None):
        if event and event.type == pygame.KEYUP:
            return
        raise constants.ExitDialog(self.text_field.text)

class ChoiceDialog(YesNoDialog):
    list = widget.causes_rebuild("_list")
    def __init__(self, parent, *args, **kwargs):
        self.parent = parent
        self.list = kwargs.pop("list", [])
        self.default = kwargs.pop("default", None)
        kwargs.setdefault("yes_type", N_("&OK"))
        kwargs.setdefault("no_type", N_("&BACK"))
        kwargs.setdefault("background_color", "clear")

        super(ChoiceDialog, self).__init__(parent, *args, **kwargs)

        self.yes_button.exit_code_func = self.return_list_pos
        self.no_button.exit_code = None
        self.listbox = self.make_listbox()

    def make_listbox(self):
        return listbox.Listbox(self, (0, 0), (-1, -.85),
                               anchor=constants.TOP_LEFT,
                               on_double_click_on_item=self.yes_button.activated,
                               )

    def return_list_pos(self):
        return self.listbox.list_pos

    def show(self):
        if type(self.default) == int:
            self.listbox.list_pos = self.default
        elif type(self.default) == str and self.default in self.list:
            self.listbox.list_pos = self.list.index(self.default)
        else:
            self.listbox.list_pos = 0
        self.listbox.auto_scroll = True

        return super(ChoiceDialog, self).show()

    def rebuild(self):
        self.listbox.list = self.list
        super(ChoiceDialog, self).rebuild()


class ChoiceDescriptionDialog(ChoiceDialog):
    key_list = widget.causes_rebuild("_key_list")

    def __init__(self, parent, *args, **kwargs):
        self.parent = parent
        self.key_list = kwargs.pop("key_list", None)
        self.desc_func = kwargs.pop("desc_func", lambda pane, key: NullDialog)

        super(ChoiceDescriptionDialog, self).__init__(parent, *args, **kwargs)

        self.description_pane = \
            widget.BorderedWidget(self, (-1, 0), (-.45, -.85),
                                  anchor = constants.TOP_RIGHT)


    def make_listbox(self):
        return listbox.UpdateListbox(self, (0, 0), (-.53, -.85),
                                     anchor=constants.TOP_LEFT,
                                     update_func=self.handle_update)

    def _update_desc_pane(self):
        list_pos = self.listbox.list_pos

        if 0 <= list_pos < len(self.list):
            if self.key_list:
                assert len(self.list) <= len(self.key_list), \
                    "Key list must be at least as long as display list."

                key = self.key_list[self.listbox.list_pos]
            else:
                key = self.list[self.listbox.list_pos]
        else:
            key = None

        # Safely clear all the description pane's children.
        self.description_pane.remove_hooks()
        self.description_pane.children = []
        self.description_pane.add_hooks()

        self.desc_func(self.description_pane, key)

    def rebuild(self):
        self.listbox.needs_rebuild = True
        self._update_desc_pane()
        super(ChoiceDescriptionDialog, self).rebuild()

    def handle_update(self, item):
        self.needs_rebuild = True
        # This is called before the class is fully initialized
        if hasattr(self, 'listbox'):
            self._update_desc_pane()



class SimpleMenuDialog(Dialog):
    width = widget.causes_rebuild("_width")

    def __init__(self, *args, **kwargs):
        buttons = kwargs.pop("buttons", [])
        width = kwargs.pop("width", .20)
        super(SimpleMenuDialog, self).__init__(*args, **kwargs)

        self.size = (-1, -1)
        self.pos = (0, 0)
        self.anchor = constants.TOP_LEFT
        self.width = width

        self.button_panel = \
            widget.BorderedWidget(self, (-.5, -.5), (0.22, 0.43),
                                  anchor=constants.MID_CENTER,
                                  background_color="simple_menu_background",
                                  border_color="simple_menu_border",
                                  borders=constants.ALL)

        self.buttons = buttons

    @property
    def buttons(self):
        return self._buttons

    @buttons.setter
    def buttons(self, buttons):
        if (hasattr(self, '_buttons') and not self._buttons is None):
            for button in self._buttons:
                if button.parent is not None:
                    button.parent = None

        self._buttons = buttons
        self.needs_rebuild = True

    def rebuild(self):
        num_buttons = len(self.buttons)
        height = (.06 * num_buttons) + .01

        self.button_panel.size = (self.width + .02, height)

        y_pos = .01
        for button in self.buttons:
            button.parent = self.button_panel

            button.pos = (.01, y_pos)
            button.size = (self.width, .05)
            button.text_size = 24

            y_pos += .06

        super(SimpleMenuDialog, self).rebuild()
