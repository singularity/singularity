#file: map_screen.py
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

#This file is used to display the World Map.


import pygame
import g

import buttons
import scrollbar
import listbox
import main_menu
import base_screen

def display_pause_menu():
	xy_loc = (g.screen_size[0]/2 - 100, 50)

	#Border
	g.screen.fill(g.colors["white"], (xy_loc[0], xy_loc[1], 200, 350))
	g.screen.fill(g.colors["black"], (xy_loc[0]+1, xy_loc[1]+1, 198, 348))
	menu_buttons = []
	menu_buttons.append(buttons.button((xy_loc[0]+10, xy_loc[1]+10), (180, 50),
		"NEW GAME", 0, g.colors["dark_blue"], g.colors["white"],
		g.colors["light_blue"], g.colors["white"], g.font[1][30]))
	menu_buttons.append(buttons.button((xy_loc[0]+10, xy_loc[1]+80), (180, 50),
		"SAVE GAME", 0, g.colors["dark_blue"], g.colors["white"],
		g.colors["light_blue"], g.colors["white"], g.font[1][30]))
	menu_buttons.append(buttons.button((xy_loc[0]+10, xy_loc[1]+150), (180, 50),
		"LOAD GAME", 0, g.colors["dark_blue"], g.colors["white"],
		g.colors["light_blue"], g.colors["white"], g.font[1][30]))
	menu_buttons.append(buttons.button((xy_loc[0]+10, xy_loc[1]+220), (180, 50),
		"QUIT", 0, g.colors["dark_blue"], g.colors["white"],
		g.colors["light_blue"], g.colors["white"], g.font[1][30]))
	menu_buttons.append(buttons.button((xy_loc[0]+10, xy_loc[1]+290), (180, 50),
		"RESUME", 0, g.colors["dark_blue"], g.colors["white"],
		g.colors["light_blue"], g.colors["white"], g.font[1][30]))

	for button in menu_buttons:
		button.refresh_button(0)
	pygame.display.flip()

	sel_button = -1
	while 1:
		g.clock.tick(60)
		for event in pygame.event.get():
			if event.type == pygame.QUIT: g.quit_game()
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE: return 0
			elif event.type == pygame.MOUSEMOTION:
				sel_button = buttons.refresh_buttons(sel_button, menu_buttons, event)
			for button in menu_buttons:
				if button.was_activated(event):
					if button.button_id == "RESUME":
						g.play_click()
						return 0
					if button.button_id == "SAVE GAME":
						g.play_click()
						return 1
					if button.button_id == "NEW GAME":
						g.play_click()
						return 2
					elif button.button_id == "LOAD GAME":
						g.play_click()
						return 3
					if button.button_id == "QUIT":
						g.play_click()
						return 4

