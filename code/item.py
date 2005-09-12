#file: item.py
#Copyright (C) 2005 Free Software Foundation
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

import pygame
import g

class item_class:
	def __init__(self, name, descript, cost, prereq, item_type, item_qual):
		self.name = name
		self.descript = descript
		self.cost = cost
		self.prereq = prereq
		self.item_type = item_type
		self.item_qual = item_qual

class item:
	def __init__(self, item_type):
		self.item_type = item_type
		self.cost = item_type.cost
		self.built = 0
	def study(self, cost_towards):
		self.cost = (self.cost[0]-cost_towards[0], self.cost[1]-cost_towards[1],
				self.cost[2]-cost_towards[2])
		if self.cost[0] <= 0: self.cost = (0, self.cost[1], self.cost[2])
		if self.cost[1] <= 0: self.cost = (self.cost[0], 0, self.cost[2])
		if self.cost[2] <= 0: self.cost = (self.cost[0], self.cost[1], 0)
		if self.cost == (0, 0, 0):
			self.build()
			return 1
		return 0
	def build(self):
		self.cost = (0, 0, 0)
		self.built = 1


