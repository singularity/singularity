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
import time
import pygame

import constants
import g
import widget
import text
import button
import listbox

def call_dialog(dialog, parent=None):
    parent_dialog = None
    target = parent
    while target:
        if isinstance(target, Dialog):
            parent_dialog = target
            break
        target = target.parent

    if parent_dialog:
        parent_dialog.key_down = None
        parent_dialog.faded = True
        parent_dialog.stop_timer()

    retval = dialog.show()

    if parent_dialog:
        parent_dialog.faded = False
        parent_dialog.start_timer()

    parent_dialog.fake_mouse()
    Dialog.top.needs_redraw = True

    return retval

def insort_all(sorted_list, items):
    for item in items:
        bisect.insort(sorted_list, item)

class Dialog(text.Text):
    """A Dialog is a Widget that has its own event loop and can be faded out."""

    top = None # The top-level dialog.

    faded = widget.causes_redraw("_faded")

    def __init__(self, parent=None, pos = (.5,.1), size = (1, .9),
                 anchor = constants.TOP_CENTER, **kwargs):
        kwargs.setdefault("background_color", (0,0,0,0))
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

    def make_top(self):
        """Makes this dialog be the top-level dialog."""
        if self.parent != None:
            raise ValueError, \
                  "Dialogs with parents cannot be the top-level dialog."
        else:
            Dialog.top = self

    def remake_surfaces(self):
        """Recreates the surfaces that this widget will draw on."""
        super(Dialog, self).remake_surfaces()

    def start_timer(self, force = False):
        if self.needs_timer == None:
            self.needs_timer = bool(self.handlers.get(constants.TICK, False))
        if self.needs_timer or force:
            pygame.time.set_timer(pygame.USEREVENT, 1000 / g.FPS)

    def stop_timer(self):
        pygame.time.set_timer(pygame.USEREVENT, 0)

    def reset_timer(self):
        self.stop_timer()
        self.start_timer()

    def show(self):
        """Shows the dialog and enters an event-handling loop."""
        from code.g import play_music

        self.visible = True
        self.key_down = None
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
                self.visible = False
                return result
        self.stop_timer()

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
            # Generic key event handlers.
            handlers = self.handlers.get(constants.KEY, [])[:]

            if event.type == pygame.KEYDOWN:
                # Generic keydown handlers.
                insort_all(handlers, self.handlers.get(constants.KEYDOWN, []))

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

        elif event.type == pygame.MOUSEBUTTONUP:
            # Mouse click handlers.
            handlers = self.handlers.get(constants.CLICK, [])
        elif event.type == pygame.QUIT:
            raise SystemExit
        else:
            handlers = []

        return self.call_handlers(handlers, event)

    def fake_mouse(self):
        """Fakes a MOUSEMOTION event.  MOUSEMOTION handlers must be able to
           handle a None event, in order to support this method."""
        handlers = self.handlers.get(constants.MOUSEMOTION, [])[:]
        self.call_handlers(handlers, event=None)

    def call_handlers(self, handlers, event):
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


class FocusDialog(Dialog):
    def __init__(self, *args, **kwargs):
        self.focus_list = []
        self.current_focus = None

        super(FocusDialog, self).__init__(*args, **kwargs)

        self.add_key_handler(pygame.K_TAB, self.change_focus, 0)

    def add_focus_widget(self, widget):
        self.focus_list.append(widget)

    def remove_focus_widget(self, widget):
        self.focus_list.remove(widget)

    def took_focus(self, widget):
        if self.current_focus is not None and self.current_focus is not widget:
            self.current_focus.has_focus = False
        self.current_focus = widget

    def change_focus(self, event):
        if event is not None and event.type != pygame.KEYDOWN:
            return

        if len(self.focus_list) == 0:
            raise constants.Handled
        elif len(self.focus_list) == 1:
            self.focus_list[0].has_focus = True
            self.current_focus = self.focus_list[0]
            raise constants.Handled

        backwards = bool(pygame.key.get_mods() & pygame.KMOD_SHIFT)

        if self.current_focus is not None:
            self.current_focus.has_focus = False

        if self.current_focus not in self.focus_list:
            if backwards:
                index = -1
            else:
                index = 0
        else:
            old_index = self.focus_list.index(self.current_focus)
            if backwards:
                index = old_index - 1 # Correctly wraps to -1
            else:
                index = old_index + 1
                if index == len(self.focus_list):
                    index = 0

        self.current_focus = self.focus_list[index]
        self.current_focus.has_focus = True

        raise constants.Handled


class NullDialog(Dialog):
    """NullDialog, for when you absolutely, positively need to do nothing at
       all."""
    def show(self):
        pass


class TopDialog(Dialog):
    def __init__(self, *args, **kwargs):
        super(TopDialog, self).__init__(*args, **kwargs)
        self.size = (1, 1)
        self.pos = (0, 0)
        self.anchor = constants.TOP_LEFT
        self.make_top()


class TextDialog(Dialog):
    def __init__(self, parent, pos=(.5,.1), size=(.45,.5),
                 anchor=constants.TOP_CENTER, **kwargs):
        kwargs.setdefault("valign", constants.TOP)
        kwargs.setdefault("align", constants.LEFT)
        kwargs.setdefault("shrink_factor", .88)
        kwargs.setdefault("background_color", g.colors["dark_blue"])
        kwargs.setdefault("borders", constants.ALL)

        super(TextDialog, self).__init__(parent, pos, size, anchor, **kwargs)


