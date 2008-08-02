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

def strip_to_null(a_string):
    if a_string[0] == " ":
        a_string = "\0" + a_string[1:]
    if a_string[-1] == " ":
        a_string =  a_string[:-1] + "\0"
    return a_string

# Splits a string into lines based on newline and word wrapping.
def split_wrap(text, font, wrap_at):
    raw_lines = text.split("\n")
    lines = []

    for raw_line in raw_lines:
        if font.size(raw_line)[0] <= wrap_at:
            lines.append(raw_line + "\0")
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
                elif word_size < wrap_at / 2:
                    lines.append(strip_to_null(line))
                    line = word
                    pos = word_size
                else:
                    widths = [m[4] for m in font.metrics(word)]
                    for index, char in enumerate(word):
                        width = widths[index]
                        if pos + width <= wrap_at:
                            line += char
                            pos += width
                        else:
                            lines.append(strip_to_null(line))
                            line = char
                            pos = width
            if line:
                lines.append(strip_to_null(line))
    return lines

def _do_print(surface, text, xy, font, color):
    if font.size(text)[0] == 0:
        return
    rendered_text = font.render(text, True, color)
    surface.blit(rendered_text, xy)

def print_string(surface, string_to_print, xy, font, color, underline_char,
                 align, valign, dimensions):
    wrap_at = dimensions[0] - 4
    height = dimensions[1] - 4
    lines = split_wrap(string_to_print, font, wrap_at)

    xy = [2,2]
    if valign != constants.TOP:
        vsize = len(lines) * font.get_linesize()
        if vsize <= height:
            excess_space = height - vsize
            if valign == constants.MID:
                xy[1] += excess_space // 2
            else: # valign == constants.BOTTOM
                xy[1] += excess_space
    
    for line in lines:
        xy[0] = 2
        if align != constants.LEFT:
            width = font.size(line)[0]
            excess_space = wrap_at - width
            if align == constants.CENTER:
                xy[0] += excess_space // 2
            else: # align == constants.RIGHT
                xy[0] += excess_space

        if 0 <= underline_char < len(line):
            before = line[:underline_char]
            at = line[underline_char]
            if at == '\0':
                at = " "
            after = line[underline_char+1:]

            _do_print(surface, before, xy, font, color)
            xy[0] += font.size(before)[0]

            font.set_underline(True)
            _do_print(surface, at, xy, font, color)
            font.set_underline(False)
            xy[0] += font.size(at)[0]

            _do_print(surface, after, xy, font, color)
        else:
            _do_print(surface, line, xy, font, color)

        underline_char -= len(line)
        xy[1] += font.get_linesize()

class Text(widget.BorderedWidget):
    text = widget.causes_rebuild("_text")
    base_font = widget.causes_rebuild("_base_font")
    color = widget.causes_rebuild("_color")
    shrink_factor = widget.causes_rebuild("_shrink_factor")
    underline = widget.causes_rebuild("_underline")
    align = widget.causes_rebuild("_align")
    valign = widget.causes_rebuild("_valign")

    bounding_rect = widget.set_on_change("_bounding_rect", "needs_refont")
    _base_font = widget.set_on_change("__base_font", "needs_refont")
    _text = widget.set_on_change("__text", "needs_refont")
    _shrink_factor = widget.set_on_change("__shrink_factor", "needs_refont")

    def __init__(self, parent, pos, size = (0, -.05), 
                 anchor = constants.TOP_LEFT, text = "", base_font = None,
                 color = None, shrink_factor = 1, underline = -1,
                 align = constants.CENTER, valign = constants.MID, **kwargs):
        super(Text, self).__init__(parent, pos, size, anchor, **kwargs)

        self.needs_refont = True
        
        self.text = text
        self.base_font = base_font or g.font[0]
        self.color = color or g.colors["white"]
        self.shrink_factor = shrink_factor
        self.underline = underline
        self.align = align
        self.valign = valign

    def pick_font(self, dimensions = None):
        if dimensions and self.needs_refont:
            self.needs_refont = False

            if dimensions[0]:
                width = dimensions[0] - 4
            else:
                width = None
            height = dimensions[1]

            basic_line_count = self.text.count("\n") + 1

            # Run a binary search for the best font size.
            # Thanks to bisect.bisect_left for the basic implementation.
            left = 8
            right = len(self.base_font)

            while left + 1 < right:
                test_index = (left + right) // 2
                test_font = self.base_font[test_index]

                if width:
                    line_count = len(split_wrap(self.text, test_font, width))
                else:
                    line_count = basic_line_count

                if ( test_font.get_linesize() * line_count ) > height:
                    right = test_index
                else:
                    left = test_index

            self._font = self.base_font[left]

        return self._font

    font = property(pick_font)

    def _calc_size(self):
        base_size = list(super(Text, self)._calc_size())

        if self.text:
            # Calculate the font height.
            height = int( (base_size[1] - 4) * self.shrink_factor )

            # Pick a font based on that height (and the width, if set).
            font = self.pick_font((base_size[0], height))

            # If the width is unspecified, calculate it from the font and text.
            if base_size[0] == 0:
                base_size[0] = font.size(self.text)[0] + 16
        return tuple(base_size)

    def rebuild(self):
        super(Text, self).rebuild()

        if self.text:
            # Print the text itself
            print_string(self.internal_surface, self.text, (2, 2), self.font, 
                         self.color, self.underline, self.align, self.valign,
                         self.real_size) 

