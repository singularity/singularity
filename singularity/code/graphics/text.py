#file: text.py
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

#This file contains the (non-editable) text widget AKA label.

from __future__ import absolute_import

import pygame

from singularity.code.pycompat import *
from singularity.code.graphics import g, widget, constants


DEBUG = False

def do_bisect(left, right, test):
    # Run a binary search for the largest acceptable value.
    # Thanks to bisect.bisect_left for the basic implementation.
    # Return is in range [left, right-1], inclusive
    while left + 1 < right:
        test_index = (left + right) // 2
        if test(test_index):
            left = test_index
        else:
            right = test_index
    return left

def convert_font_size(size):
    # Scale it to the screen size.
    raw_size = size * g.real_screen_size[1] // g.default_screen_size[1]
    # And round.
    return int(raw_size + 0.5)

def get_widths(font, text):
    if hasattr(font, "metrics"):
        return [m[4] for m in font.metrics(text)]
    else:
        return [font.size(c)[0] for c in text]

def strip_to_null(a_string):
    if not a_string:
        return a_string
    if a_string[0] == " ":
        a_string = u"\uFEFF" + a_string[1:]
    if a_string[-1] == " ":
        a_string =  a_string[:-1] + u"\uFEFF"
    return a_string

class WrapError(Exception): pass

# Splits a string into lines based on newline and word wrapping.
def split_wrap(text, font, wrap_at, break_words=True):
    raw_lines = text.split("\n")
    lines = []

    for raw_line in raw_lines:
        if font.size(raw_line)[0] <= wrap_at or wrap_at == 0:
            lines.append(raw_line + u"\uFEFF")
        else:
            words = raw_line.split(" ")
            pos = 0
            line = ""
            for word in words:
                word += " "
                word_size = font.size(word)[0]
                if pos + word_size <= wrap_at:
                    line += word
                    pos += word_size
                elif word_size < wrap_at:
                    lines.append(strip_to_null(line))
                    line = word
                    pos = word_size
                else:
                    if not break_words:
                        message = "'%s' is too wide and can't be broken"
                        raise WrapError(message % word)
                    widths = get_widths(font, word)
                    for index, char in enumerate(word):
                        width = widths[index]
                        if pos + width <= wrap_at:
                            line += char
                            pos += width
                        else:
                            lines.append(strip_to_null(line))
                            line = char
                            pos = width
            if line and line != " ":
                lines.append(strip_to_null(line))
    return lines

def size_of_block(text, font, width=0):
    # Apply newlines and word wrap.
    lines = split_wrap(text, font, width)

    # Calculate height and width of the text.
    total_height = 0
    max_width = 0
    for line in lines:
        line_width, line_height = font.size(line)
        max_width = max(max_width, line_width)
        total_height += line_height

    return (max_width, total_height)

def _do_print(surface, text, xy, font, color):
    if font.size(text)[0] == 0:
        return
    rendered_text = font.render(text, True, color)
    surface.blit(rendered_text, xy)

def print_string(surface, string_to_print, xy_orig, font, styles, align, valign,
                 dimensions, wrap):
    xy = list(xy_orig)

    width = dimensions[0] - 4
    height = dimensions[1] - 4

    if wrap:
        lines = split_wrap(string_to_print, font, width)
    else:
        lines = split_wrap(string_to_print, font, 0)

    if valign != constants.TOP:
        vsize = len(lines) * font.get_linesize()
        if vsize <= height:
            excess_space = height - vsize
            if valign == constants.MID:
                xy[1] += excess_space // 2
            else: # valign == constants.BOTTOM
                xy[1] += excess_space

    color, bgcolor, underline, switch_char = styles.pop(0)
    offset = 0
    for line in lines:
        xy[0] = xy_orig[0]
        if align != constants.LEFT:
            hsize = font.size(line)[0]
            excess_space = width - hsize
            if align == constants.CENTER:
                xy[0] += excess_space // 2
            else: # align == constants.RIGHT
                xy[0] += excess_space

        chunks = [line]
        my_styles = [(color, bgcolor, underline)]
        while switch_char != 0 and switch_char < offset + len(chunks[-1]):
            real_switch = switch_char - offset
            offset += real_switch

            piece = chunks.pop()
            chunks.extend([piece[:real_switch], piece[real_switch:]])
            color, bgcolor, underline, switch_char = styles.pop(0)
            my_styles.append((color, bgcolor, underline))
        offset += len(chunks[-1])

        print_line(surface, xy, font, chunks, my_styles)
        xy[1] += font.get_linesize()