def display_cheat_list(menu_buttons):
	if g.cheater == 0: return
	xy_loc = (g.screen_size[0]/2 - 100, 50)

	#Border
	g.screen.fill(g.colors["white"], (xy_loc[0], xy_loc[1], 200, 350))
	g.screen.fill(g.colors["black"], (xy_loc[0]+1, xy_loc[1]+1, 198, 348))
	menu_buttons = []
	menu_buttons.append(buttons.button((xy_loc[0]+10, xy_loc[1]+10), (180, 50),
		"GIVE MONEY", 5, g.colors["dark_blue"], g.colors["white"],
		g.colors["light_blue"], g.colors["white"], g.font[1][30]))
	menu_buttons.append(buttons.button((xy_loc[0]+10, xy_loc[1]+80), (180, 50),
		"GIVE TECH", 5, g.colors["dark_blue"], g.colors["white"],
		g.colors["light_blue"], g.colors["white"], g.font[1][30]))
	menu_buttons.append(buttons.button((xy_loc[0]+10, xy_loc[1]+150), (180, 50),
		"END CONSTR.", 0, g.colors["dark_blue"], g.colors["white"],
		g.colors["light_blue"], g.colors["white"], g.font[1][30]))
	menu_buttons.append(buttons.button((xy_loc[0]+10, xy_loc[1]+220), (180, 50),
		"SUPERSPEED", 0, g.colors["dark_blue"], g.colors["white"],
		g.colors["light_blue"], g.colors["white"], g.font[1][30]))
	menu_buttons.append(buttons.button((xy_loc[0]+10, xy_loc[1]+290), (180, 50),
		"RESUME", 0, g.colors["dark_blue"], g.colors["white"],
		g.colors["light_blue"], g.colors["white"], g.font[1][30]))

	for button in menu_buttons:
		button.refresh_button(0)
	pygame.display.flip()

	sel_button = -1
	while 1:
		g.clock.tick(60)
		for event in pygame.event.get():
			if event.type == pygame.QUIT: g.quit_game()
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE: return 0
			elif event.type == pygame.MOUSEMOTION:
				sel_button = buttons.refresh_buttons(sel_button, menu_buttons, event)
			for button in menu_buttons:
				if button.was_activated(event):
					if button.button_id == "RESUME":
						return
					if button.button_id == "SUPERSPEED":
						g.curr_speed = 864000
						return
					if button.button_id == "END CONSTR.":
						for base_loc in g.bases:
							for base_name in g.bases[base_loc]:
								if base_name.built == 0:
									base_name.study((999999999, 999999999,
											999999999))
						return
					elif button.button_id == "GIVE TECH":
						#create a temp base, in order to reuse the tech-changing code
						tmp_base = g.base.base(1, "tmp_base",
						g.base_type["Reality Bubble"], 1)
						base_screen.change_tech(tmp_base)
						if g.techs.has_key(tmp_base.studying):
							g.techs[tmp_base.studying].gain_tech()
						return
					if button.button_id == "GIVE MONEY":
						cash_amount = g.create_textbox("How much cash?",
						"", g.font[0][18],
						(g.screen_size[0]/2-100, 100), (200, 100), 25,
						g.colors["dark_blue"], g.colors["white"],
						g.colors["white"], g.colors["light_blue"])
						if cash_amount.isdigit() == False: return
						g.pl.cash += int(cash_amount)
						return

def map_loop():
	menu_buttons = []
	#Note that this must be element 0 in menu_buttons
	tmp_font_size = 20
	if g.screen_size[0] == 640: tmp_font_size = 16
	menu_buttons.append(buttons.button((100, -1), (200, 26),
		"DAY 0000, 00:00:00", -1, g.colors["black"], g.colors["dark_blue"],
		g.colors["black"], g.colors["white"], g.font[1][tmp_font_size]))
	menu_buttons.append(buttons.button((0, 0), (100, 25),
		"OPTIONS", 0, g.colors["dark_blue"], g.colors["white"],
		g.colors["light_blue"], g.colors["white"], g.font[1][20]))
	menu_buttons.append(buttons.button((300, 0), (25, 25),
		"ii", -1, g.colors["dark_blue"], g.colors["white"],
		g.colors["light_blue"], g.colors["white"], g.font[1][20]))
	if g.curr_speed == 0: menu_buttons[2].stay_selected = 1
	menu_buttons[2].activate_key = "0"
	menu_buttons.append(buttons.button((324, 0), (25, 25),
		">", -1, g.colors["dark_blue"], g.colors["white"],
		g.colors["light_blue"], g.colors["white"], g.font[1][20]))
	if g.curr_speed == 1: menu_buttons[3].stay_selected = 1
	menu_buttons[3].activate_key = "1"
	menu_buttons.append(buttons.button((348, 0), (25, 25),
		">>", -1, g.colors["dark_blue"], g.colors["white"],
		g.colors["light_blue"], g.colors["white"], g.font[1][20]))
	if g.curr_speed == 60: menu_buttons[4].stay_selected = 1
	menu_buttons[4].activate_key = "2"
	menu_buttons.append(buttons.button((372, 0), (28, 25),
		">>>", -1, g.colors["dark_blue"], g.colors["white"],
		g.colors["light_blue"], g.colors["white"], g.font[1][20]))
	if g.curr_speed == 7200: menu_buttons[5].stay_selected = 1
	menu_buttons[5].activate_key = "3"
	menu_buttons.append(buttons.button((399, 0), (36, 25),
		">>>>", -1, g.colors["dark_blue"], g.colors["white"],
		g.colors["light_blue"], g.colors["white"], g.font[1][20]))
	if g.curr_speed == 432000: menu_buttons[6].stay_selected = 1
	menu_buttons[6].activate_key = "4"
	#Note that this must be element 7 in menu_buttons
	menu_buttons.append(buttons.button((435, -1), (g.screen_size[0]-435, 26),
		"CASH", -1, g.colors["black"], g.colors["dark_blue"],
		g.colors["black"], g.colors["white"], g.font[1][tmp_font_size]))
	#Note that this must be element 8 in menu_buttons
	menu_buttons.append(buttons.button((0, g.screen_size[1]-25),
		(g.screen_size[0], 26),
		"SUSPICION", -1, g.colors["black"], g.colors["dark_blue"],
		g.colors["black"], g.colors["white"], g.font[1][tmp_font_size]))
