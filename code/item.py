#file: item.py
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

#This file contains the item class.

import buyable

class Item_Class(buyable.Buyable_Class):
    def __init__(self, name, description, cost, prerequisites, item_type, 
            item_qual, buildable):
        super(Item_Class, self).__init__(name, description, cost, prerequisites,
                                         type="item")

        self.item_type = item_type
        self.item_qual = item_qual
        self.buildable = buildable
        if self.buildable == ["all"]:
            self.buildable = ["N AMERICA", "S AMERICA", "EUROPE", "ASIA",
            "AFRICA", "ANTARCTIC", "OCEAN", "MOON", "FAR REACHES",
            "TRANSDIMENSIONAL", "AUSTRALIA"]
        if self.buildable == ["pop"]:
            self.buildable = ["N AMERICA", "S AMERICA", "EUROPE", "ASIA",
            "AFRICA", "AUSTRALIA"]

class Item(buyable.Buyable):
    def __init__(self, item_type, base = None):
        super(Item, self).__init__(item_type)
        self.item_qual = item_type.item_qual

        self.base = base