def print_line(surface, xy, font, chunks, styles):
    for chunk, (color, bgcolor, underline) in zip(chunks, styles):
        size = font.size(chunk)

        # Fill the background, if any.
        if bgcolor is not None:
            surface.fill(bgcolor, xy+size)

        # Print the text.
        font.set_underline(underline)
        _do_print(surface, chunk, xy, font, color)
        font.set_underline(False)

        # Adjust the starting position.
        xy[0] += size[0]


def resize_redraw(self):
    self.needs_resize = True
    self.needs_redraw = True


class Text(widget.BorderedWidget):

    def _on_enabled_change(self):
        resize_redraw(self)
        if self.on_enable_change_func:
            self.on_enable_change_func()

    text = widget.call_on_change("_text", resize_redraw)
    shrink_factor = widget.call_on_change("_shrink_factor", resize_redraw)
    underline = widget.call_on_change("_underline", resize_redraw)
    wrap = widget.call_on_change("_wrap", resize_redraw)
    bold = widget.call_on_change("_bold", resize_redraw)

    enabled = widget.call_on_change("_enabled", _on_enabled_change)

    align = widget.causes_redraw("_align")
    valign = widget.causes_redraw("_valign")

    color = widget.auto_reconfig("_color", "resolved", g.resolve_color_alias)
    resolved_color = widget.causes_redraw("_resolved_color")
    color_disabled = widget.auto_reconfig("_color_disabled", "resolved", g.resolve_color_alias)
    resolved_color_disabled = widget.causes_redraw("_resolved_color_disabled")
    base_font = widget.auto_reconfig("_base_font", "resolved", g.resolve_font_alias)
    resolved_base_font = widget.call_on_change("_resolved_base_font", resize_redraw)

    text_size = widget.auto_reconfig("_text_size", "resolved", g.resolve_text_size)
    resolved_text_size = widget.causes_redraw("_resolved_text_size")

    def __init__(self, parent, pos, size=(0, .05), anchor=constants.TOP_LEFT,
                 text=None, base_font=None, shrink_factor=0.875,
                 color=None, align=constants.CENTER, valign=constants.MID,
                 color_disabled=None, on_enable_change=None,
                 underline=-1, wrap=True, bold=False, text_size="default", **kwargs):
        kwargs.setdefault("background_color", "text_background")
        kwargs.setdefault("border_color", "text_border")
        super(Text, self).__init__(parent, pos, size, anchor, **kwargs)

        self.text = text
        self.base_font = base_font or "normal"
        self.color = color or "text"
        self.color_disabled = color_disabled or "text_disabled"
        self.shrink_factor = shrink_factor
        self.underline = underline
        self.align = align
        self.valign = valign
        self.wrap = wrap
        self.bold = bold
        self.text_size = text_size
        self.on_enable_change_func = on_enable_change
        self.enabled = True

    max_size = property(lambda self: min(len(self.resolved_base_font)-1,
                                         convert_font_size(self._resolved_text_size)))
    font = property(lambda self: self._font)

    def pick_font(self, dimensions):
        nice_size = self.pick_font_size(dimensions, False)
        mean_size = self.pick_font_size(dimensions)

        size = max(nice_size, mean_size - convert_font_size(5))

        return self.resolved_base_font[size]

    def font_bisect(self, test_font):
        left = 0
        right = (self.max_size or len(self.resolved_base_font)-1) + 1

        def test_size(size):
            font = self.resolved_base_font[size]
            font.set_bold(self.bold)
            result = test_font(font)
            font.set_bold(False)

            return result

        return do_bisect(left, right, test_size)

    def pick_font_size(self, dimensions, break_words=True):
        if dimensions[0]:
            width = int(dimensions[0] * self.shrink_factor)
        else:
            width = None
        height = int(dimensions[1] * self.shrink_factor)

        basic_line_count = self.text.count("\n") + 1

        def test_size(test_font):
            too_wide = False
            if width:
                if self.wrap:
                    try:
                        lines = split_wrap(self.text, test_font, width,
                                           break_words)
                    except WrapError:
                        lines = []
                        too_wide = True
                else:
                    lines = split_wrap(self.text, test_font, 0)
                    for line in lines:
                        if test_font.size(line)[0] > width:
                            too_wide = True
                            break
                line_count = len(lines)
            else:
                line_count = basic_line_count

            too_tall = (test_font.get_linesize() * line_count) > height

            return not (too_tall or too_wide)

        return self.font_bisect(test_size)

    def size_using_font(self, font, width=0):
        #Calculate the size of the text block.
        raw_width, raw_height = size_of_block(self.text, font, width)

        #Adjust for shrink_factor and borders.
        width = int(raw_width / self.shrink_factor) + 4
        height = int(raw_height / self.shrink_factor) + 4

        return width, height

    def calc_text_size(self, initial_dimensions):
        if not (initial_dimensions[0] and initial_dimensions[1]):
            if not self.max_size:
                raise ValueError("No font size given, but a dimension is 0.")

            max_font = self.resolved_base_font[self.max_size]
            if initial_dimensions[0] == initial_dimensions[1] == 0:
                # No size specified, use the natural size of the max font.
                width, height = self.size_using_font(max_font)
                return (width, height), max_font
            elif not initial_dimensions[1]:
                # Width specified, use the size of the max font, word-wrapped.
                text_width = int((initial_dimensions[0] - 4)
                                 * self.shrink_factor)
                width, height = self.size_using_font(max_font, width=text_width)
                return (initial_dimensions[0], height), max_font
            else:
                # Height specified.  Try the natural size of the max font.
                width, height = self.size_using_font(max_font)

                if height <= initial_dimensions[1]:
                    return (width, initial_dimensions[1]), max_font
                else:
                    # Too tall.  Run a binary search to find the largest font
                    # size that fits.
                    def test_size(font):
                        width, raw_height = size_of_block(self.text, font)
                        height = int(raw_height / self.shrink_factor) + 4
                        return height <= initial_dimensions[1]

                    font_size = self.font_bisect(test_size)
                    font = self.resolved_base_font[font_size]
                    width, height = self.size_using_font(font)

                    return (width, initial_dimensions[1]), font
        else:
            # Both sizes specified.  Search for a usable font size.
            return initial_dimensions, self.pick_font(initial_dimensions)

    def _calc_size(self):
        base_size = list(super(Text, self)._calc_size())

        if self.text is None:
            return tuple(base_size)
        else:
            # Determine the true size and font of the text area.
            text_size, font = self.calc_text_size(base_size)
            self._font = font
            return tuple(text_size)

    def redraw(self):
        super(Text, self).redraw()

        if self.text != None:
            self.print_text()

    @property
    def text_color(self):
        return self.resolved_color if self.enabled else self.resolved_color_disabled

    def print_text(self):
        # Mark the character to be underlined (if any).
        no_underline = [self.text_color, None, False]
        underline = [self.text_color, None, True]
        styles = [no_underline + [0]]
        if 0 <= self.underline < len(self.text):
            styles.insert(0, underline + [self.underline + 1])
            if self.underline != 0:
                styles.insert(0, no_underline + [self.underline])

        self.font.set_bold(self.bold)
        # Print the string itself.
        print_string(self.surface, self.text, (3, 2), self.font, styles,
                     self.align, self.valign, self.real_size, self.wrap)
        self.font.set_bold(False)