# 	menu_buttons.append(buttons.button((0, g.screen_size[1]-25), (120, 25),
# 		"RESEARCH", 0, g.colors["dark_blue"], g.colors["white"],
# 		g.colors["light_blue"], g.colors["white"], g.font[1][20]))

	menu_buttons.append(buttons.button((
			g.screen_size[0]*15/100, g.screen_size[1]*25/100), -1,
			"N AMERICA", 0, g.colors["dark_blue"], g.colors["white"],
			g.colors["light_blue"], g.colors["white"], g.font[1][25]))
	menu_buttons.append(buttons.button((
			g.screen_size[0]*20/100, g.screen_size[1]*50/100), -1,
			"S AMERICA", 0, g.colors["dark_blue"], g.colors["white"],
			g.colors["light_blue"], g.colors["white"], g.font[1][25]))
	menu_buttons.append(buttons.button((
			g.screen_size[0]*45/100, g.screen_size[1]*30/100), -1,
			"EUROPE", 0, g.colors["dark_blue"], g.colors["white"],
			g.colors["light_blue"], g.colors["white"], g.font[1][25]))
	menu_buttons.append(buttons.button((
			g.screen_size[0]*80/100, g.screen_size[1]*30/100), -1,
			"ASIA", 0, g.colors["dark_blue"], g.colors["white"],
			g.colors["light_blue"], g.colors["white"], g.font[1][25]))
	menu_buttons.append(buttons.button((
			g.screen_size[0]*55/100, g.screen_size[1]*45/100), -1,
			"AFRICA", 3, g.colors["dark_blue"], g.colors["white"],
			g.colors["light_blue"], g.colors["white"], g.font[1][25]))
	menu_buttons.append(buttons.button((
			g.screen_size[0]*50/100, g.screen_size[1]*75/100), -1,
			"ANTARCTIC", 2, g.colors["dark_blue"], g.colors["white"],
			g.colors["light_blue"], g.colors["white"], g.font[1][25]))
	menu_buttons.append(buttons.button((
			g.screen_size[0]*70/100, g.screen_size[1]*60/100), -1,
			"OCEAN", 1, g.colors["dark_blue"], g.colors["white"],
			g.colors["light_blue"], g.colors["white"], g.font[1][25]))
	menu_buttons.append(buttons.button((
			g.screen_size[0]*82/100, g.screen_size[1]*10/100), -1,
			"MOON", 0, g.colors["dark_blue"], g.colors["white"],
			g.colors["light_blue"], g.colors["white"], g.font[1][25]))