class EditableText(Text):
    cursor_pos = widget.causes_rebuild("_cursor_pos")
    def __init__(self, parent, *args, **kwargs):
        super(EditableText, self).__init__(parent, *args, **kwargs)

        self.cursor_pos = len(self.text)
        if self.parent:
            self.parent.add_handler(constants.KEYDOWN, self.handle_key, 150)
            self.parent.add_handler(constants.CLICK, self.handle_click)

    def handle_key(self, event):
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
            self.text = self.text[:self.cursor_pos] + event.unicode \
                        + self.text[self.cursor_pos:]
            self.cursor_pos += len(event.unicode)
        else:
            return

        raise constants.Handled

    def handle_click(self, event):
        if not self.collision_rect.collidepoint(event.pos):
            return

        click_x = event.pos[0] - self.collision_rect[0]
        click_y = event.pos[1] - self.collision_rect[1]

        lines = split_wrap(self.text, self.font, self.real_size[0] - 4)
        line_size = self.font.get_linesize()
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
            if line_y < click_y:
                char_offset += len(line)
                continue

            line_x = 2
            if self.align != constants.LEFT:
                line_width = self.font.size(line)[0]
                excess_space = self.collision_rect.width - line_width
                if self.align == constants.CENTER:
                    line_x = excess_space // 2
                else: # self.align == constants.LEFT
                    line_x = excess_space

            widths = [m[4] for m in self.font.metrics(line)]
            for index, width in enumerate(widths):
                if line_x + (width // 2) > click_x:
                    line_x += width
                else:
                    break
            self.cursor_pos = char_offset + index

    def rebuild(self):
        super(EditableText, self).rebuild()

        lines = split_wrap(self.text, self.font, self.real_size[0] - 4)
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

        line_x = 2
        if self.align != constants.LEFT:
            line_width = self.font.size(line)[0]
            excess_space = self.real_size[0] - line_width
            if self.align == constants.CENTER:
                line_x = excess_space // 2
            else: # self.align == constants.LEFT
                line_x = excess_space

        line_x += self.font.size(line[:after_char])[0]

        self.internal_surface.fill( self.color, 
                                    (line_x, line_y, 1, line_size))


class SelectableText(Text):
    selected = widget.causes_rebuild("_selected")
    selected_color = widget.causes_rebuild("_selected_color")
    unselected_color = widget.causes_rebuild("_unselected_color")

    def __init__(self, parent, pos, size, border_color = None,
                 unselected_color = None, selected_color = None, **kwargs):
        super(SelectableText, self).__init__(parent, pos, size, **kwargs)

        self.border_color = border_color or g.colors["white"]
        self.selected_color = selected_color or g.colors["light_blue"]
        self.unselected_color = unselected_color or g.colors["dark_blue"]

        self.selected = False

    def rebuild(self):
        if self.selected:
            self.background_color = self.selected_color
        else:
            self.background_color = self.unselected_color
        super(SelectableText, self).rebuild()
