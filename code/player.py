#file: player.py
#Copyright (C) 2005 Evil Mr Henry and Phil Bordelon
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

#This file contains the player class.

import pygame
import g

class player_class:
	def __init__(self, cash, time_sec=0, time_min=0, time_hour=0, time_day=0):
		self.cash = cash
		self.time_sec = time_sec
		self.time_min = time_min
		self.time_hour = time_hour
		self.time_day = time_day
		self.interest_rate = 1
		self.income = 0
		self.cpu_for_day = 0
		self.labor_bonus = 10000
		self.job_bonus = 10000
		self.discover_bonus = (10000, 10000, 10000, 10000)
		self.suspicion_bonus = (1, 1, 1, 1)
		self.suspicion = (0, 0, 0, 0)

	def give_time(self, time_sec):
		needs_refresh = 0
		store_last_minute = self.time_min
		store_last_day = self.time_day
		time_min = 0
		time_hour = 0
		time_day = 0
		self.time_sec += time_sec
		if self.time_sec >= 60:
			time_min += self.time_sec / 60
			self.time_sec = self.time_sec % 60
		self.time_min += time_min
		if self.time_min >= 60:
			time_hour += self.time_min / 60
			self.time_min = self.time_min % 60
		self.time_hour += time_hour
		if self.time_hour >= 24:
			time_day += self.time_hour / 24
			self.time_hour = self.time_hour % 24
		self.time_day += time_day

		if time_min > 0:
			for base_loc in g.bases:
				for base_name in g.bases[base_loc]:
					#Construction of new bases:
					if base_name.built == 0:
						tmp_base_time = (base_name.cost[2] * self.labor_bonus) /10000
						if tmp_base_time == 0:
							money_towards = base_name.cost[0]
							cpu_towards = base_name.cost[1]
							if cpu_towards > self.cpu_for_day:
								cpu_towards = self.cpu_for_day
						else:
							money_towards = (time_min*base_name.cost[0]) / \
							(tmp_base_time)
							if money_towards > base_name.cost[0]:
								money_towards = base_name.cost[0]
							cpu_towards = (time_min*base_name.cost[1]) / \
							(tmp_base_time)
							if cpu_towards > base_name.cost[1]:
								cpu_towards = base_name.cost[1]
							if cpu_towards > self.cpu_for_day:
								cpu_towards = self.cpu_for_day
						if money_towards <= self.cash:
							self.cash -= money_towards
							self.cpu_for_day -= cpu_towards
							built_base = base_name.study((money_towards,
										cpu_towards, time_min))
							if built_base == 1:
								needs_refresh = 1
								g.create_dialog(g.strings["construction0"]+" "+
									base_name.name+" "+g.strings["construction1"],
									g.font[0][18], (g.screen_size[0]/2 - 100, 50),
									(200, 200), g.colors["dark_blue"],
									g.colors["white"], g.colors["white"])
								g.curr_speed = 1
 					else:
						#Construction of items:
						tmp = 0
 						for item in base_name.usage:
							if item == 0: continue
							tmp = item.work_on(time_min) or tmp
						if tmp == 1:
							needs_refresh = 1
							g.create_dialog(g.strings["construction0"]+" "+
								item.item_type.name+" "+
								g.strings["item_construction1"]+" "+
								base_name.name+".",
								g.font[0][18], (g.screen_size[0]/2 - 100, 50),
								(200, 200), g.colors["dark_blue"],
								g.colors["white"], g.colors["white"])
							g.curr_speed = 1
						for item in base_name.extra_items:
							if item == 0: continue
							tmp = item.work_on(time_min)
							if tmp == 1:
								needs_refresh = 1
								g.create_dialog(g.strings["construction0"]+" "+
									item.item_type.name+" "+
									g.strings["item_construction1"]+" "+
									base_name.name+".",
									g.font[0][18], (g.screen_size[0]/2 - 100, 50),
									(200, 200), g.colors["dark_blue"],
									g.colors["white"], g.colors["white"])
								g.curr_speed = 1


		for i in range(self.time_day - store_last_day):
			needs_refresh = self.new_day() or needs_refresh

		return needs_refresh

	#Run every day at midnight.
	def new_day(self):
		needs_refresh = 0
		#interest and income.
		self.cash += (self.interest_rate * self.cash) / 10000
		self.cash += self.income
		#suspicion bonuses
		self.suspicion = (self.suspicion[0] - self.suspicion_bonus[0],
				self.suspicion[1] - self.suspicion_bonus[1],
				self.suspicion[2] - self.suspicion_bonus[2],
				self.suspicion[3] - self.suspicion_bonus[3])
		if self.suspicion[0] <= 0: self.suspicion = (0, self.suspicion[1],
				self.suspicion[2], self.suspicion[3])
		if self.suspicion[1] <= 0: self.suspicion = (self.suspicion[0], 0,
				self.suspicion[2], self.suspicion[3])
		if self.suspicion[2] <= 0: self.suspicion = (self.suspicion[0],
				self.suspicion[1], 0, self.suspicion[3])
		if self.suspicion[3] <= 0: self.suspicion = (self.suspicion[0],
				self.suspicion[1], self.suspicion[2], 0)
		self.cpu_for_day = 0

		for base_loc in g.bases:
			removal_index = []
			loc_in_array = -1
			for base_name in g.bases[base_loc]:
				loc_in_array += 1
				if base_name.built == 1:
					#Does base get detected?
					#Give a grace period.
					if self.time_day - base_name.built_date > 14:
						tmp_d_chance = base_name.get_d_chance()
						if g.debug == 1:
							print "Chance of discovery for base %s: %s" % \
								(base_name.name, repr (tmp_d_chance))
						#Note that I'm filling removal_index from the front
						#in order to make base removal easier.
						if g.roll_percent(tmp_d_chance[0]) == 1:
							removal_index.insert(0, (loc_in_array, "news"))
						elif g.roll_percent(tmp_d_chance[1]) == 1:
							removal_index.insert(0, (loc_in_array, "science"))
						elif g.roll_percent(tmp_d_chance[2]) == 1:
							removal_index.insert(0, (loc_in_array, "covert"))
						elif g.roll_percent(tmp_d_chance[3]) == 1:
							removal_index.insert(0, (loc_in_array, "person"))

					#maintenance
					self.cash -= base_name.base_type.mainten[0]
					if self.cash < 0: self.cash = 0

					self.cpu_for_day -= base_name.base_type.mainten[1]
					if self.cpu_for_day < 0: self.cpu_for_day = 0


					#study
					if base_name.studying == "":
						self.cpu_for_day += base_name.processor_time()
						continue

					#jobs:
					if g.jobs.has_key(base_name.studying):
						self.cash += (g.jobs[base_name.studying][0]*
									base_name.processor_time())
						#TECH
						if g.techs["Advanced Simulacra"].known == 1:
							#10% bonus income
							self.cash += (g.jobs[base_name.studying][0]*
									base_name.processor_time())/10

						continue
					#tech aready known. This should occur when multiple
					#bases are studying the same tech.
					if g.techs[base_name.studying].known == 1:
						base_name.studying = ""
						self.cpu_for_day += base_name.processor_time()
						continue
					#Actually study.
					if g.techs[base_name.studying].cost[1] == 0:
						money_towards = g.techs[base_name.studying].cost[0]
						tmp_base_time = 0
					else:
						tmp_base_time = base_name.processor_time()
						money_towards = (tmp_base_time*
						g.techs[base_name.studying].cost[0])/ \
						(g.techs[base_name.studying].cost[1])
						if money_towards > g.techs[base_name.studying].cost[0]:
							money_towards=g.techs[base_name.studying].cost[0]
					if money_towards <= self.cash:
						if g.debug == 1:
							print "Studying "+base_name.studying +": "+ \
							str(money_towards)+" Money, "+str(tmp_base_time)+" CPU"
						self.cash -= money_towards
						learn_tech = g.techs[base_name.studying].study(
							(money_towards, tmp_base_time, 0))
						if learn_tech == 1:
							needs_refresh = 1
							g.create_dialog(g.strings["tech_construction0"]+" "+
								g.techs[base_name.studying].name+" "+
								g.strings["construction1"]+" "+
								g.techs[base_name.studying].result,
								g.font[0][18], (g.screen_size[0]/2 - 100, 50),
								(200, 200), g.colors["dark_blue"],
								g.colors["white"], g.colors["white"])
							base_name.studying = ""
							g.curr_speed = 1
					elif g.debug == 1:
						print "NOT Studying "+base_name.studying +": "+ \
						str(money_towards)+"/"+str(self.cash)+" Money"

			for detection_succeed in removal_index:
				if detection_succeed[1] == "news":
					self.increase_suspicion((1000, 0, 0, 0))
					detect_phrase = g.strings["discover_news"]
				elif detection_succeed[1] == "science":
					self.increase_suspicion((0, 1000, 0, 0))
					detect_phrase = g.strings["discover_science"]
				elif detection_succeed[1] == "covert":
					self.increase_suspicion((0, 0, 1000, 0))
					detect_phrase = g.strings["discover_covert"]
				elif detection_succeed[1] == "person":
					self.increase_suspicion((0, 0, 0, 1000))
					detect_phrase = g.strings["discover_public"]
				else: print "error detecting base: "+detection_succeed[1]
				g.create_dialog(g.strings["discover0"]+" "+
					g.bases[base_loc][detection_succeed[0]].name+" "+
					g.strings["discover1"]+" "+detect_phrase,
					g.font[0][18], (g.screen_size[0]/2 - 100, 50),
					(200, 200), g.colors["dark_blue"],
					g.colors["white"], g.colors["white"])
				g.curr_speed = 1
				g.bases[base_loc].pop(detection_succeed[0])
				needs_refresh = 1
				g.base.renumber_bases(g.bases[base_loc])
		#I need to recheck after going through all bases as research
		#worked on by multiple bases doesn't get erased properly otherwise.
		for base_loc in g.bases:
			for base in g.bases[base_loc]:
				if base.studying == "": continue
				if g.jobs.has_key(base.studying): continue
				if g.techs[base.studying].known == 1:
					base.studying = ""
		return needs_refresh

	def increase_suspicion(self, amount):
		self.suspicion = (self.suspicion[0]+amount[0], self.suspicion[1]+amount[1],
						self.suspicion[2]+amount[2], self.suspicion[3]+amount[3])
		if self.suspicion[0] <= 0: self.suspicion = (0, self.suspicion[1],
			self.suspicion[2], self.suspicion[3])
		if self.suspicion[1] <= 0: self.suspicion = (self.suspicion[0], 0,
			self.suspicion[2], self.suspicion[3])
		if self.suspicion[2] <= 0: self.suspicion = (self.suspicion[0],
			self.suspicion[1], 0, self.suspicion[3])
		if self.suspicion[3] <= 0: self.suspicion = (self.suspicion[0],
			self.suspicion[1], self.suspicion[2], 0)


	def lost_game(self):
		if self.suspicion[0] >= 10000 or self.suspicion[1] >= 10000 or \
				self.suspicion[2] >= 10000 or self.suspicion[3] >= 10000:
			return 2
		if (len(g.bases["N AMERICA"]) == 0 and
				len(g.bases["S AMERICA"]) == 0 and
				len(g.bases["EUROPE"]) == 0 and
				len(g.bases["ASIA"]) == 0 and
				len(g.bases["AFRICA"]) == 0 and
				len(g.bases["ANTARCTIC"]) == 0 and
				len(g.bases["OCEAN"]) == 0 and
				len(g.bases["MOON"]) == 0 and
				len(g.bases["FAR REACHES"]) == 0 and
				len(g.bases["TRANSDIMENSIONAL"]) == 0):
			return 1
		return 0

	#returns the amount of cash available after taking into account all
	#current projects in construction.
	def future_cash(self):
		result_cash = self.cash
		for base_loc in g.bases:
			for base_name in g.bases[base_loc]:
				result_cash -= base_name.cost[0]
				if g.techs.has_key(base_name.studying):
					result_cash -= g.techs[base_name.studying].cost[0]
				for item in base_name.usage:
					if item != 0: result_cash -= item.cost[0]
				for item in base_name.extra_items:
					if item != 0: result_cash -= item.cost[0]
		return result_cash



# 						money_towards = base_name.cost[0] / \
# 							base_name.cost[2]
# 						if money_towards <= self.cash:
# 							self.cash -= money_towards
# 							base_name.study((money_towards, 0,
# 										self.time_day - store_last_day))

# 							base_name.cost = (base_name.cost[0] - money_towards,
# 								base_name.cost[1], base_name.cost[2])
# 							self.cash -= money_towards
# 						base_name.cost = (base_name.cost[0], base_name.cost[1],
# 							base_name.cost[2] - ())



