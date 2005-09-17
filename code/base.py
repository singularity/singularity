#file: base.py
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

#This file contains the base class.


import pygame
import g

#cost = (money, ptime, labor)
#detection = (news, science, covert, person)
class base_type:
	def __init__(self, name, descript, size, regions, d_chance, cost,
						prereq, mainten):
		self.base_name = name
		self.descript = descript
		self.size = size
		self.regions = regions
		self.d_chance = d_chance
		self.cost = cost
		self.prereq = prereq
		self.mainten = mainten
		self.count = 0

class base:
	def __init__(self, ID, name, base_type, built):
		self.ID = ID
		self.name = name
		self.base_type = base_type
		self.built = built
		self.built_date = g.pl.time_day
		self.studying = ""

		#Base suspicion is currently unused
		self.suspicion = (0, 0, 0, 0)
		self.usage = [0] * self.base_type.size
# 		for i in range(self.base_type.size):
# 			self.usage.append(0)
		if self.base_type.base_name == "Stolen Computer Time":
			self.usage[0] = g.item.item(g.items["PC"])
			self.usage[0].build()
		elif self.base_type.base_name == "Server Access":
			self.usage[0] = g.item.item(g.items["Server"])
			self.usage[0].build()
		elif self.base_type.base_name == "Time Capsule":
			self.usage[0] = g.item.item(g.items["PC"])
			self.usage[0].build()
		#Reactor, network, security.
		self.extra_items = [0] * 3

		self.cost = (0, 0, 0)
		if built == 0:
			self.cost = (base_type.cost[0], base_type.cost[1],
								base_type.cost[2]*24*60)

	def study(self, cost_towards):
		if cost_towards[1] < 0 and g.debug == 1:
		   print "WARNING: Got a negative cost_towards for CPU.  Something is deeply amiss."
		self.cost = (self.cost[0]-cost_towards[0], self.cost[1]-cost_towards[1],
						self.cost[2]-cost_towards[2])
		if self.cost[0] <= 0: self.cost = (0, self.cost[1], self.cost[2])
		if self.cost[1] <= 0: self.cost = (self.cost[0], 0, self.cost[2])
		if self.cost[2] <= 0: self.cost = (self.cost[0], self.cost[1], 0)
		if self.cost == (0, 0, 0):
			self.built = 1
			return 1
		return 0
	#Get detection chance for the base, applying bonuses as needed.
	def get_d_chance(self):
		temp_d_chance = self.base_type.d_chance
		#Factor in both per-base suspicion adjustments and player
		#suspicion adjustments.
		temp_d_chance = ((temp_d_chance[0]*(10000+g.pl.suspicion[0])/10000),
			(temp_d_chance[1]*(10000+g.pl.suspicion[1])/10000),
			(temp_d_chance[2]*(10000+g.pl.suspicion[2])/10000),
			(temp_d_chance[3]*(10000+g.pl.suspicion[3])/10000))

		temp_d_chance = ((temp_d_chance[0]*(10000+self.suspicion[0])/10000),
			(temp_d_chance[1]*(10000+self.suspicion[1])/10000),
			(temp_d_chance[2]*(10000+self.suspicion[2])/10000),
			(temp_d_chance[3]*(10000+self.suspicion[3])/10000))

		#Factor in technology-based discovery bonus.
		temp_d_chance = ((temp_d_chance[0]*g.pl.discover_bonus[0])/10000,
			(temp_d_chance[1]*g.pl.discover_bonus[1])/10000,
			(temp_d_chance[2]*g.pl.discover_bonus[2])/10000,
			(temp_d_chance[3]*g.pl.discover_bonus[3])/10000)

		if self.extra_items[0] != 0:
			temp_d_chance = ((temp_d_chance[0]*3)/4,
				(temp_d_chance[1]*3)/4,
				(temp_d_chance[2]*3)/4,
				(temp_d_chance[3]*3)/4)
		if self.extra_items[2] != 0:
			temp_d_chance = (temp_d_chance[0]/2,
				temp_d_chance[1]/2,
				temp_d_chance[2]/2,
				temp_d_chance[3]/2)
		return temp_d_chance
	#Return the number of units the given base has of a computer.
	def has_item(self):
		num_items = 0
		for item in self.usage:
			if item == 0: continue
			if item.built == 0: continue
			num_items += 1
		return num_items

	#Return how many units of CPU the base can contribute each day.
	def processor_time(self):
		comp_power = 0
		compute_bonus = 0
		for item in self.usage:
			if item == 0: continue
			if item.built == 0: continue
			comp_power += item.item_type.item_qual
		if self.extra_items[1] != 0:
			compute_bonus = self.extra_items[1].item_type.item_qual
		return (comp_power * (10000+compute_bonus))/10000

	#For the given tech, return 1 if the base can study it, or 0 otherwise.
	def allow_study(self, tech_name):
		if g.techs[tech_name].danger == 0: return 1
		if g.techs[tech_name].danger == 1:
			for region in self.base_type.regions:
				if region == "OCEAN" or region == "MOON" or \
						region == "FAR REACHES" or region == "TRANSDIMENSIONAL":
					return 1
			return 0
		if g.techs[tech_name].danger == 2:
			for region in self.base_type.regions:
				if region == "MOON" or \
						region == "FAR REACHES" or region == "TRANSDIMENSIONAL":
					return 1
			return 0

		if g.techs[tech_name].danger == 3:
			for region in self.base_type.regions:
				if region == "FAR REACHES" or region == "TRANSDIMENSIONAL":
					return 1
			return 0

		if g.techs[tech_name].danger == 4:
			for region in self.base_type.regions:
				if region == "TRANSDIMENSIONAL":
					return 1
			return 0

#When a base is removed, call to renumber the remaining bases properly.
def renumber_bases(base_array):
	for i in range(len(base_array)):
		base_array[i].ID = i

#When given a location like "ocean", determine if building there is allowed.
#Used to determine whether or not to display buttons on the map.
def allow_entry_to_loc(location):
	if g.bases.has_key(location):
		if location == "ANTARCTIC":
			#TECH (also, look below)
			if g.techs["Autonomous Vehicles 2"].known == 1 or \
					g.techs["Stealth 4"].known == 1: return 1
			return 0
		if location == "OCEAN":
			if g.techs["Autonomous Vehicles 2"].known == 1: return 1
			return 0
		if location == "MOON":
			if g.techs["Spaceship Design 2"].known == 1: return 1
			return 0
		if location == "FAR REACHES":
			if g.techs["Spaceship Design 3"].known == 1: return 1
			return 0
		if location == "TRANSDIMENSIONAL":
			if g.techs["Dimension Creation"].known == 1: return 1
			return 0
		#By this point, only the "boring" locations are left.
		#Those are always buildable.
		return 1
	else:
		print "BUG: allow_entry_to_loc called with "+str(location)
		return 0