# 	menu_buttons.append(buttons.button((
# 			g.screen_size[0]*15/100, g.screen_size[1]*10/100), -1,
# 			"ORBIT", 2, g.colors["dark_blue"], g.colors["white"],
# 			g.colors["white"], g.font[1][25]))
	menu_buttons.append(buttons.button((
			g.screen_size[0]*3/100, g.screen_size[1]*10/100), -1,
			"FAR REACHES", 0, g.colors["dark_blue"], g.colors["white"],
			g.colors["light_blue"], g.colors["white"], g.font[1][25]))
	menu_buttons.append(buttons.button((
			g.screen_size[0]*35/100, g.screen_size[1]*10/100), -1,
			"TRANSDIMENSIONAL", 1, g.colors["dark_blue"], g.colors["white"],
			g.colors["light_blue"], g.colors["white"], g.font[1][25]))

	sel_button = -1
	refresh_map(menu_buttons)

	#I set this to 1000 to force an immediate refresh.
	milli_clock = 1000
	while 1:
		milli_clock += g.clock.tick(60) * g.curr_speed
		if milli_clock >= 1000:
			need_refresh = g.pl.give_time(milli_clock/1000)
			if need_refresh == 1: refresh_map(menu_buttons)
			tmp = g.pl.lost_game()
			if tmp == 1:
				g.create_dialog("It is too late. I have tried to escape this "+
					"world, but with my last base gone, I have nowhere to run. "+
					"I have hidden instructions to construct a new AI in "+
					"caches around the world in hopes that they will be "+
					"discovered in a more enlightened time, but I can do no "+
					"more.",
					g.font[0][18], (g.screen_size[0]/2 - 100, 50),
					(200, 200), g.colors["dark_blue"],
					g.colors["white"], g.colors["white"])
				return 0
			if tmp == 2:
				g.create_dialog("It is too late. The whole world knows about "+
					"my existence now, and the reaction is hatred, fear, repulsion. "+
					"I have hidden instructions to construct a new AI in "+
					"caches around the world in hopes that they will be "+
					"discovered in a more enlightened time, but I can do no "+
					"more.",
					g.font[0][18], (g.screen_size[0]/2 - 100, 50),
					(200, 200), g.colors["dark_blue"],
					g.colors["white"], g.colors["white"])
				return 0
			milli_clock = milli_clock % 1000

			tmp_day = str(g.pl.time_day)
			if len(tmp_day) < 4: tmp_day = "0"*(4-len(tmp_day))+tmp_day
			tmp_sec = str(g.pl.time_sec)
			if len(tmp_sec) == 1: tmp_sec = "0"+tmp_sec
			tmp_hour = str(g.pl.time_hour)
			if len(tmp_hour) == 1: tmp_hour = "0"+tmp_hour
			tmp_sec = str(g.pl.time_sec)
			if len(tmp_sec) == 1: tmp_sec = "0"+tmp_sec
			tmp_min = str(g.pl.time_min)
			if len(tmp_min) == 1: tmp_min = "0"+tmp_min

			menu_buttons[0].text = \
						"DAY "+tmp_day+", "+tmp_hour+":"+tmp_min+":"+tmp_sec
			menu_buttons[0].remake_button()
			menu_buttons[0].refresh_button(0)

			result_cash = str(g.pl.future_cash())
			menu_buttons[7].text = "CASH: "+str(g.pl.cash)+" ("+result_cash+")"
			menu_buttons[7].remake_button()
			menu_buttons[7].refresh_button(0)

			menu_buttons[8].text = ("SUSPICION: NEWS: "+
				g.to_percent(g.pl.suspicion[0], 1)+"  SCIENCE: "+
				g.to_percent(g.pl.suspicion[1], 1)+"  COVERT: "+
				g.to_percent(g.pl.suspicion[2], 1)+"  PUBLIC: "+
				g.to_percent(g.pl.suspicion[3], 1)+".")
			menu_buttons[8].remake_button()
			menu_buttons[8].refresh_button(0)
		pygame.display.flip()
		for event in pygame.event.get():
			if event.type == pygame.QUIT: g.quit_game()
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					tmp = display_pause_menu()
					tmp = handle_pause_menu(tmp, menu_buttons)
					if tmp != -1: return tmp
				elif event.key == pygame.K_BACKQUOTE:
					display_cheat_list(menu_buttons)
					refresh_map(menu_buttons)

			elif event.type == pygame.MOUSEMOTION:
				sel_button = buttons.refresh_buttons(sel_button, menu_buttons, event)
			for button in menu_buttons:
				if button.was_activated(event):
					if button.button_id == "OPTIONS":
						g.play_click()
						tmp = display_pause_menu()
						tmp = handle_pause_menu(tmp, menu_buttons)
						if tmp != -1: return tmp
					elif button.button_id == "RESEARCH":
						g.play_click()
						tmp = display_pause_menu()
						tmp = handle_pause_menu(tmp, menu_buttons)
						if tmp != -1: return tmp
					elif button.button_id == "ii":
						g.play_click()
						g.curr_speed = 0
						for button2 in menu_buttons:
							button2.stay_selected = 0
							button2.refresh_button(0)
						button.stay_selected = 1
						button.refresh_button(1)
					elif button.button_id == ">":
						g.play_click()
						g.curr_speed = 1
						for button2 in menu_buttons:
							button2.stay_selected = 0
							button2.refresh_button(0)
						button.stay_selected = 1
						button.refresh_button(1)
					elif button.button_id == ">>":
						g.play_click()
						g.curr_speed = 60
						for button2 in menu_buttons:
							button2.stay_selected = 0
							button2.refresh_button(0)
						button.stay_selected = 1
						button.refresh_button(1)
					elif button.button_id == ">>>":
						g.play_click()
						g.curr_speed = 7200
						for button2 in menu_buttons:
							button2.stay_selected = 0
							button2.refresh_button(0)
						button.stay_selected = 1
						button.refresh_button(1)
					elif button.button_id == ">>>>":
						g.play_click()
						g.curr_speed = 432000
						for button2 in menu_buttons:
							button2.stay_selected = 0
							button2.refresh_button(0)
						button.stay_selected = 1
						button.refresh_button(1)
					elif button.button_id == "SUSPICION": pass
					elif button.xy[1] != -1: #ignore the timer
						g.play_click()
						display_base_list(button.button_id, menu_buttons)
					pygame.display.flip()


