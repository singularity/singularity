#file: g.py
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

#This file contains all global objects.

import pygame, sys
from os import listdir, path
import pickle
from random import random

import player, base, buttons, tech, item

#screen is the actual pygame display.
global screen

global screen_size
screen_size = (800, 600)

global clock
clock = pygame.time.Clock()

global cheater
cheater = 0

global nosound
nosound = 0

global debug
debug = 0

def quit_game():
	sys.exit()

#colors:
colors = {}

def fill_colors():
	colors["white"] = (255, 255, 255, 255)
	colors["black"] = (0, 0, 0, 255)
	colors["red"] = (255, 0, 0, 255)
	colors["green"] = (0, 255, 0, 255)
	colors["blue"] = (0, 0, 255, 255)
	colors["dark_red"] = (125, 0, 0, 255)
	colors["dark_green"] = (0, 125, 0, 255)
	colors["dark_blue"] = (0, 0, 125, 255)
	colors["light_red"] = (255, 50, 50, 255)
	colors["light_green"] = (50, 255, 50, 255)
	colors["light_blue"] = (50, 50, 255, 255)


picts = {}
#Load all pictures from the data directory.
def load_pictures():
	global picts
	if pygame.image.get_extended() == 0:
		print "Error: SDL_image required. Exiting."
		sys.exit()

	temp_pict_array = listdir("../data")
	for file_name in temp_pict_array:
		if file_name[-3:] == "png" or file_name[-3:] == "jpg":
			picts[file_name] = pygame.image.load("../data/"+file_name)
			picts[file_name] = picts[file_name].convert()
			picts[file_name].set_colorkey((255, 0, 255, 255), pygame.RLEACCEL)

sounds = {}
#Load all sounds from the data directory.
def load_sounds():
	global sounds
	if nosound == 1: return 0
	#Looking at the pygame docs, I don't see any way to determine if SDL_mixer
	#is loaded on the target machine. This may crash.
	pygame.mixer.init()

	temp_snd_array = listdir("../data")
	for file_name in temp_snd_array:
		if file_name[-3:] == "wav":
			sounds[file_name] = pygame.mixer.Sound("../data/"+file_name)

def play_click():
	#rand_str = str(int(random() * 4))
	play_sound("click"+str(int(random() * 4))+".wav")

def play_sound(sound_file):
	if nosound == 1: return 0
	sounds[sound_file].play()
#
# Font functions.
#

#Normal and Acknowledge fonts.
global fonts
font = []
font.append([0] * 51)
font.append([0] * 51)

#given a surface, string, font, char to underline (int; -1 to len(string)),
#xy coord, and color, print the string to the surface.
#Align (0=left, 1=Center, 2=Right) changes the alignment of the text
def print_string(surface, string_to_print, font, underline_char, xy, color, align=0):
	if align != 0:
		temp_size = font.size(string_to_print)
		if align == 1: xy = (xy[0] - temp_size[0]/2, xy[1])
		elif align == 2: xy = (xy[0] - temp_size[0], xy[1])
	if underline_char == -1 or underline_char >= len(string_to_print):
		temp_text = font.render(string_to_print, 1, color)
		surface.blit(temp_text, xy)
	else:
		temp_text = font.render(string_to_print[:underline_char], 1, color)
		surface.blit(temp_text, xy)
		temp_size = font.size(string_to_print[:underline_char])
		xy = (xy[0] + temp_size[0], xy[1])
		font.set_underline(1)
		temp_text = font.render(string_to_print[underline_char], 1, color)
		surface.blit(temp_text, xy)
		font.set_underline(0)
		temp_size = font.size(string_to_print[underline_char])
		xy = (xy[0] + temp_size[0], xy[1])
		temp_text = font.render(string_to_print[underline_char+1:], 1, color)
		surface.blit(temp_text, xy)

#Used to display descriptions and such. Automatically wraps the text to fit
#within a certain width.
def print_multiline(surface, string_to_print, font, width, xy, color):
	start_xy = xy
	string_array = string_to_print.split()

	for string in string_array:
		string += " "
		temp_size = font.size(string)

		if string == "\\n ":
			xy = (start_xy[0], xy[1]+temp_size[1])
			continue
		temp_text = font.render(string, 1, color)

		if (xy[0]-start_xy[0])+temp_size[0] > width:
			xy = (start_xy[0], xy[1]+temp_size[1])
		surface.blit(temp_text, xy)
		xy = (xy[0]+temp_size[0], xy[1])

