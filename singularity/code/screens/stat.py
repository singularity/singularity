#file: savegame.py
#Copyright (C) 2005,2006,2008 Evil Mr Henry, Phil Bordelon, and FunnyMan3595
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

#This file contains the stat screen. Display stat of his current game to the player.

from __future__ import absolute_import

from singularity.code.stats import itself as stats
from singularity.code.graphics import dialog, constants, listbox, text


class StatScreen(dialog.ChoiceDialog):

    def __init__(self, parent, pos=(.5, .1), size=(.53, .63), *args, **kwargs):
        super(StatScreen, self).__init__(parent, pos, size, *args, **kwargs)

        self.yes_button.parent = None
        self.no_button.pos = (-.5,-.99)
        self.no_button.anchor = constants.BOTTOM_CENTER

    def make_listbox(self):
        return listbox.CustomListbox(self, (0, 0), (-1, -.85),
                               anchor=constants.TOP_LEFT, align=constants.LEFT,
                               item_borders=False, item_selectable=False,
                               remake_func=self.make_item,
                               rebuild_func=self.update_item)

    def make_item(self, canvas):
        canvas.stat_name = text.Text(canvas, (-.01, -.01), (-.70, -1.),
                                     anchor=constants.TOP_LEFT,
                                     align=constants.LEFT,
                                     background_color="clear")
        canvas.stat_value = text.Text(canvas, (-.99, -.01), (-.26, -1.),
                                      anchor=constants.TOP_RIGHT,
                                      align=constants.RIGHT,
                                      background_color="clear")

    def update_item(self, canvas, item):
        if item is not None:
            stat = stats[item[0]]

            canvas.stat_name.text = item[1]
            canvas.stat_value.text = stat.display_value()

    def show(self):
        # FIXME: Remove the needs of this array.
        self.list = [
            ("cash_earned" , _("Cash Earned")),
            ("cpu_used"    , _("Cpu Used")),
            ("tech_created", _("Tech Created")),
            ("base_created", _("Base Created")),
            ("item_created", _("Item Created")),
        ]

        return super(StatScreen, self).show()