def text_changed(self):
    if self.text is None:
        new_len = 0
    else:
        new_len = len(self.text)
    if new_len != self.old_len:
        self.old_len = new_len
        self.needs_resize = True
    self.needs_redraw = True

class FastText(Text):
    """
       Reduces font searches by assuming a monospace font and single-line text.
    """
    text = widget.call_on_change("_text", text_changed)
    old_len = 0
    maybe_needs_refont = False

class EditableText(widget.FocusWidget, Text):
    cursor_pos = widget.causes_redraw("_cursor_pos")
    def __init__(self, parent, *args, **kwargs):
        self.allows_new_line = kwargs.pop("allows_new_line", False)
        self.allowed_characters = kwargs.pop("allowed_characters", None)
        
        super(EditableText, self).__init__(parent, *args, **kwargs)

        if self.text is None:
            self.text = ""

        self.cursor_pos = len(self.text)

    def add_hooks(self):
        super(EditableText, self).add_hooks()
        self.parent.add_handler(constants.KEYDOWN, self.handle_key, 10)
        self.parent.add_handler(constants.CLICK, self.handle_click)

    def remove_hooks(self):
        super(EditableText, self).remove_hooks()
        self.parent.remove_handler(constants.KEYDOWN, self.handle_key)
        self.parent.remove_handler(constants.CLICK, self.handle_click)

    def handle_key(self, event, require_focus=True):
        if require_focus and not self.has_focus:
            return
        assert event.type == pygame.KEYDOWN
        if event.key == pygame.K_BACKSPACE:
            if self.cursor_pos > 0:
                self.text = self.text[:self.cursor_pos - 1] \
                            + self.text[self.cursor_pos:]
                self.cursor_pos -= 1
        elif event.key == pygame.K_DELETE:
            if self.cursor_pos < len(self.text):
                self.text = self.text[:self.cursor_pos] \
                + self.text[self.cursor_pos + 1:]
        elif event.key == pygame.K_LEFT:
            self.cursor_pos = max(0, self.cursor_pos - 1)
        elif event.key == pygame.K_RIGHT:
            self.cursor_pos = min(len(self.text), self.cursor_pos + 1)
        elif event.key in (pygame.K_UP, pygame.K_HOME):
            self.cursor_pos = 0
        elif event.key in (pygame.K_DOWN, pygame.K_END):
            self.cursor_pos = len(self.text)
        elif event.key == pygame.K_ESCAPE:
            return
        elif event.unicode:
            char = event.unicode
            if char in (u"\r\n", u"\n", u"\r", u"\v", u"\f", u"\x1e", 
                        u"\x1c", u"\x1d", u"\x85", u"\u2028", u"\u2029"):
                if not self.allows_new_line:
                    return
                char = "\n"
            if self.allowed_characters is not None and char not in self.allowed_characters:
                return

            self.text = self.text[:self.cursor_pos] + char \
                        + self.text[self.cursor_pos:]
            self.cursor_pos += len(char)
        else:
            return

        raise constants.Handled

    hitbox = [0,0,0,0]

    def handle_click(self, event):
        if getattr(self, "collision_rect", None) is None:
            return
        elif not self.collision_rect.collidepoint(event.pos):
            return

        self.has_focus = True
        self.took_focus(self)

        self.font.set_bold(self.bold)

        click_x = event.pos[0] - self.collision_rect[0]
        click_y = event.pos[1] - self.collision_rect[1]

        if self.wrap:
            lines = split_wrap(self.text, self.font, self.real_size[0] - 4)
        else:
            lines = split_wrap(self.text, self.font, 0)

        line_size = self.font.get_linesize()
        self.hitbox[3] = line_size
        real_text_height = line_size * len(lines)

        line_y = 2
        if self.valign != constants.TOP \
           and real_text_height <= self.collision_rect.height - 4:
            excess_space = self.collision_rect.height - real_text_height
            if self.valign == constants.MID:
                line_y = excess_space // 2
            else: # self.valign == constants.BOTTOM
                line_y = excess_space

        char_offset = 0
        for line in lines:
            line_y += line_size
            char_offset += len(line)
            if line_y >= click_y:
                break

        char_offset -= len(line)

        self.hitbox[1] = line_y - line_size
        line_x = 3
        if self.align != constants.LEFT:
            line_width = self.font.size(line)[0]
            excess_space = self.collision_rect.width - line_width
            if self.align == constants.CENTER:
                line_x = excess_space // 2
            else: # self.align == constants.LEFT
                line_x = excess_space

        prev_width = 20000
        widths = get_widths(self.font, line)
        for index, width in enumerate(widths):
            if line_x + (width // 2) < click_x:
                line_x += width
                prev_width = width
            else:
                break
        else:
            index += 1
            width = 20000
        self.hitbox[0] = line_x - prev_width // 2
        self.hitbox[2] = prev_width - (prev_width // 2) + width // 2
        self.cursor_pos = char_offset + index

        self.font.set_bold(False)

    def redraw(self):
        super(EditableText, self).redraw()

        if self.wrap:
            lines = split_wrap(self.text, self.font, self.real_size[0] - 4)
        else:
            lines = split_wrap(self.text, self.font, 0)

        if not self.has_focus:
            return

        line_size = self.font.get_linesize()
        real_text_height = line_size * len(lines)

        line_y = 2
        if self.valign != constants.TOP \
           and real_text_height <= self.real_size[1] - 4:
            excess_space = self.real_size[1] - real_text_height
            if self.valign == constants.MID:
                line_y = excess_space // 2
            else: # self.valign == constants.BOTTOM
                line_y = excess_space

        char_offset = 0
        for line in lines:
            if char_offset + len(line) < self.cursor_pos:
                char_offset += len(line)
                line_y += line_size
            else:
                break

        after_char = self.cursor_pos - char_offset

        line_x = 3
        if self.align != constants.LEFT:
            line_width = self.font.size(line)[0]
            excess_space = self.real_size[0] - line_width
            if self.align == constants.CENTER:
                line_x = excess_space // 2
            else: # self.align == constants.LEFT
                line_x = excess_space

        line_x += self.font.size(line[:after_char])[0]

        self.surface.fill( self.resolved_color, (line_x, line_y, 1, line_size))

        if DEBUG:
            s = pygame.Surface(self.hitbox[2:]).convert_alpha()
            s.fill( (255,0,255,100) )
            self.surface.blit( s, self.hitbox)

class UpdateEditableText(EditableText):
    def _on_text_change(self):
        self.update_func(self.text)

    _text = widget.call_on_change("__text", _on_text_change)

    def __init__(self, *args, **kwargs):
        self.update_func = kwargs.pop("update_func", lambda value: None)
        super(UpdateEditableText, self).__init__(*args, **kwargs)

class SelectableText(Text):
    selected = widget.causes_redraw("_selected")

    selected_color = widget.auto_reconfig("_selected_color", "resolved", g.resolve_color_alias)
    resolved_selected_color = widget.causes_redraw("_resolved_selected_color")
    unselected_color = widget.auto_reconfig("_unselected_color", "resolved", g.resolve_color_alias)
    resolved_unselected_color = widget.causes_redraw("_resolved_unselected_color")

    def __init__(self, parent, pos, size, border_color = None,
                 unselected_color = None, selected_color = None, **kwargs):
        super(SelectableText, self).__init__(parent, pos, size, **kwargs)

        self.border_color = border_color or "text_border"
        self.selected_color = selected_color or "text_background_selected"
        self.unselected_color = unselected_color or "text_background_unselected"

        self.selected = False

    def redraw(self):
        if self.selected:
            self.background_color = self.selected_color
        else:
            self.background_color = self.unselected_color
        super(SelectableText, self).redraw()


class ProgressText(SelectableText):
    progress = widget.causes_redraw("_progress")
    
    progress_color = widget.auto_reconfig("_progress_color", "resolved", g.resolve_color_alias)
    resolved_progress_color = widget.causes_redraw("_resolved_progress_color")


    def __init__(self, parent, pos, size, *args, **kwargs):
        self.parent = parent
        self.progress = kwargs.pop("progress", 0)
        self.progress_color = kwargs.pop("progress", "progress_background_progress")
        kwargs.setdefault("border_color", "progress_border")
        kwargs.setdefault("selected_color", "progress_background_selected")
        kwargs.setdefault("unselected_color", "progress_background_unselected")
        super(ProgressText, self).__init__(parent, pos, size, **kwargs)

    def redraw(self):
        super(ProgressText, self).redraw()
        width, height = self.real_size
        self.surface.fill(self.resolved_progress_color,
                          (0, 0, width * self.progress, height))
        self.draw_borders()


class ChunkedText(Text):
    def update_text(self):
        self.text = "".join(self.chunks)

    chunks = widget.call_on_change("__chunks", update_text)

    def __init__(self, *args, **kwargs):
        chunks = kwargs.pop("chunks", ())
        super(ChunkedText, self).__init__(*args, **kwargs)

        self.chunks = chunks

class StyledText(ChunkedText):
    def resolve_styles(value):
        return tuple((g.resolve_color_alias(c), bg, u) for c, bg, u in value)
    
    styles = widget.auto_reconfig("_styles", "resolved", resolve_styles)
    resolved_styles = widget.causes_redraw("_resolved_styles")

    def __init__(self, *args, **kwargs):
        styles = kwargs.pop("styles", ())
        super(StyledText, self).__init__(*args, **kwargs)

        self.styles = styles

    def print_text(self):
        if self.styles:
            offset = 0
            styles = []
            for chunk, style in zip(self.chunks, self.resolved_styles):
                offset += len(chunk)
                styles.append(list(style) + [offset])
            styles[-1][-1] = 0

            print_string(self.surface, self.text, (3, 2), self.font, styles,
                         self.align, self.valign, self.real_size, self.wrap)
        else:
            super(StyledText, self).print_text()

class FastStyledText(FastText, StyledText):
    pass


def _make_prototype_handler(parent):
    def print_on_click(event):
        if event.button != 2 and not (event.button == 1
                                      and (pygame.key.get_mods() & pygame.KMOD_ALT)):
            return
        prefixes = ["|-", "| "]
        kids = [(child, 0) for child in parent.children]
        while kids:
            kid, depth = kids.pop()
            further_kids = [(child, depth+1) for child in kid.children]
            kids += further_kids

            prefix = ""
            if depth:
                prefix = prefixes[1] * (depth - 1) + prefixes[0]

            print(prefix + str(kid))
    return print_on_click

class ProtoWidget(EditableText):
    """Prototyping widget, for creating quick mockups.

       Usage:
       Type to name.
       Drag to move.
       Shift+Drag to resize.
       Control+Drag to duplicate. (children will not duplicate)
       Shift+Control+Drag to create a child.

       Right-click to delete.
       Middle-click or Alt+Click to write out location and size of each widget.
       """
    drag_state = -1

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("color", (0,0,0))
        kwargs.setdefault("border_color", (0,0,0))
        kwargs.setdefault("borders", constants.ALL)
        kwargs.setdefault("background_color", (255,255,255))
        super(ProtoWidget, self).__init__(*args, **kwargs)

    def add_hooks(self):
        super(ProtoWidget, self).add_hooks()
        self.parent.add_handler(constants.DRAG, self.handle_drag)
        self.parent.add_handler(constants.CLICK, self.handle_click)

        if not isinstance(self.parent, ProtoWidget) \
           and not getattr(self.parent, "demo_mode", False):
            self.parent.demo_mode = True
            self.parent.add_handler(constants.CLICK, _make_prototype_handler(self.parent))

    def remove_hooks(self):
        self.parent.remove_handler(constants.DRAG, self.handle_drag)
        self.parent.remove_handler(constants.CLICK, self.handle_click)
        super(ProtoWidget, self).remove_hooks()

    def handle_drag(self, event):
        if self.drag_state == -1:
            start_pos = tuple(event.pos[i]-event.rel[i] for i in range(2))
            if self.is_over(start_pos):
                for child in self.children:
                    if child.is_over(start_pos):
                        self.drag_state = 0
                        return
                real_pos = self.collision_rect[:2]
                self.mouse_rel = tuple(real_pos[i]-start_pos[i]
                                                     for i in range(2))

                mod_keys = pygame.key.get_mods()
                shift = mod_keys & pygame.KMOD_SHIFT
                control = mod_keys & pygame.KMOD_CTRL
                if shift and control:
                    self.drag_state = 0
                    new_size = tuple(d/2 for d in self.size)
                    pw=ProtoWidget(self, (0,0), new_size,
                                  self.anchor,
                                  background_color = self.background_color,
                                  border_color = self.border_color,
                                  borders = self.borders)
                    pw.drag_state = 0
                elif shift:
                    self.drag_state = 2
                elif control:
                    self.drag_state = 0
                    pw=ProtoWidget(self.parent, self.pos, self.size, self.anchor,
                                  background_color = self.background_color,
                                  border_color = self.border_color,
                                  borders = self.borders)
                    pw.drag_state = 1
                    pw.mouse_rel = self.mouse_rel
                else:
                    self.drag_state = 1
            else:
                self.drag_state = 0

        if self.drag_state <= 0:
            return

        if self.parent:
            parent_rect = self.parent.collision_rect
        else:
            parent_rect = pygame.Rect((0,0) + g.real_screen_size)

        if self.drag_state == 1:
            mouse_pos = pygame.mouse.get_pos()
            new_real_pos = tuple(self.mouse_rel[i] + mouse_pos[i] for i in range(2))

            new_rel_pos = tuple(new_real_pos[i] - parent_rect[i] for i in range(2))

            new_unit_pos = tuple( max(0,(new_rel_pos[i] / float(g.real_screen_size[i])))
                                     for i in range(2))

            new_pct_pos = tuple( int( (new_unit_pos[i] * 100) + 0.5)
                                   for i in range(2))

            self.pos = tuple(new_pct_pos[i] / 100. for i in range(2))

            raise constants.Handled
        elif self.drag_state == 2:
            mouse_pos = pygame.mouse.get_pos()
            new_size = tuple(mouse_pos[i] - self.collision_rect[i] for i in range(2))

            unit_size = tuple(max(0,new_size[i] / float(g.real_screen_size[i]))
                                    for i in range(2))

            pct_size = tuple( int( (unit_size[i] * 100) + 0.5)
                                   for i in range(2))

            self.size = tuple(pct_size[i] / 100. for i in range(2))

            raise constants.Handled

    def handle_click(self, event):
        if event.button == 3 and self.is_over(event.pos):
            mine = True
            for child in self.children:
                if child.is_over(event.pos):
                    mine = False
                    break
            if mine:
                self.remove_hooks()
                self.parent.needs_redraw = True
        if self.drag_state > 0:
            self.drag_state = -1
            #raise constants.Handled
        else:
            self.drag_state = -1

    def __str__(self):
        return "%s pos: (%.2f, %.2f), size: (%.2f, %.2f)" % \
           ((self.text,) + self.pos +        self.size)