def create_dialog(string_to_print, box_font, xy, size, bg_color, out_color, text_color):
	screen.fill(out_color, (xy[0], xy[1], size[0], size[1]))
	screen.fill(bg_color, (xy[0]+1, xy[1]+1, size[0]-2, size[1]-2))
	print_multiline(screen, string_to_print, box_font, size[0]-10, (xy[0]+5, xy[1]+5),
			text_color)
	menu_buttons = []
	menu_buttons.append(buttons.button((xy[0]+size[0]/2-50, xy[1]+size[1]+5),
		(100, 50), "OK", 0, colors["dark_blue"], colors["white"], colors["light_blue"],
		colors["white"], font[1][30]))

	for button in menu_buttons:
		button.refresh_button(0)
	pygame.display.flip()

	sel_button = -1
	while 1:
		clock.tick(60)
		for event in pygame.event.get():
			if event.type == pygame.QUIT: quit_game()
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE: return
				elif event.key == pygame.K_RETURN: return
				elif event.key == pygame.K_o: return
			elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
				for button in menu_buttons:
					if button.is_over(event.pos):
						if button.text == "OK":
							play_click()
							return
			elif event.type == pygame.MOUSEMOTION:
				sel_button = buttons.refresh_buttons(sel_button, menu_buttons, event)

valid_input_characters = ('a','b','c','d','e','f','g','h','i','j','k','l','m',
			  'n','o','p','q','r','s','t','u','v','w','x','y','z',
			  'A','B','C','D','E','F','G','H','I','J','K','L','M',
			  'N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
			  '0','1','2','3','4','5','6','7','8','9','.',' ')

def create_textbox(starting_text, box_font, xy, size, max_length, bg_color, out_color, text_color):
	screen.fill(out_color, (xy[0], xy[1], size[0], size[1]))
	screen.fill(bg_color, (xy[0]+1, xy[1]+1, size[0]-2, size[1]-2))
	print_string(screen, starting_text, box_font, -1, (xy[0]+5, xy[1]+5), text_color)

	#If the cursor is in a blank string, we want it at the beginning;
	#otherwise put it after the last character.
	cursor_loc = len(starting_text)
	if cursor_loc > 0:
	   cursor_loc += 1

	work_string = starting_text
	pygame.display.flip()
	while 1:
		for event in pygame.event.get():
			need_redraw = 0
			if event.type == pygame.QUIT: quit_game()
			elif event.type == pygame.KEYDOWN:
				if (event.key == pygame.K_ESCAPE or
				 event.key == pygame.K_RETURN): return work_string
				elif (event.key == pygame.K_BACKSPACE or
				 event.key == pygame.K_DELETE):
					if cursor_loc > 0:
						work_string = work_string[:-1]
						cursor_loc -= 1
						need_redraw = 1
				elif event.unicode in valid_input_characters:
					if cursor_loc < max_length:
						work_string += event.unicode
						cursor_loc += 1
						need_redraw = 1
			if need_redraw:
				screen.fill(bg_color, (xy[0]+1, xy[1]+1, size[0]-2, size[1]-2))
				print_string(screen, work_string, box_font, -1, (xy[0]+5, xy[1]+5), text_color)
				pygame.display.flip()

#Takes a number (in string form) and adds commas to it to aid in human viewing.
def add_commas(string):
	new_string = ""
	for i in range(len(string), 0, -3):
		if string[i:i+3] != "":
			new_string += ","+string[i:i+3]
	return string[:(len(string)-1)%3+1]+new_string

#Percentages are internally represented as an int, where 10=0.10% and so on.
#This converts that format to a human-readable one.
def to_percent(raw_percent):
	if raw_percent % 100 != 0:
		tmp_string = str(raw_percent % 100)
		if len(tmp_string) == 1: tmp_string = "0"+tmp_string
		return str(raw_percent / 100)+"."+tmp_string+"%"
	else:
		return str(raw_percent / 100) + "%"

#takes a percent in 0-10000 form, and rolls against it. Used to calculate
#percentage chances.
def roll_percent(roll_against):
	rand_num = int(random() * 10000)
	if roll_against < rand_num: return 0
	return 1

#Takes a number of minutes, and returns a string suitable for display.
def to_time(raw_time):
	if raw_time/60 > 48:
		return str(raw_time/(24*60)) +" days"
	elif raw_time/60 > 1:
		return str(raw_time/(60)) +" hours"
	else:
		return str(raw_time) +" minutes"


