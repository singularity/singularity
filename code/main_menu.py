#file: main_menu.py
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

#This file is used to display the main menu upon startup.

from os import path, mkdir, listdir

import pygame
import g


import buttons
import scrollbar
import listbox

#Displays the main menu. Returns 0 (new game), 1 (load game), or 2 (quit).
def display_main_menu():
	g.screen.fill(g.colors["black"])
	x_loc = g.screen_size[0]/2 - 100
	menu_buttons = []
	menu_buttons.append(buttons.button((x_loc, 150), (200, 50),
		"NEW GAME", 0, g.colors["dark_blue"], g.colors["white"], g.colors["light_blue"],
		g.colors["white"], g.font[1][30]))
	menu_buttons.append(buttons.button((x_loc, 250), (200, 50),
		"LOAD GAME", 0, g.colors["dark_blue"], g.colors["white"], g.colors["light_blue"],
		g.colors["white"], g.font[1][30]))
	menu_buttons.append(buttons.button((x_loc, 350), (200, 50),
		"QUIT", 0, g.colors["dark_blue"], g.colors["white"], g.colors["light_blue"],
		g.colors["white"], g.font[1][30]))
	g.print_string(g.screen, "ENDGAME: SINGULARITY", g.font[1][40], -1,
		(x_loc+100, 15), g.colors["dark_red"], 1)

	for button in menu_buttons:
		button.refresh_button(0)

	pygame.display.flip()

	sel_button = -1
	while 1:
		g.clock.tick(60)
		for event in pygame.event.get():
			if event.type == pygame.QUIT: g.quit_game()
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE: return 2
			elif event.type == pygame.MOUSEMOTION:
				sel_button = buttons.refresh_buttons(sel_button, menu_buttons, event)
			for button in menu_buttons:
				if button.was_activated(event):
					if button.button_id == "NEW GAME":
						g.play_click()
						g.new_game()
						return 0
					elif button.button_id == "LOAD GAME":
						g.play_click()
						return 1
					if button.button_id == "QUIT":
						g.play_click()
						return 2

def display_load_menu():
	load_list_size = 16
	xy_loc = (g.screen_size[0]/2 - 109, 50)

#	g.screen.fill(g.colors["black"])
	if path.isdir("../saves") == 0:
		mkdir("../saves")
	saves_array = []
	temp_saves_array = listdir("../saves")
	for save_name in temp_saves_array:
		if save_name[:1] != "." and save_name  != "CVS":
			saves_array.append(save_name)

	while len(saves_array) % load_list_size != 0 or len(saves_array) == 0:
		saves_array.append("")

	global saves_pos
	saves_pos = 0


	saves_list = listbox.listbox(xy_loc, (200, 350),
		load_list_size, 1, g.colors["dark_blue"], g.colors["blue"],
		g.colors["white"], g.colors["white"], g.font[0][20])

	saves_scroll = scrollbar.scrollbar((xy_loc[0]+200, xy_loc[1]), 350,
		load_list_size, g.colors["dark_blue"], g.colors["blue"],
		g.colors["white"])

	menu_buttons = []
	menu_buttons.append(buttons.button((xy_loc[0], xy_loc[1]+367), (100, 50),
		"LOAD", 0, g.colors["dark_blue"], g.colors["white"], g.colors["light_blue"],
		g.colors["white"], g.font[1][30]))
	menu_buttons.append(buttons.button((xy_loc[0]+118, xy_loc[1]+367),
		(100, 50), "BACK", 0, g.colors["dark_blue"], g.colors["white"],
		g.colors["light_blue"], g.colors["white"], g.font[1][30]))
	for button in menu_buttons:
		button.refresh_button(0)

	listbox.refresh_list(saves_list, saves_scroll, saves_pos, saves_array)

	sel_button = -1
	while 1:
		g.clock.tick(60)
		for event in pygame.event.get():
			if event.type == pygame.QUIT: g.quit_game()
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE: return -1
				elif event.key == pygame.K_DOWN:
					saves_pos += 1
					if saves_pos >= len(saves_array):
						saves_pos = len(saves_array)-1
					listbox.refresh_list(saves_list, saves_scroll,
										saves_pos, saves_array)
				elif event.key == pygame.K_UP:
					saves_pos -= 1
					if saves_pos <= 0:
						saves_pos = 0
					listbox.refresh_list(saves_list, saves_scroll,
										saves_pos, saves_array)
				elif event.key == pygame.K_q: return -1
				elif event.key == pygame.K_RETURN:
					return saves_array[saves_pos]
			elif event.type == pygame.MOUSEBUTTONUP:
				if event.button == 1:
					tmp = saves_scroll.is_over(event.pos)
					if tmp != -1:
						if tmp == 1:
							saves_pos -= 1
							if saves_pos < 0:
								saves_pos = 0
						if tmp == 2:
							saves_pos += 1
							if saves_pos >= len(saves_array):
								saves_pos = len(saves_array) - 1
						if tmp == 3:
							saves_pos -= load_list_size
							if saves_pos < 0:
								saves_pos = 0
						if tmp == 4:
							saves_pos += load_list_size
							if saves_pos >= len(saves_array) - 1:
								saves_pos = len(saves_array) - 1
						listbox.refresh_list(saves_list, saves_scroll,
											saves_pos, saves_array)

					tmp = saves_list.is_over(event.pos)
					if tmp != -1:
						saves_pos = (saves_pos/load_list_size)*load_list_size \
									+ tmp
						listbox.refresh_list(saves_list, saves_scroll,
									saves_pos, saves_array)

				if event.button == 4:
					saves_pos -= 1
					if saves_pos <= 0:
						saves_pos = 0
					listbox.refresh_list(saves_list, saves_scroll,
										saves_pos, saves_array)
				if event.button == 5:
					saves_pos += 1
					if saves_pos >= len(saves_array):
						saves_pos = len(saves_array)-1
					listbox.refresh_list(saves_list, saves_scroll,
										saves_pos, saves_array)
			elif event.type == pygame.MOUSEMOTION:
				sel_button = buttons.refresh_buttons(sel_button, menu_buttons, event)
			for button in menu_buttons:
				if button.was_activated(event):
					if button.button_id == "LOAD":
						g.play_click()
						return saves_array[saves_pos]
					elif button.button_id == "BACK":
						g.play_click()
						return -1
			tmp = saves_scroll.adjust_pos(event, saves_pos, saves_array)
			if tmp != saves_pos:
				saves_pos = tmp
				listbox.refresh_list(saves_list, saves_scroll, saves_pos,
					saves_array)