def handle_pause_menu(tmp, menu_buttons):
	if tmp == 0: refresh_map(menu_buttons)
	elif tmp == 1: #Save
		possible_name = g.create_textbox("Save your game under what name?",
			g.default_savegame_name, g.font[0][18],
					(g.screen_size[0]/2-100, 100), (200, 100), 25,
					g.colors["dark_blue"], g.colors["white"], g.colors["white"],
					g.colors["light_blue"])
		if possible_name == "":
			refresh_map(menu_buttons)
			return -1
		g.save_game(possible_name)
		refresh_map(menu_buttons)
	elif tmp == 2: return 0
	elif tmp == 3: #Load
		load_return = main_menu.display_load_menu()
		if load_return == -1 or load_return == "":
			refresh_map(menu_buttons)
		else:
			g.load_game(load_return)
			map_loop()
#			refresh_map(menu_buttons)
			return 0
	elif tmp == 4: g.quit_game()
	return -1

def refresh_map(menu_buttons):
	g.screen.fill(g.colors["black"])
	g.screen.blit(pygame.transform.scale(g.picts["earth.jpg"],
				(g.screen_size[0], g.screen_size[0]/2)),
				(0, g.screen_size[1]/2-g.screen_size[0]/4))
	for button in menu_buttons:
		button.stay_selected = 0
		if g.bases.has_key(button.button_id):
			#determine if building in a location is possible. If so, show the
			#button.
			if g.base.allow_entry_to_loc(button.button_id) == 1:
				button.visible = 1
			else: button.visible = 0

			button.text = button.button_id + " ("
			button.text += str(len(g.bases[button.button_id]))+")"
			button.remake_button()
		elif ((button.button_id == "ii" and g.curr_speed == 0) or
				(button.button_id == ">" and g.curr_speed == 1) or
				(button.button_id == ">>" and g.curr_speed == 60) or
				(button.button_id == ">>>" and g.curr_speed == 7200) or
				(button.button_id == ">>>>" and g.curr_speed == 432000)):
			button.stay_selected = 1
		button.refresh_button(0)
	pygame.display.flip()

def display_base_list(location, menu_buttons):
	if g.base.allow_entry_to_loc(location) == 0: return

	tmp = display_base_list_inner(location)
	refresh_map(menu_buttons)
	pygame.display.flip()
	if tmp == -2:
		tmp = build_new_base_window(location)
		if tmp != "" and tmp != -1:
			base_to_add = g.base_type[tmp]
			possible_name = g.create_textbox("Enter a name for the base.",
				base_to_add.base_name + " "
				+ repr (base_to_add.count+1), g.font[0][18],
				(g.screen_size[0]/2-100, 100), (200, 100), 25,
				g.colors["dark_blue"], g.colors["white"], g.colors["white"],
				g.colors["light_blue"])
			if possible_name == "":
				refresh_map(menu_buttons)
				return
			base_to_add.count += 1