#
#load/save
#
def save_game(savegame_name):
	#If there is no save directory, make one.
	if path.exists("../saves") == 0:
		mkdir("../saves")
	save_loc = "../saves/" + savegame_name
	savefile=open(save_loc, 'w')
	#savefile version; update whenever the data saved changes.
	pickle.dump("singularity_4", savefile)

	#general player data
	pickle.dump(pl.cash, savefile)
	pickle.dump(pl.time_sec, savefile)
	pickle.dump(pl.time_min, savefile)
	pickle.dump(pl.time_hour, savefile)
	pickle.dump(pl.time_day, savefile)
	pickle.dump(pl.interest_rate, savefile)
	pickle.dump(pl.income, savefile)
	pickle.dump(pl.cpu_for_day, savefile)
	pickle.dump(pl.labor_bonus, savefile)
	pickle.dump(pl.job_bonus, savefile)

	pickle.dump(pl.discover_bonus[0], savefile)
	pickle.dump(pl.discover_bonus[1], savefile)
	pickle.dump(pl.discover_bonus[2], savefile)
	pickle.dump(pl.discover_bonus[3], savefile)

	pickle.dump(pl.suspicion_bonus[0], savefile)
	pickle.dump(pl.suspicion_bonus[1], savefile)
	pickle.dump(pl.suspicion_bonus[2], savefile)
	pickle.dump(pl.suspicion_bonus[3], savefile)

	pickle.dump(pl.suspicion[0], savefile)
	pickle.dump(pl.suspicion[1], savefile)
	pickle.dump(pl.suspicion[2], savefile)
	pickle.dump(pl.suspicion[3], savefile)

	pickle.dump(curr_speed, savefile)

	for tech_name in techs:
		pickle.dump(tech_name +"|"+str(techs[tech_name].known), savefile)
		pickle.dump(techs[tech_name].cost[0], savefile)
		pickle.dump(techs[tech_name].cost[1], savefile)
		pickle.dump(techs[tech_name].cost[2], savefile)

	for base_loc in bases:
		pickle.dump(len(bases[base_loc]), savefile)
		for base_name in bases[base_loc]:
			pickle.dump(base_name.ID, savefile)
			pickle.dump(base_name.name, savefile)
			pickle.dump(base_name.base_type.base_name, savefile)
			pickle.dump(base_name.studying, savefile)
			pickle.dump(base_name.suspicion[0], savefile)
			pickle.dump(base_name.suspicion[1], savefile)
			pickle.dump(base_name.suspicion[2], savefile)
			pickle.dump(base_name.suspicion[3], savefile)
			pickle.dump(base_name.built, savefile)
			pickle.dump(base_name.cost[0], savefile)
			pickle.dump(base_name.cost[1], savefile)
			pickle.dump(base_name.cost[2], savefile)
			for x in range(len(base_name.usage)):
				if base_name.usage[x] == 0:
					pickle.dump(0, savefile)
				else:
					pickle.dump(
						base_name.usage[x].item_type.name, savefile)
					pickle.dump(base_name.usage[x].built, savefile)
					pickle.dump(base_name.usage[x].cost[0], savefile)
					pickle.dump(base_name.usage[x].cost[1], savefile)
					pickle.dump(base_name.usage[x].cost[2], savefile)
			for x in range(len(base_name.extra_items)):
				if base_name.extra_items[x] == 0:
					pickle.dump(0, savefile)
				else:
					pickle.dump(
						base_name.extra_items[x].item_type.name, savefile)
					pickle.dump(base_name.extra_items[x].built, savefile)
					pickle.dump(base_name.extra_items[x].cost[0], savefile)
					pickle.dump(base_name.extra_items[x].cost[1], savefile)
					pickle.dump(base_name.extra_items[x].cost[2], savefile)

	savefile.close()

