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

import pygame

import widget
import constants
import g

DEBUG = False

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
                        raise WrapError, message % word
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

def causes_refont(data_member):
    return widget.set_on_change(data_member, "needs_refont")

class Text(widget.BorderedWidget):
    text = causes_refont("_text")
    base_font = causes_refont("_base_font")
    color = widget.causes_redraw("_color")
    shrink_factor = causes_refont("_shrink_factor")
    underline = causes_refont("_underline")
    align = widget.causes_redraw("_align")
    valign = widget.causes_redraw("_valign")
    wrap = causes_refont("_wrap")
    bold = causes_refont("_bold")
    oversize = causes_refont("_oversize")

    needs_refont = widget.causes_resize("_needs_refont")

    lorem_ipsum = {}

    def __init__(self, parent, pos, size=(0, .05), anchor=constants.TOP_LEFT,
                 text=None, base_font=None, shrink_factor=1,
                 color=None, align=constants.CENTER, valign=constants.MID,
                 underline=-1, wrap=True, bold=False, oversize=False, **kwargs):
        super(Text, self).__init__(parent, pos, size, anchor, **kwargs)

        self.needs_refont = True

        self.text = text
        self.base_font = base_font or g.font[0]
        self.color = color or g.colors["white"]
        self.shrink_factor = shrink_factor
        self.underline = underline
        self.align = align
        self.valign = valign
        self.wrap = wrap
        self.bold = bold
        self.oversize = oversize

    def pick_font(self, dimensions=None):
        if dimensions and self.needs_refont:
            nice_size = self.pick_font_size(dimensions, False)
            mean_size = self.pick_font_size(dimensions)

            if nice_size > mean_size - 5:
                size = nice_size
            else:
                size = mean_size
            self._font = self.base_font[size]

            self.needs_refont = False

        return self._font

    font = property(pick_font)

    def pick_font_size(self, dimensions, break_words=True):
        if dimensions[0]:
            width = dimensions[0] - 4
        else:
            width = None
        height = dimensions[1]

        basic_line_count = self.text.count("\n") + 1

        # Run a binary search for the best font size.
        # Thanks to bisect.bisect_left for the basic implementation.
        left = 8
        if self.oversize or self.base_font[0] not in Text.lorem_ipsum:
            right = len(self.base_font)
        else:
            right = Text.lorem_ipsum[self.base_font[0]].font_size

        while left + 1 < right:
            test_index = (left + right) // 2
            test_font = self.base_font[test_index]
            test_font.set_bold(self.bold)

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
            if too_tall or too_wide:
                right = test_index
            else:
                left = test_index

            test_font.set_bold(False)

        return left

    def calc_text_size(self, dimensions=None):
        if dimensions == None:
            dimensions = self.real_size

        # Calculate the text height.
        height = int( (dimensions[1] - 4) * self.shrink_factor )
        width = dimensions[0]

        return width, height

    def _calc_size(self):
        base_size = list(super(Text, self)._calc_size())

        if self.text != None:
            # Determine the true size of the text area.
            text_size = self.calc_text_size(base_size)

            # Pick a font based on that size.
            self.needs_refont = True
            font = self.pick_font(text_size)

            # If the width is unspecified, calculate it from the font and text.
            if base_size[0] == 0:
                base_size[0] = font.size(self.text)[0] + 16
        return tuple(base_size)

    def redraw(self):
        super(Text, self).redraw()

        if self.text != None:
            # Mark the character to be underlined (if any).
            no_underline = [self.color, None, False]
            underline = [self.color, None, True]
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

_lorem_ipsum = '''Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.'''
class _LoremIpsum(Text):
    def __init__(self, base_font):
        super(_LoremIpsum, self).__init__(None, (0,0), (.35, .4),
                                          base_font=base_font,
                                          text=_lorem_ipsum, oversize=True)
        Text.lorem_ipsum[base_font[0]] = self
        self.last_resolution = None

    _calc_size = widget.Widget._calc_size

    def get_font_size(self):
        if self.last_resolution != g.screen_size:
            self._font_size = self.pick_font_size(self._calc_size())
            self.last_resolution = g.screen_size
        return self._font_size

    font_size = property(get_font_size)