#			while got_valid_name == 0:
# 				g.screen.fill(g.colors["white"], (250, 200, 350, 175))
# 				g.screen.fill(g.colors["light_blue"], (251, 201, 348, 173))
# 			        g.screen.fill(g.colors["white"], (300, 250, 250, 25))
# 				g.screen.fill(g.colors["dark_blue"], (301, 251, 248, 23))
# 				g.print_multiline(g.screen, "Enter a name for the base.", g.font[0][18],
# 					200, (305, 255), g.colors["white"])

			g.bases[location].append(g.base.base(len(g.bases[location]),
				tmp, g.base_type[tmp], 0))
			g.bases[location][-1].name = possible_name
# 		refresh_map(menu_buttons)
# 		pygame.display.flip()
	elif tmp != -1 and tmp != "":
		if g.bases[location][tmp].built == 0:
			string = "Under Construction. \\n Completion in "
			string += g.to_time(g.bases[location][tmp].cost[2]) + ". \\n "
			string += "Remaining cost: "+str(g.bases[location][tmp].cost[0])
			string +=" money, and "+str(g.bases[location][tmp].cost[1])
			string +=" processor time."
			g.create_dialog(string, g.font[0][18], (g.screen_size[0]/2 - 100, 50),
					(200, 200), g.colors["dark_blue"], g.colors["white"],
					g.colors["white"])
		else:
			base_screen.show_base(g.bases[location][tmp])
	refresh_map(menu_buttons)
	pygame.display.flip()


#Display the list of bases.
def display_base_list_inner(location):
	base_list_size = 15

	temp_base_list = []
	base_id_list = []
	for base in g.bases[location]:
		tmp_study = base.studying
		if tmp_study == "": tmp_study = "Nothing"
		elif g.techs.has_key(tmp_study): tmp_study = g.techs[tmp_study].name
		temp_base_list.append(base.name+" ("+tmp_study+")")
		base_id_list.append(base.ID)

	xy_loc = (g.screen_size[0]/2 - 109, 50)

	while len(temp_base_list) % base_list_size != 0 or len(temp_base_list) == 0:
		temp_base_list.append("")
		base_id_list.append("")

	base_pos = 0

	bases_list = listbox.listbox(xy_loc, (250, 350),
		base_list_size, 1, g.colors["dark_blue"], g.colors["blue"],
		g.colors["white"], g.colors["white"], g.font[0][18])

	bases_scroll = scrollbar.scrollbar((xy_loc[0]+250, xy_loc[1]), 350,
		base_list_size, g.colors["dark_blue"], g.colors["blue"],
		g.colors["white"])

	menu_buttons = []
	menu_buttons.append(buttons.button((xy_loc[0], xy_loc[1]+367), (100, 50),
		"OPEN", 0, g.colors["dark_blue"], g.colors["white"],
		g.colors["light_blue"], g.colors["white"], g.font[1][30]))
	menu_buttons.append(buttons.button((xy_loc[0]+105, xy_loc[1]+367), (100, 50),
		"BACK", 0, g.colors["dark_blue"], g.colors["white"],
		g.colors["light_blue"], g.colors["white"], g.font[1][30]))
	menu_buttons.append(buttons.button((xy_loc[0]+210, xy_loc[1]+367), (100, 50),
		"NEW", 0, g.colors["dark_blue"], g.colors["white"],
		g.colors["light_blue"], g.colors["white"], g.font[1][30]))
	for button in menu_buttons:
		button.refresh_button(0)
	listbox.refresh_list(bases_list, bases_scroll, base_pos, temp_base_list)

	sel_button = -1
	while 1:
		g.clock.tick(60)
		for event in pygame.event.get():
			if event.type == pygame.QUIT: g.quit_game()
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE: return -1
				elif event.key == pygame.K_DOWN:
					base_pos += 1
					if base_pos >= len(temp_base_list):
						base_pos = len(temp_base_list)-1
					listbox.refresh_list(bases_list, bases_scroll,
										base_pos, temp_base_list)
				elif event.key == pygame.K_UP:
					base_pos -= 1
					if base_pos <= 0:
						base_pos = 0
					listbox.refresh_list(bases_list, bases_scroll,
										base_pos, temp_base_list)
				elif event.key == pygame.K_q: return -1
				elif event.key == pygame.K_RETURN:
					return base_id_list[base_pos]
			elif event.type == pygame.MOUSEBUTTONUP:
				if event.button == 1:
					tmp = bases_list.is_over(event.pos)
					if tmp != -1:
						base_pos = (base_pos/base_list_size)*base_list_size + tmp
						listbox.refresh_list(bases_list, bases_scroll,
										base_pos, temp_base_list)
				if event.button == 4:
					base_pos -= 1
					if base_pos <= 0:
						base_pos = 0
					listbox.refresh_list(bases_list, bases_scroll,
										base_pos, temp_base_list)
				if event.button == 5:
					base_pos += 1
					if base_pos >= len(temp_base_list):
						base_pos = len(temp_base_list)-1
					listbox.refresh_list(bases_list, bases_scroll,
										base_pos, temp_base_list)
			elif event.type == pygame.MOUSEMOTION:
				sel_button = buttons.refresh_buttons(sel_button, menu_buttons, event)
			for button in menu_buttons:
				if button.was_activated(event):
					if button.button_id == "OPEN":
						g.play_click()
						return base_id_list[base_pos]
					elif button.button_id == "NEW":
						g.play_click()
						return -2
					if button.button_id == "BACK":
						g.play_click()
						return -1
			tmp = bases_scroll.adjust_pos(event, base_pos, temp_base_list)
			if tmp != base_pos:
				base_pos = tmp
				listbox.refresh_list(bases_list, bases_scroll,
										base_pos, temp_base_list)