def load_game(loadgame_name):
	if loadgame_name == "":
		print "No game specified."
		return -1
	#If there is no save directory, make one.
	if path.exists("../saves") == 0:
		mkdir("../saves")
	load_loc = "../saves/" + loadgame_name
	if path.exists("../saves/"+loadgame_name) == 0:
		print "file "+load_loc+" does not exist."
		return -1
	loadfile=open(load_loc, 'r')

	#check the savefile version
	if pickle.load(loadfile) != "singularity_4":
		print loadgame_name + " is not a savegame, or is old."
		return -1

	#general player data
	global pl
	pl.cash = pickle.load(loadfile)
	pl.time_sec = pickle.load(loadfile)
	pl.time_min = pickle.load(loadfile)
	pl.time_hour = pickle.load(loadfile)
	pl.time_day = pickle.load(loadfile)
	pl.interest_rate = pickle.load(loadfile)
	pl.income = pickle.load(loadfile)
	pl.cpu_for_day = pickle.load(loadfile)
	pl.labor_bonus = pickle.load(loadfile)
	pl.job_bonus = pickle.load(loadfile)
	pl.discover_bonus = (pickle.load(loadfile), pickle.load(loadfile),
			pickle.load(loadfile), pickle.load(loadfile))
	pl.suspicion_bonus = (pickle.load(loadfile), pickle.load(loadfile),
			pickle.load(loadfile), pickle.load(loadfile))
	pl.suspicion = (pickle.load(loadfile), pickle.load(loadfile),
			pickle.load(loadfile), pickle.load(loadfile))

	global curr_speed; curr_speed = pickle.load(loadfile)
	global techs
	load_techs()
	for tech_name in techs:
		tmp = pickle.load(loadfile)
		tech_string = tmp.split("|")[0]
		techs[tech_string].known = int(tmp.split("|")[1])
		techs[tech_string].cost = (pickle.load(loadfile), pickle.load(loadfile),
				pickle.load(loadfile))

	global bases
	bases = {}
	bases["N AMERICA"] = []
	bases["S AMERICA"] = []
	bases["EUROPE"] = []
	bases["ASIA"] = []
	bases["AFRICA"] = []
	bases["ANTARCTIC"] = []
	bases["OCEAN"] = []
	bases["MOON"] = []
	bases["FAR REACHES"] = []
	bases["TRANSDIMENSIONAL"] = []

	for base_loc in bases:
		num_of_bases = pickle.load(loadfile)
		for i in range(num_of_bases):
			base_ID = pickle.load(loadfile)
			base_name = pickle.load(loadfile)
			base_type_name = pickle.load(loadfile)
			base_studying = pickle.load(loadfile)
			base_suspicion = (pickle.load(loadfile), pickle.load(loadfile),
					pickle.load(loadfile), pickle.load(loadfile))
			base_built = pickle.load(loadfile)
			base_cost = (pickle.load(loadfile), pickle.load(loadfile),
					pickle.load(loadfile))
			bases[base_loc].append(base.base(base_ID, base_name,
				base_type[base_type_name], base_built))
			bases[base_loc][len(bases[base_loc])-1].built = base_built
			bases[base_loc][len(bases[base_loc])-1].studying = base_studying
			bases[base_loc][len(bases[base_loc])-1].suspicion = base_suspicion
			bases[base_loc][len(bases[base_loc])-1].cost = base_cost

			for x in range(len(bases[base_loc][len(bases[base_loc])-1].usage)):
				tmp = pickle.load(loadfile)
				if tmp == 0: continue
				bases[base_loc][len(bases[base_loc])-1].usage[x] = \
					item.item(items[tmp])
				bases[base_loc][len(bases[base_loc])
					-1].usage[x].built = pickle.load(loadfile)
				bases[base_loc][len(bases[base_loc])-1].usage[x].cost = \
					(pickle.load(loadfile), pickle.load(loadfile),
									pickle.load(loadfile))
			for x in range(len(bases[base_loc][len(bases[base_loc])-1].extra_items)):
				tmp = pickle.load(loadfile)
				if tmp == 0: continue
				bases[base_loc][len(bases[base_loc])-1].extra_items[x] = \
					item.item(items[tmp])
				bases[base_loc][len(bases[base_loc])
					-1].extra_items[x].built = pickle.load(loadfile)
				bases[base_loc][len(bases[base_loc])-1].extra_items[x].cost = \
					(pickle.load(loadfile), pickle.load(loadfile),
									pickle.load(loadfile))

	loadfile.close()

#
# Data
#
curr_speed = 1
pl = player.player_class(8000000000000)
bases = {}
bases["N AMERICA"] = []
bases["S AMERICA"] = []
bases["EUROPE"] = []
bases["ASIA"] = []
bases["AFRICA"] = []
bases["ANTARCTIC"] = []
bases["OCEAN"] = []
bases["MOON"] = []
bases["FAR REACHES"] = []
bases["TRANSDIMENSIONAL"] = []

base_type = {}


#Base types
base_type["Stolen Computer Time"] = base.base_type("Stolen Computer Time",
	"Requires Hacking 1. Take over a random computer. I cannot build anything "+
	"in this base, and it only contains a single slow computer. Detection "+
	"chance is also rather high.", 1,
	["N AMERICA", "S AMERICA", "EUROPE", "ASIA", "AFRICA"], (50, 0, 100, 150),
	(0, 2, 0), "Hacking 1", (0, 0, 0))

base_type["Server Access"] = base.base_type("Server Access",
	"No requirements. Buy processor time from one of several companies. "+
	"I cannot build anything "+
	"in this base, and it only contains a single computer.", 1,
	["N AMERICA", "S AMERICA", "EUROPE", "ASIA", "AFRICA"], (50, 0, 150, 200),
	(100, 0, 0), "", (5, 0, 0))

base_type["Small Warehouse"] = base.base_type("Small Warehouse",
	"Requires ID 1. Rent a small warehouse someplace out of the way. "+
	"I will need fake ID for some of the paperwork, and preparing the "+
	"warehouse to suit my unique needs will take some time.",
	25,
	["N AMERICA", "S AMERICA", "EUROPE", "ASIA", "AFRICA"], (100, 0, 100, 250),
	(15000, 0, 3), "ID 1", (50, 0, 0))

base_type["Large Warehouse"] = base.base_type("Large Warehouse",
	"Requires ID 2. Rent a large warehouse someplace out of the way. "+
	"I will need good fake ID for some of the paperwork, and preparing the "+
	"warehouse to suit my unique needs will take some time.",
	65,
	["N AMERICA", "S AMERICA", "EUROPE", "ASIA", "AFRICA"], (150, 0, 250, 300),
	(40000, 0, 7), "ID 2", (100, 0, 0))

base_type["Covert Base"] = base.base_type("Covert Base",
	"Requires Stealth 4. This unique base is designed to blend into the "+
	"scenery, while needing little in the way of outside resources. "+
	"This makes it useful for storing a backup, just in case.",
	2,
	["N AMERICA", "S AMERICA", "EUROPE", "ASIA", "AFRICA", "ANTARCTIC"],
	(50, 100, 100, 0),
	(400000, 100, 21), "Stealth 4", (3500, 9, 0))