class FastText(Text):
    """Reduces font searches by assuming a monospace font, single-line text,
       and a fixed widget width."""
    text = widget.set_on_change("_text", "maybe_needs_refont")
    _text = widget.causes_redraw("__text")
    old_text = ""
    maybe_needs_refont = False

    def redraw(self):
        self.pick_font(self.calc_text_size(self._real_size))
        super(FastText, self).redraw()

    def pick_font(self, dimensions=None):
        if self.maybe_needs_refont and not self.needs_refont:
            if len(self.old_text) != len(self.text):
                self.old_text = self.text
                self.needs_refont = True
        self.maybe_needs_refont = False

        return super(FastText, self).pick_font(dimensions)

class EditableText(widget.FocusWidget, Text):
    cursor_pos = widget.causes_redraw("_cursor_pos")
    def __init__(self, parent, *args, **kwargs):
        super(EditableText, self).__init__(parent, *args, **kwargs)

        if self.text == None:
            self.text = ""

        self.cursor_pos = len(self.text)

    def add_hooks(self):
        super(EditableText, self).add_hooks()
        self.parent.add_handler(constants.KEYDOWN, self.handle_key, 150)
        self.parent.add_handler(constants.CLICK, self.handle_click)

    def remove_hooks(self):
        super(EditableText, self).remove_hooks()
        self.parent.remove_handler(constants.KEYDOWN, self.handle_key)
        self.parent.remove_handler(constants.CLICK, self.handle_click)

    def handle_key(self, event):
        if not self.has_focus:
            return
        assert event.type == pygame.KEYDOWN
        if event.key == pygame.K_BACKSPACE:
            if self.cursor_pos > 0:
                self.text = self.text[:self.cursor_pos - 1] \
                            + self.text[self.cursor_pos:]
                self.cursor_pos -= 1
        elif event.key == pygame.K_LEFT:
            self.cursor_pos = max(0, self.cursor_pos - 1)
        elif event.key == pygame.K_RIGHT:
            self.cursor_pos = min(len(self.text), self.cursor_pos + 1)
        elif event.key == pygame.K_UP:
            self.cursor_pos = 0
        elif event.key == pygame.K_DOWN:
            self.cursor_pos = len(self.text)
        elif event.unicode:
            char = event.unicode
            if char == "\r":
                char = "\n"
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

        self.surface.fill( self.color, (line_x, line_y, 1, line_size))

        if DEBUG:
            s = pygame.Surface(self.hitbox[2:]).convert_alpha()
            s.fill( (255,0,255,100) )
            self.surface.blit( s, self.hitbox)


class SelectableText(Text):
    selected = widget.causes_redraw("_selected")
    selected_color = widget.causes_redraw("_selected_color")
    unselected_color = widget.causes_redraw("_unselected_color")

    def __init__(self, parent, pos, size, border_color = None,
                 unselected_color = None, selected_color = None, **kwargs):
        super(SelectableText, self).__init__(parent, pos, size, **kwargs)

        self.border_color = border_color or g.colors["white"]
        self.selected_color = selected_color or g.colors["light_blue"]
        self.unselected_color = unselected_color or g.colors["dark_blue"]

        self.selected = False

    def redraw(self):
        if self.selected:
            self.background_color = self.selected_color
        else:
            self.background_color = self.unselected_color
        super(SelectableText, self).redraw()


class ProgressText(SelectableText):
    progress = widget.causes_redraw("_progress")
    progress_color = widget.causes_redraw("_progress_color")
    def __init__(self, parent, *args, **kwargs):
        self.parent = parent
        self.progress = kwargs.pop("progress", 0)
        self.progress_color = kwargs.pop("progress", g.colors["blue"])
        super(ProgressText, self).__init__(parent, pos, size, **kwargs)

    def redraw(self):
        super(ProgressText, self).redraw()
        width, height = self.real_size
        self.surface.fill(self.progress_color,
                          (0, 0, width * self.progress, height))
        self.draw_borders()