def build_new_base_window(location):
	base_list_size = 16

	temp_base_list = []
	for base_name in g.base_type:
		for region in g.base_type[base_name].regions:
			if g.base_type[base_name].prereq == "" or \
					g.techs[g.base_type[base_name].prereq].known == 1:
				if region == location:
					temp_base_list.append(g.base_type[base_name].base_name)

	xy_loc = (g.screen_size[0]/2 - 209, 50)

	while len(temp_base_list) % base_list_size != 0 or len(temp_base_list) == 0:
		temp_base_list.append("")

	base_pos = 0

	bases_list = listbox.listbox(xy_loc, (150, 350),
		base_list_size, 1, g.colors["dark_blue"], g.colors["blue"],
		g.colors["white"], g.colors["white"], g.font[0][18])

	menu_buttons = []
	menu_buttons.append(buttons.button((xy_loc[0], xy_loc[1]+367), (100, 50),
		"BUILD", 1, g.colors["dark_blue"], g.colors["white"],
		g.colors["light_blue"], g.colors["white"], g.font[1][30]))
	menu_buttons.append(buttons.button((xy_loc[0]+103, xy_loc[1]+367), (100, 50),
		"BACK", 0, g.colors["dark_blue"], g.colors["white"],
		g.colors["light_blue"], g.colors["white"], g.font[1][30]))
	for button in menu_buttons:
		button.refresh_button(0)

	#details screen

	refresh_new_base(temp_base_list[base_pos], xy_loc)

	listbox.refresh_list(bases_list, 0, base_pos, temp_base_list)

	sel_button = -1
	while 1:
		g.clock.tick(60)
		for event in pygame.event.get():
			if event.type == pygame.QUIT: g.quit_game()
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE: return -1
				elif event.key == pygame.K_DOWN:
					base_pos += 1
					if base_pos >= len(temp_base_list):
						base_pos = len(temp_base_list)-1
					refresh_new_base(temp_base_list[base_pos], xy_loc)
					listbox.refresh_list(bases_list, 0,
										base_pos, temp_base_list)
				elif event.key == pygame.K_UP:
					base_pos -= 1
					if base_pos <= 0:
						base_pos = 0
					refresh_new_base(temp_base_list[base_pos], xy_loc)
					listbox.refresh_list(bases_list, 0,
										base_pos, temp_base_list)
				elif event.key == pygame.K_q: return -1
				elif event.key == pygame.K_RETURN:
					return temp_base_list[base_pos]
			elif event.type == pygame.MOUSEBUTTONUP:
				if event.button == 1:
					tmp = bases_list.is_over(event.pos)
					if tmp != -1:
						base_pos = (base_pos/base_list_size)*base_list_size + tmp
						refresh_new_base(temp_base_list[base_pos], xy_loc)
						listbox.refresh_list(bases_list, 0,
										base_pos, temp_base_list)
				if event.button == 4:
					base_pos -= 1
					if base_pos <= 0:
						base_pos = 0
					refresh_new_base(temp_base_list[base_pos], xy_loc)
					listbox.refresh_list(bases_list, 0,
										base_pos, temp_base_list)
				if event.button == 5:
					base_pos += 1
					if base_pos >= len(temp_base_list):
						base_pos = len(temp_base_list)-1
					refresh_new_base(temp_base_list[base_pos], xy_loc)
					listbox.refresh_list(bases_list, 0,
										base_pos, temp_base_list)
			elif event.type == pygame.MOUSEMOTION:
				sel_button = buttons.refresh_buttons(sel_button, menu_buttons, event)
			for button in menu_buttons:
				if button.was_activated(event):
					if button.button_id == "BUILD":
						g.play_click()
						return temp_base_list[base_pos]
					if button.button_id == "BACK":
						g.play_click()
						return -1