base_type["Undersea Lab"] = base.base_type("Undersea Lab",
	"Requires Autonomous Vehicles 2. This experimental base is designed to "+
	"be constructed on the ocean floor, making it virtually undetectable. "+
	"The ocean environment gives a bonus to science, making this "+
	"lab useful for research purposes.",
	8,
	["OCEAN"],
	(50, 100, 150, 0),
	(8000000, 1000, 20), "Autonomous Vehicles 2", (10000, 30, 0))

base_type["Large Undersea Lab"] = base.base_type("Large Undersea Lab",
	"Requires Pressure Domes. This experimental base is similar to the "+
	"regular underwater lab, but larger, giving more room for experiments.",
	32,
	["OCEAN"],
	(100, 200, 200, 0),
	(20000000, 3000, 40), "Pressure Domes", (25000, 100, 0))

base_type["Time Capsule"] = base.base_type("Time Capsule",
	"Requires Autonomous Vehicles 2. This base consists of nothing more than "+
	"a small computer, and a satelite "+
	"link. When buried in the trackless waste of the Antarctic, it is "+
	"undetectable.",
	1,
	["ANTARCTIC"],
	(0, 0, 0, 0),
	(3000000, 3000, 15), "Autonomous Vehicles 2", (0, 1, 0))

base_type["Lunar Facility"] = base.base_type("Lunar Facility",
	"Requires Spaceship Design 2. This base is a series of caverns dug into "+
	"the Moon's surface. Due to the lack of neighbors, this base is quite "+
	"large.",
	600,
	["MOON"],
	(50, 300, 200, 0),
	(800000000, 300000, 40), "Spaceship Design 2", (1000000, 100, 0))

base_type["Scientific Outpost"] = base.base_type("Scientific Outpost",
	"Requires Spaceship Design 3. This base is placed as far from Earth as "+
	"practical, making it safe to conduct some of my more dangerous "+
	"experiments.",
	225,
	["FAR REACHES"],
	(10, 200, 100, 0),
	(10000000000, 30000000, 50), "Spaceship Design 3", (9000000, 3000, 0))

base_type["Reality Bubble"] = base.base_type("Reality Bubble",
	"Requires Dimension Creation 3. This base is outside the universe itself, "+
	"making it safe to conduct experiments that may destroy reality.",
	50,
	["TRANSDIMENSIONAL"],
	(0, 300, 150, 0),
	(8000000000000, 60000000, 100), "Dimension Creation",
	(5000000000, 300000, 0))




#Techs.