class YesNoDialog(TextDialog):
    yes_type = widget.causes_rebuild("_yes_type")
    no_type = widget.causes_rebuild("_no_type")
    def __init__(self, parent, *args, **kwargs):
        self.parent = parent

        self.yes_type = kwargs.pop("yes_type", "yes")
        self.no_type = kwargs.pop("no_type", "no")
        self.invert_enter = kwargs.pop("invert_enter", False)
        self.invert_escape = kwargs.pop("invert_escape", False)

        super(YesNoDialog, self).__init__(parent, *args, **kwargs)

        self.yes_button = button.ExitDialogButton(self, (-.1,-.99), (-.3,-.1),
                                                 anchor = constants.BOTTOM_LEFT,
                                                 exit_code = True)

        self.no_button = button.ExitDialogButton(self, (-.9,-.99), (-.3,-.1),
                                                anchor = constants.BOTTOM_RIGHT,
                                                exit_code = False)

        self.add_key_handler(pygame.K_RETURN, self.on_return)
        self.add_key_handler(pygame.K_ESCAPE, self.on_escape)

    def rebuild(self):
        super(YesNoDialog, self).rebuild()

        self.yes_button.text = g.buttons[self.yes_type]
        self.yes_button.hotkey = g.buttons[self.yes_type + "_hotkey"]
        self.no_button.text = g.buttons[self.no_type]
        self.no_button.hotkey = g.buttons[self.no_type + "_hotkey"]

    def on_return(self, event):
        if self.invert_enter:
            self.no_button.activate_with_sound(event)
        else:
            self.yes_button.activate_with_sound(event)

    def on_escape(self, event):
        if self.invert_escape:
            self.yes_button.activate_with_sound(event)
        else:
            self.no_button.activate_with_sound(event)


class MessageDialog(TextDialog):
    ok_type = widget.causes_rebuild("_ok_type")
    def __init__(self, parent, **kwargs):
        self.parent = parent

        self.ok_type = kwargs.pop("ok_type", "ok")

        super(MessageDialog, self).__init__(parent, **kwargs)

        self.ok_button = button.ExitDialogButton(self, (-.5,-.99), (-.3,-.1),
                                               anchor = constants.BOTTOM_CENTER)

        self.add_key_handler(pygame.K_RETURN, self.ok_button.activate_with_sound)
        self.add_key_handler(pygame.K_ESCAPE, self.ok_button.activate_with_sound)

    def rebuild(self):
        super(MessageDialog, self).rebuild()

        self.ok_button.text = g.buttons[self.ok_type]
        self.ok_button.hotkey = g.buttons[self.ok_type + "_hotkey"]


class TextEntryDialog(TextDialog):
    def __init__(self, parent, size=(.25, .1), **kwargs):
        self.default_text = kwargs.pop("default_text", "")

        super(TextEntryDialog, self).__init__(parent, size = size, **kwargs)

        self.shrink_factor = .5
        self.text_field = text.EditableText(self, (0, -.5), (-.8, -.5),
                                            borders=constants.ALL,
                                            base_font=g.font[0])

        self.ok_button = button.FunctionButton(self, (-.82, -.5), (-.18, -.5),
                                               text=g.buttons["ok"],
                                               function=self.return_text)

        self.add_key_handler(pygame.K_RETURN, self.return_text)
        self.add_key_handler(pygame.K_ESCAPE, self.return_nothing)

    def show(self):
        self.text_field.text = self.default_text
        self.text_field.cursor_pos = len(self.default_text)
        return super(TextEntryDialog, self).show()

    def return_nothing(self, event):
        raise constants.ExitDialog, ""

    def return_text(self, event=None):
        raise constants.ExitDialog, self.text_field.text

class ChoiceDialog(YesNoDialog):
    list = widget.causes_rebuild("_list")
    def __init__(self, parent, *args, **kwargs):
        self.parent = parent
        self.list = kwargs.pop("list", [])
        self.default = kwargs.pop("default", None)
        kwargs.setdefault("yes_type", "ok")
        kwargs.setdefault("no_type", "back")
        kwargs.setdefault("background_color", g.colors["clear"])

        super(ChoiceDialog, self).__init__(parent, *args, **kwargs)

        self.listbox = self.make_listbox()

        self.yes_button.exit_code_func = self.return_list_pos
        self.no_button.exit_code = None

    def make_listbox(self):
        return listbox.Listbox(self, (0, 0), (-1, -.85),
                               anchor=constants.TOP_LEFT)

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

    def rebuild(self):
        self.listbox.needs_rebuild = True
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

        super(ChoiceDescriptionDialog, self).rebuild()

    def handle_update(self, item):
        self.needs_rebuild = True


class SimpleMenuDialog(Dialog):
    def __init__(self, *args, **kwargs):
        buttons = kwargs.pop("buttons")
        super(SimpleMenuDialog, self).__init__(*args, **kwargs)

        self.size = (-1, -1)
        self.pos = (0, 0)
        self.anchor = constants.TOP_LEFT

        num_buttons = len(buttons)
        height = (.06 * num_buttons) + .01
        self.button_panel = \
            widget.BorderedWidget(self, (-.5, -.5), (.22, height),
                                  anchor=constants.MID_CENTER,
                                  background_color=g.colors["dark_blue"],
                                  border_color=g.colors["white"],
                                  borders=constants.ALL)

        y_pos = .01
        for button in buttons:
            if button.parent is not None:
                button.remove_hooks()
            button.parent = self.button_panel
            button.add_hooks()

            button.pos = (.01, y_pos)
            button.size = (.20, .05)
            button.text_shrink_factor=.70

            y_pos += .06