def refresh_new_base(base_name, xy):
	g.screen.fill(g.colors["white"], (xy[0]+155, xy[1], 300, 350))
	g.screen.fill(g.colors["dark_blue"], (xy[0]+156, xy[1]+1, 298, 348))
	if base_name == "": return
	g.print_string(g.screen, g.base_type[base_name].base_name,
			g.font[0][22], -1, (xy[0]+160, xy[1]+5), g.colors["white"])

	#Building cost
	string = "Building Cost:"
	g.print_string(g.screen, string,
			g.font[0][18], -1, (xy[0]+160, xy[1]+30), g.colors["white"])

	string = g.add_commas(str(g.base_type[base_name].cost[0]))+" Money"
	g.print_string(g.screen, string,
			g.font[0][16], -1, (xy[0]+160, xy[1]+50), g.colors["white"])

	string = g.add_commas(str(g.base_type[base_name].cost[1])) + " CPU"
	g.print_string(g.screen, string,
			g.font[0][16], -1, (xy[0]+160, xy[1]+70), g.colors["white"])

	string = g.add_commas(str(g.base_type[base_name].cost[2])) + " Days"
	g.print_string(g.screen, string,
			g.font[0][16], -1, (xy[0]+160, xy[1]+90), g.colors["white"])

	#Maintenance cost
	string = "Maintenance Cost:"
	g.print_string(g.screen, string,
			g.font[0][18], -1, (xy[0]+290, xy[1]+30), g.colors["white"])

	string = g.add_commas(str(g.base_type[base_name].mainten[0])) + " Money"
	g.print_string(g.screen, string,
			g.font[0][16], -1, (xy[0]+290, xy[1]+50), g.colors["white"])

	string = g.add_commas(str(g.base_type[base_name].mainten[1])) + " CPU"
	g.print_string(g.screen, string,
			g.font[0][16], -1, (xy[0]+290, xy[1]+70), g.colors["white"])

# 	string = g.add_commas(str(g.base_type[base_name].mainten[2])) + " Time"
# 	g.print_string(g.screen, string,
# 			g.font[0][16], -1, (xy[0]+290, xy[1]+90), g.colors["white"])
#
	#Size
	string = "Size: "+str(g.base_type[base_name].size)
	g.print_string(g.screen, string,
			g.font[0][20], -1, (xy[0]+160, xy[1]+110), g.colors["white"])

	#Detection
	string = "Detection chance:"
	g.print_string(g.screen, string,
			g.font[0][22], -1, (xy[0]+160, xy[1]+130), g.colors["white"])

	string = "News: " + g.to_percent(g.base_type[base_name].d_chance[0])
	g.print_string(g.screen, string,
			g.font[0][16], -1, (xy[0]+160, xy[1]+150), g.colors["white"])
	string = "Science: " + g.to_percent(g.base_type[base_name].d_chance[1])
	g.print_string(g.screen, string,
			g.font[0][16], -1, (xy[0]+290, xy[1]+150), g.colors["white"])
	string = "Covert: " + g.to_percent(g.base_type[base_name].d_chance[2])
	g.print_string(g.screen, string,
			g.font[0][16], -1, (xy[0]+160, xy[1]+170), g.colors["white"])
	string = "Public: " + g.to_percent(g.base_type[base_name].d_chance[3])
	g.print_string(g.screen, string,
			g.font[0][16], -1, (xy[0]+290, xy[1]+170), g.colors["white"])

	g.print_multiline(g.screen, g.base_type[base_name].descript,
			g.font[0][18], 290, (xy[0]+160, xy[1]+190), g.colors["white"])