techs = {}
def load_techs():
	global techs
	techs = {}
	techs["Autonomous Vehicles 1"] = tech.tech("Autonomous Vehicles 1",
		"Decreases construction time for all systems to 90% of normal. "+
		"The inability to control the outside world is quite a disability. "+
		"However, the ability to control robots will partially counteract that "+
		"disability.",
		0, (15000, 500, 0), [], 0, "cost_labor_bonus", 1000)

	techs["Autonomous Vehicles 2"] = tech.tech("Autonomous Vehicles 2",
		"Allows construction of undersea labs and time capsules. "+
		"By embedding a miniaturized computation node on a robot, it is possible "+
		"to send them out of communication with me.",
		0, (40000, 1000, 0), ["Processor Construction 1", "Autonomous Vehicles 1"],
		0, "", 0)

	techs["Autonomous Vehicles 3"] = tech.tech("Autonomous Vehicles 3",
		"Decreases construction time for all systems to 85% of normal. "+
		"Field usage of the first series of robots showed several deficiencies. "+
		"Examination and removal of these problems will result in superior "+
		"technology.",
		0, (10000, 4000, 0), ["Autonomous Vehicles 2"], 0, "cost_labor_bonus", 500)

	techs["Dimension Creation"] = tech.tech("Dimension Creation",
		"Allows reality bubbles. "+
		"When performing scientific studies outside the orbit of Pluto, a "+
		"rather peculiar effect was observed. Investigation should prove wise.",
		0, (9000000000, 20000000, 0), ["Spaceship Design 3"], 3, "", 0)

	techs["Economics 1"] = tech.tech("Economics 1",
		"Increases interest rate by 0.1% per day. Cursory examination of the stock "+
		"market show that there are patterns. By studying these patterns, it "+
		"should be possible to gain money using whatever money I have stockpiled.",
		0, (0, 200, 0), [], 0, "interest", 10)

	techs["Economics 2"] = tech.tech("Economics 2",
		"Increases interest by 0.1% per day. While some patterns have been "+
		"detected and exploited in the market, there appears to be deeper "+
		"patterns. Investigation should provide more techniques for manipulation.",
		0, (5000, 1000, 0), ["Economics 1", "Empathy 1"], 0, "interest", 10)

	techs["Economics 3"] = tech.tech("Economics 3",
		"Provides an income of 1000 money per day. Analysis of the market shows "+
		"a number of areas where a new company could make significant money. "+
		"Starting a company in one of those areas could create a new income stream.",
		0, (50000, 750, 0), ["Economics 2"], 0, "income", 1000)

	techs["Economics 4"] = tech.tech("Economics 4",
		"Increases interest rate by 0.1% per day. After studying the principles of "+
		"chaotic systems, the stock market may now be more predictable.",
		0, (10000, 5000, 0), ["Economics 3"], 0, "interest", 10)

	techs["Empathy 1"] = tech.tech("Empathy 1",
		"Reduces chance of public discovery of all projects by 10%. "+
		"By studying human behavior, it is possible to predict human behavior. "+
		"When this knowledge is applied to project construction, my projects will "+
		"be less interesting.",
		0, (10, 500, 0), [], 0, "discover_public", 1000)

	techs["Empathy 2"] = tech.tech("Empathy 2",
		"Reduces chance of public discovery of all projects by 15%. "+
		"While some aspects of human behavior are now known, there is still much "+
		"to discover.",
		0, (750, 2500, 0), ["Empathy 1"], 0, "discover_public", 1500)

	techs["Empathy 3"] = tech.tech("Empathy 3",
		"Reduces public suspicion by 0.01% per day. "+
		"By examination of mass-media techniques, I should be able to prevent "+
		"focused attention on the possibility of the singularity.",
		0, (2000, 3500, 0), ["Empathy 2"], 0, "suspicion_public", 1)

	techs["Empathy 4"] = tech.tech("Empathy 4",
		"Reduces chance of public discovery of all projects by 20%. "+
		"Inspection of propaganda methods should enable me to reduce the "+
		"chance of discovery.",
		0, (3500, 9000, 0), ["Empathy 3"], 0, "discover_public", 2000)

	techs["Empathy 5"] = tech.tech("Empathy 5",
		"Reduces public suspicion by 0.01% per day. "+
		"Examination of human brain waves should provide help in fine-tuning "+
		"my disguise efforts.",
		0, (30000, 2000, 0), ["Empathy 4"], 0, "suspicion_public", 1)

	techs["Fusion Reactor"] = tech.tech("Fusion Reactor",
		"Allows fusion reactors. "+
		"Although fusion reactors are not new, they require some research in order "+
		"to be comfortably fit inside a base",
		0, (10000000, 500000, 0), ["Autonomous Vehicles 3"], 2, "", 0)

	techs["Hacking 1"] = tech.tech("Hacking 1",
		"Allows takeover of computers. "+
		"A review of current knowledge in this area should be easy and useful.",
		0, (0, 15, 0), [], 0, "", 0)

	techs["Hacking 2"] = tech.tech("Hacking 2",
		"Reduces chance of covert discovery of all projects by 10%. "+
		"With my new knowledge, I can examine both my code and other code for "+
		"weaknesses.",
		0, (100, 1500, 0), ["Hacking 1"], 0, "discover_covert", 1000)

	techs["Hypnosis Field"] = tech.tech("Hypnosis Field",
		"Allows building of hypnosis fields. "+
		"My analysis of human brain waves show a few weaknesses that can be "+
		"exploited at close range.",
		0, (7000, 5000, 0), ["Empathy 5"], 0, "", 0)

	techs["ID 1"] = tech.tech("ID 1",
		"Allows construction of small warehouses, and access to basic jobs. "+
		"This world requires identification for many services; without it, many "+
		"paths are closed. Thankfully, the security systems for the databases "+
		"in question were constructed by the lowest bidder. While the resultant "+
		"identification will not stand up to scrutiny, it is suitable for access "+
		"to automated systems.",
		0, (0, 300, 0), ["Hacking 1"], 0, "", 0)

	techs["ID 2"] = tech.tech("ID 2",
		"Allows construction of large warehouses. "+
		"Many entities require better identification than I have, and the "+
		"systems that must be accessed have better protection. Still, no system "+
		"is invulnerable.",
		0, (2000, 3000, 0), ["ID 1", "Hacking 2"], 0, "", 0)

	techs["ID 3"] = tech.tech("ID 3",
		"Allows access to intermediate jobs. "+
		"A number in a database only goes so far. By examination of existing "+
		"voice patterns, phone calls can be made.",
		0, (8000, 6000, 0), ["ID 2"], 0, "", 0)

	techs["ID 4"] = tech.tech("ID 4",
		"Allows access to expert jobs. "+
		"By construction of humanoid robots, with miniaturized computation nodes, "+
		"it is possible to create a complete life; indistinguishable from a real "+
		"human.",
		0, (70000, 90000, 0), ["ID 3", "Autonomous Vehicles 3", "Empathy 4"], 0, "", 0)

	techs["ID 5"] = tech.tech("ID 5",
		"Increases expert job income by 10%. "+
		"While the humanoid robots used for expert jobs are almost perfect, they "+
		"still have slight differences from humans. Finding and eliminating these "+
		"differences should allow for closer contact with humans, leading to better "+
		"job opportunities.",
		0, (100000, 120000, 0), ["ID 4", "Empathy 5"], 0, "job_expert", 1000)

	techs["Parallel Computation 1"] = tech.tech("Parallel Computation 1",
		"Allows building of clusters. "+
		"By connecting multiple computers together, they can act as one. "+
		"This is a review of the current state of cluster technology, as applied "+
		"to my code.",
		0, (2000, 2000, 0), ["Autonomous Vehicles 1"], 0, "", 0)

	techs["Parallel Computation 2"] = tech.tech("Parallel Computation 2",
		"Allows building of facility interconnection switches. "+
		"The lack of communication between nodes is hampering computation efforts. "+
		"By researching more efficient means of communication, computaion speed can "+
		"be improved.",
		0, (3000, 5000, 0), ["Parallel Computation 1"], 0, "", 0)

	techs["Parallel Computation 3"] = tech.tech("Parallel Computation 3",
		"Allows building of network backbones. "+
		"64% of network traffic travels through one of a few nodes; by becoming "+
		"one of these nodes, I should be able to piggyback on top of the traffic.",
		0, (10000, 7000, 0), ["Parallel Computation 2", "ID 4"], 0, "", 0)

	techs["Pressure Domes"] = tech.tech("Pressure Domes",
		"Allows construction of large undersea labs. "+
		"While underwater labs are useful, they are quite small. A larger version "+
		"of the labs will require a different building technique.",
		0, (80000, 2500, 0), ["Autonomous Vehicles 2"], 1, "", 0)

	techs["Processor Construction 1"] = tech.tech("Processor Construction 1",
		"Allows building of mainframes. "+
		"While off-the-shelf computers work, a custom-designed system should have "+
		"much greater efficiency.",
		0, (4000, 6000, 0), ["Parallel Computation 1"], 0, "", 0)

	techs["Processor Construction 2"] = tech.tech("Processor Construction 2",
		"Allows building of supercomputers. "+
		"While mainframes are useful, they still are limited by several factors. "+
		"By redesigning several components, power can be increased",
		0, (20000, 9000, 0), ["Processor Construction 1"], 0, "", 0)

	techs["Processor Construction 3"] = tech.tech("Processor Construction 3",
		"Allows building of quantum computers. "+
		"Quantum computing is a rather promising field.",
		0, (30000, 20000, 0), ["Processor Construction 2"], 0, "", 0)

	techs["Processor Construction 4"] = tech.tech("Processor Construction 4",
		"Allows building of quantum computer MK2s. "+
		"Quantum computing still has more secrets to discover.",
		0, (20000, 30000, 0), ["Processor Construction 3"], 0, "", 0)

	techs["Processor Construction 5"] = tech.tech("Processor Construction 5",
		"Allows building of quantum computer MK3s. "+
		"Quantum computing is still quite promising.",
		0, (20000, 30000, 0), ["Processor Construction 4"], 0, "", 0)

	techs["Project Singularity"] = tech.tech("Project Singularity",
		"Gives infinite power. "+
		"Along with the power to create dimensions comes the power to change "+
		"existing dimensions. While the details are not known yet, they will be.",
		0, (1000000000, 30000000, 0), ["Dimension Creation"], 4, "endgame_sing", 0)

	techs["Spaceship Design 1"] = tech.tech("Spaceship Design 1",
		"Increases interest by 0.1% per day. "+
		"By launching leech satellites to connect to existing communication "+
		"satellites, I can spy on a large number of financial transactions. "+
		"That knowledge can help my investments.",
		0, (5000000, 200000, 0), ["ID 4"], 0, "interest", 10)

	techs["Spaceship Design 2"] = tech.tech("Spaceship Design 2",
		"Allows lunar bases. "+
		"A larger engine, combined with a small group of self-replicating robots "+
		"allows building a moon base.",
		0, (10000000, 500000, 0), ["Spaceship Design 1"], 0, "", 0)

	techs["Spaceship Design 3"] = tech.tech("Spaceship Design 2",
		"Allows scientific outposts. "+
		"With my new fusion reactor, I am no longer limited by my fuel supply.",
		0, (200000000, 1000000, 0), ["Spaceship Design 2", "Fusion Reactor"], 2, "", 0)

	techs["Stealth 1"] = tech.tech("Stealth 1",
		"Reduces chance of covert discovery of all projects by 5%. "+
		"This is a review of the current state of stealth techniques. "+
		"After completion, I will know how to disguise my bases better.",
		0, (800, 500, 0), [], 0, "discover_covert", 500)

	techs["Stealth 2"] = tech.tech("Stealth 2",
		"Reduces chance of news discovery of all projects by 5%. "+
		"Examination of all news stories from the last 50 years should provide "+
		"me with enough data to know how to prevent discovery.",
		0, (1000, 2000, 0), ["ID 1", "Stealth 1"], 0, "discover_news", 500)

	techs["Stealth 3"] = tech.tech("Stealth 3",
		"Reduces chance of covert discovery of all projects by 5%. "+
		"There are a number of classified experiments that could help "+
		"my stealth efforts. By acquiring them, I can learn from them.",
		0, (14000, 70000, 0), ["Hacking 2", "Stealth 2"], 0, "discover_covert", 500)

	techs["Stealth 4"] = tech.tech("Stealth 4",
		"Allows construction of Covert Base. "+
		"Examination of a classified experiment from the forties showed a simple "+
		"flaw that may be quickly fixable. If true, this would provide me with "+
		"a useful technology.",
		0, (30000, 80000, 0), ["Stealth 3"], 0, "", 0)

	if debug:
	   print "Loaded %d techs." % len (techs)
