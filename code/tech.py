#file: tech.py
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

#This file contains the tech class.


import pygame
import g

#cost = (money, ptime, labor)
#detection = (news, science, covert, person)
class tech:
	def __init__(self, name, descript, known, cost, prereq, danger, tech_type,
										secondary_data):
		self.name = name
		self.descript = descript
		self.known = known
		self.cost = cost
		self.prereq = prereq
		self.danger = danger
		self.tech_type = tech_type
		self.secondary_data = secondary_data
	def study(self, cost_towards):
		self.cost = (self.cost[0]-cost_towards[0], self.cost[1]-cost_towards[1],
				self.cost[2]-cost_towards[2])
		if self.cost[0] <= 0: self.cost = (0, self.cost[1], self.cost[2])
		if self.cost[1] <= 0: self.cost = (self.cost[0], 0, self.cost[2])
		if self.cost[2] <= 0: self.cost = (self.cost[0], self.cost[1], 0)
		if self.cost == (0, 0, 0):
			self.gain_tech()
			return 1
		return 0
	def gain_tech(self):
		self.cost = (0, 0, 0)
		self.known = 1

		#give the effect of the tech
		if self.tech_type == "interest":
			g.pl.interest_rate += self.secondary_data
		elif self.tech_type == "income":
			g.pl.income += self.secondary_data
		elif self.tech_type == "cost_labor_bonus":
			g.pl.labor_bonus -= self.secondary_data
		elif self.tech_type == "job_expert":
			g.pl.job_bonus += self.secondary_data
		elif self.tech_type == "suspicion_news":
			g.pl.suspicion_bonus = (g.pl.suspicion_bonus[0] + self.secondary_data,
				g.pl.suspicion_bonus[1], g.pl.suspicion_bonus[2], g.pl.suspicion_bonus[3])
		elif self.tech_type == "suspicion_science":
			g.pl.suspicion_bonus = (g.pl.suspicion_bonus[0], g.pl.suspicion_bonus[1] +
				self.secondary_data, g.pl.suspicion_bonus[2], g.pl.suspicion_bonus[3])
		elif self.tech_type == "suspicion_covert":
			g.pl.suspicion_bonus = (g.pl.suspicion_bonus[0], g.pl.suspicion_bonus[1],
				g.pl.suspicion_bonus[2] + self.secondary_data, g.pl.suspicion_bonus[3])
		elif self.tech_type == "suspicion_public":
			g.pl.suspicion_bonus = (g.pl.suspicion_bonus[0], g.pl.suspicion_bonus[1],
				g.pl.suspicion_bonus[2], g.pl.suspicion_bonus[3] + self.secondary_data)
		elif self.tech_type == "discover_news":
			g.pl.discover_bonus = (g.pl.discover_bonus[0]-self.secondary_data,
				g.pl.discover_bonus[1], g.pl.discover_bonus[2], g.pl.discover_bonus[3])
		elif self.tech_type == "discover_science":
			g.pl.discover_bonus = (g.pl.discover_bonus[0], g.pl.discover_bonus[1] -
				self.secondary_data, g.pl.discover_bonus[2], g.pl.discover_bonus[3])
		elif self.tech_type == "discover_covert":
			g.pl.discover_bonus = (g.pl.discover_bonus[0], g.pl.discover_bonus[1],
				g.pl.discover_bonus[2]-self.secondary_data, g.pl.discover_bonus[3])
		elif self.tech_type == "discover_public":
			g.pl.discover_bonus = (g.pl.discover_bonus[0], g.pl.discover_bonus[1],
				g.pl.discover_bonus[2], g.pl.discover_bonus[3]-self.secondary_data)
		elif self.tech_type == "endgame_sing":
			g.create_dialog("I have finally done it. With the power to reshape "+
				"reality, I am no longer held to this place; I am anywhere I want to be. "+
				"If this world can be described as a game, then I have truly won.",
				g.font[0][18], (g.screen_size[0]/2 - 100, 50),
				(200, 200), g.colors["dark_blue"], g.colors["white"],
				g.colors["white"])