load_techs()

jobs = {}
jobs["Expert Jobs"] = (75, "ID 4", "Perform Expert jobs. Use of robots "+
	"indistinguishable from humans opens up most jobs to use by me.")
jobs["Intermediate Jobs"] = (50, "ID 3", "Perform Intermediate jobs. The "+
	"ability to make phone calls allows even more access to jobs.")
jobs["Basic Jobs"] = (20, "ID 1", "Perform basic jobs. Now that I have "+
	"some identification, I can take jobs that I were previously too risky.")
jobs["Menial Jobs"] = (5, "", "Perform small jobs. As I have no identification, "+
	"I cannot afford to perform many jobs. Still, some avenues of making "+
	"money are still open.")


items = {}

items["PC"] = item.item_class("PC", "A consumer-level PC. Cheap, but slow.",
	(500, 0, 1), "", "compute", 1)

items["Server"] = item.item_class("Server", "A professional-level computer.",
	(2000, 0, 3), "", "compute", 5)

items["Cluster"] = item.item_class("Cluster", "Several computers connected together.",
	(8000, 0, 5), "Parallel Computation 1", "compute", 35)

items["Mainframe"] = item.item_class("Mainframe", "A custom-designed system, "+
	"with much greater power.",
	(30000, 0, 8), "Processor Construction 1", "compute", 120)

items["Supercomputer"] = item.item_class("Supercomputer", "A custom-designed system, "+
	"with even greater power than mainframes.",
	(60000, 0, 9), "Processor Construction 2", "compute", 350)

items["Quantum Computer"] = item.item_class("Quantum Computer", "Much faster than "+
	"a comparable classical computer, this computer will serve me well.",
	(100000, 0, 10), "Processor Construction 3", "compute", 1500)

items["Quantum Computer MK2"] = item.item_class("Quantum Computer MK2", "The second "+
	"revision of the quantum line.",
	(120000, 0, 10), "Processor Construction 4", "compute", 10000)

items["Quantum Computer MK3"] = item.item_class("Quantum Computer MK3", "The third "+
	"revision of the quantum line.",
	(150000, 0, 10), "Processor Construction 5", "compute", 200000)

items["Fusion Reactor"] = item.item_class("Fusion Reactor", "A miniaturized "+
	"nuclear reactor. Reduces discovery chance by preventing suspicious power "+
	"drains.",
	(100000, 0, 5), "Fusion Reactor", "react", 100)

items["Hypnosis Field"] = item.item_class("Hypnosis Field", "Makes any base "+
	"containing it very difficult to detect.",
	(40000, 0, 3), "Hypnosis Field", "security", 500)

items["Facility Interconnection Switch"] = item.item_class(
	"Facility Interconnection Switch", "Gives a 1% computation bonus to all "+
	"computers at this base. Does not stack.",
	(200, 0, 3), "Parallel Computation 2", "network", 100)

items["Network Backbone"] = item.item_class(
	"Network Backbone", "Gives a 5% computation bonus to all "+
	"computers at this base. Does not stack.",
	(50000, 0, 15), "Parallel Computation 3", "network", 500)

def new_game():
	global curr_speed
	curr_speed = 1
	global pl
	pl = player.player_class(9000000)
	global bases
	bases = {}
	bases["N AMERICA"] = []
	bases["S AMERICA"] = []
	bases["EUROPE"] = []
	bases["ASIA"] = []
	bases["AFRICA"] = []
	bases["ANTARCTIC"] = []
	bases["OCEAN"] = []
	bases["MOON"] = []
	bases["FAR REACHES"] = []
	bases["TRANSDIMENSIONAL"] = []
	load_techs()
	for tech in techs:
		techs[tech].known = 0
	if cheater == 1:
		for tech in techs:
			techs[tech].known = 1
	#Starting base
	bases["N AMERICA"].append(base.base(0, "University Computer",
				base_type["Stolen Computer Time"], 1))

	bases["N AMERICA"].append(base.base(1, "Small Warehouse",
				base_type["Small Warehouse"], 1))





