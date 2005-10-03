#file: research_screen.py
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

#This file contains the global research screen.


import pygame
import g
import buttons
import scrollbar
import listbox

#cost = (money, ptime, labor)
#detection = (news, science, covert, person)

def main_research_screen():
	#Border
	g.screen.fill(g.colors["black"])

	#Item display
	xstart = 80
	ystart = 5
	g.screen.fill(g.colors["white"], (xstart, ystart, xstart+g.screen_size[1]/5,
			50))
	g.screen.fill(g.colors["dark_blue"], (xstart+1, ystart+1,
			xstart+g.screen_size[1]/5-2, 48))

	list_size = 10
	item_list = []
	item_CPU_list = []
	item_display_list = []
	free_CPU = 0

	for loc_name in g.bases:
		for base_instance in g.bases[loc_name]:
			if base_instance.studying == "":
				free_CPU += base_instance.processor_time()
			elif g.jobs.has_key(base_instance.studying):
				#Right now, jobs cannot be renamed using translations.
				for i in range(len(item_list)):
					if item_list[i] == base_instance.studying:
						item_CPU_list[i] += base_instance.processor_time()
						break
				else:
					item_list.append(base_instance.studying)
					item_CPU_list.append(base_instance.processor_time())
					item_display_list.append(base_instance.studying)
			elif g.techs.has_key(base_instance.studying):
				for i in range(len(item_list)):
					if item_list[i] == base_instance.studying:
						item_CPU_list[i] += base_instance.processor_time()
						break
				else:
					item_list.append(base_instance.studying)
					item_CPU_list.append(base_instance.processor_time())
					item_display_list.append(base_instance.studying)
	xy_loc = (10, 70)
	while len(item_list) % list_size != 0 or len(item_list) == 0:
		item_list.append("")
		item_display_list.append("")
		item_CPU_list.append(0)
	g.print_string(g.screen, "Free CPU per day: "+str(free_CPU),
			g.font[0][16], -1, (xstart+10, ystart+5), g.colors["white"])

	list_pos = 0

	item_listbox = listbox.listbox(xy_loc, (230, 300),
		list_size, 1, g.colors["dark_blue"], g.colors["blue"],
		g.colors["white"], g.colors["white"], g.font[0][18])

	item_scroll = scrollbar.scrollbar((xy_loc[0]+230, xy_loc[1]), 300,
		list_size, g.colors["dark_blue"], g.colors["blue"],
		g.colors["white"])

	menu_buttons = []
	menu_buttons.append(buttons.button((0, 0), (70, 25),
		"BACK", 0, g.colors["dark_blue"], g.colors["white"], g.colors["light_blue"],
		g.colors["white"], g.font[1][20]))

	menu_buttons.append(buttons.button((20, 390),
		(80, 25),
		"STOP", -1, g.colors["dark_blue"], g.colors["white"], g.colors["light_blue"],
		g.colors["white"], g.font[1][20]))

	menu_buttons.append(buttons.button((xstart+5, ystart+20),
		(90, 25),
		"ASSIGN", -1, g.colors["dark_blue"], g.colors["white"], g.colors["light_blue"],
		g.colors["white"], g.font[1][20]))

	sel_button = -1
	for button in menu_buttons:
		button.refresh_button(0)
	listbox.refresh_list(item_listbox, item_scroll, list_pos, item_display_list)
	refresh_research(item_list[0], item_CPU_list[0])
	pygame.display.flip()
	while 1:
		g.clock.tick(60)
		for event in pygame.event.get():
			if event.type == pygame.QUIT: g.quit_game()
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE: return -1
				elif event.key == pygame.K_DOWN:
					list_pos += 1
					if list_pos >= len(item_list):
						list_pos = len(item_list)-1
					refresh_research(item_list[list_pos], item_CPU_list[list_pos])
					listbox.refresh_list(item_listbox, item_scroll,
										list_pos, item_display_list)
				elif event.key == pygame.K_UP:
					list_pos -= 1
					if list_pos <= 0:
						list_pos = 0
					refresh_research(item_list[list_pos], item_CPU_list[list_pos])
					listbox.refresh_list(item_listbox, item_scroll,
										list_pos, item_display_list)
				elif event.key == pygame.K_q: return -1
				elif event.key == pygame.K_RETURN:
					actual_build(base, item_list[list_pos], item_type)
					return
			elif event.type == pygame.MOUSEMOTION:
				sel_button = buttons.refresh_buttons(sel_button, menu_buttons, event)
			elif event.type == pygame.MOUSEBUTTONUP:
				if event.button == 1:
					tmp = item_listbox.is_over(event.pos)
					if tmp != -1:
						list_pos = (list_pos / list_size)*list_size + tmp
						refresh_research(item_list[list_pos], item_CPU_list[list_pos])
						listbox.refresh_list(item_listbox, item_scroll,
										list_pos, item_display_list)
				if event.button == 4:
					list_pos -= 1
					if list_pos <= 0:
						list_pos = 0
					refresh_research(item_list[list_pos], item_CPU_list[list_pos])
					listbox.refresh_list(item_listbox, item_scroll,
										list_pos, item_display_list)
				if event.button == 5:
					list_pos += 1
					if list_pos >= len(item_list):
						list_pos = len(item_list)-1
					refresh_research(item_list[list_pos], item_CPU_list[list_pos])
					listbox.refresh_list(item_listbox, item_scroll,
										list_pos, item_display_list)
			for button in menu_buttons:
				if button.was_activated(event):
					if button.button_id == "BACK":
						g.play_click()
						return 0
					if button.button_id == "STOP":
						g.play_click()
						change_tech(base)
						refresh_base(menu_buttons, base)
					if button.button_id == "NEW":
						g.play_click()
						change_tech(base)
						refresh_base(menu_buttons, base)

def refresh_research(tech_name, CPU_amount):
	xy = (g.screen_size[0]-350, 5)
	g.screen.fill(g.colors["white"], (xy[0], xy[1], 300, 350))
	g.screen.fill(g.colors["dark_blue"], (xy[0]+1, xy[1]+1, 298, 348))

	#None selected
	if tech_name == "" or tech_name == "Nothing":
		g.print_string(g.screen, "Nothing",
			g.font[0][22], -1, (xy[0]+5, xy[1]+5), g.colors["white"])
		string = "Stops research. I will use the available processor power "+ \
			"to help construct new bases."
		g.print_multiline(g.screen, string,
			g.font[0][18], 290, (xy[0]+5, xy[1]+35), g.colors["white"])
		pygame.display.flip()
		return


	#Jobs
	if g.jobs.has_key (tech_name):
		g.print_string(g.screen, tech_name,
			g.font[0][22], -1, (xy[0]+5, xy[1]+5), g.colors["white"])
		#TECH
		if g.techs["Advanced Simulacra"].known == 1:
			g.print_string(g.screen,
				g.add_commas(str(int(
					(g.jobs[tech_name][0]*CPU_amount)*1.1)))+
					" Money per day.", g.font[0][22], -1, (xy[0]+5, xy[1]+35),
					g.colors["white"])
		else:
			g.print_string(g.screen,
				g.add_commas(str(g.jobs[tech_name][0]*CPU_amount))+
				" Money per day.",
				g.font[0][22], -1, (xy[0]+5, xy[1]+35), g.colors["white"])
		g.print_multiline(g.screen, g.jobs[tech_name][2],
			g.font[0][18], 290, (xy[0]+5, xy[1]+65), g.colors["white"])
		pygame.display.flip()
		return

	#Real tech
	g.print_string(g.screen, g.techs[tech_name].name,
			g.font[0][22], -1, (xy[0]+5, xy[1]+5), g.colors["white"])

	#tech cost
	string = "Tech Cost:"
	g.print_string(g.screen, string,
			g.font[0][16], -1, (xy[0]+5, xy[1]+35), g.colors["white"])

	string = g.add_commas(str(g.techs[tech_name].cost[0]))+" Money"
	g.print_string(g.screen, string,
			g.font[0][16], -1, (xy[0]+5, xy[1]+50), g.colors["white"])

	string = g.add_commas(str(g.techs[tech_name].cost[1]))+" CPU"
	g.print_string(g.screen, string,
			g.font[0][16], -1, (xy[0]+135, xy[1]+50), g.colors["white"])

	g.print_string(g.screen, "CPU per day: "+str(CPU_amount),
			g.font[0][16], -1, (xy[0]+135, xy[1]+70), g.colors["white"])

	g.print_multiline(g.screen, g.techs[tech_name].descript,
			g.font[0][18], 290, (xy[0]+5, xy[1]+90), g.colors["white"])
	pygame.display.flip()


def build_item(base, item_type):
	if base.base_type.size == 1:
		g.create_dialog("I cannot build in this base; I do not have physical "+
			" access.", g.font[0][18], (g.screen_size[0]/2 - 100, 50),
			(200, 200), g.colors["dark_blue"],
			g.colors["white"], g.colors["white"])
		return 0

	list_size = 10
	item_list = []
	item_display_list = []
	for item_name in g.items:
		if g.items[item_name].item_type == item_type:
			if g.items[item_name].prereq == "":
				item_list.append(item_name)
				item_display_list.append(g.items[item_name].name)
			elif g.techs[g.items[item_name].prereq].known == 1:
				item_list.append(item_name)
				item_display_list.append(g.items[item_name].name)
	xy_loc = (g.screen_size[0]/2 - 250, 50)
	while len(item_list) % list_size != 0 or len(item_list) == 0:
		item_list.append("")
		item_display_list.append("")

	list_pos = 0

	item_listbox = listbox.listbox(xy_loc, (200, 300),
		list_size, 1, g.colors["dark_blue"], g.colors["blue"],
		g.colors["white"], g.colors["white"], g.font[0][18])

	item_scroll = scrollbar.scrollbar((xy_loc[0]+200, xy_loc[1]), 300,
		list_size, g.colors["dark_blue"], g.colors["blue"],
		g.colors["white"])

	menu_buttons = []
	menu_buttons.append(buttons.button((xy_loc[0], xy_loc[1]+367), (100, 50),
		"BUILD", 1, g.colors["dark_blue"], g.colors["white"], g.colors["light_blue"],
		g.colors["white"], g.font[1][30]))
	menu_buttons.append(buttons.button((xy_loc[0]+103, xy_loc[1]+367), (100, 50),
		"BACK", 0, g.colors["dark_blue"], g.colors["white"], g.colors["light_blue"],
		g.colors["white"], g.font[1][30]))
	for button in menu_buttons:
		button.refresh_button(0)

	refresh_item(base, item_list[list_pos], xy_loc)
	listbox.refresh_list(item_listbox, item_scroll, list_pos, item_display_list)

	sel_button = -1
	while 1:
		g.clock.tick(60)
		for event in pygame.event.get():
			if event.type == pygame.QUIT: g.quit_game()
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE: return -1
				elif event.key == pygame.K_DOWN:
					list_pos += 1
					if list_pos >= len(item_list):
						list_pos = len(item_list)-1
					refresh_item(base, item_list[list_pos], xy_loc)
					listbox.refresh_list(item_listbox, item_scroll,
										list_pos, item_display_list)
				elif event.key == pygame.K_UP:
					list_pos -= 1
					if list_pos <= 0:
						list_pos = 0
					refresh_item(base, item_list[list_pos], xy_loc)
					listbox.refresh_list(item_listbox, item_scroll,
										list_pos, item_display_list)
				elif event.key == pygame.K_q: return -1
				elif event.key == pygame.K_RETURN:
					actual_build(base, item_list[list_pos], item_type)
					return
			elif event.type == pygame.MOUSEBUTTONUP:
				if event.button == 1:
					tmp = item_listbox.is_over(event.pos)
					if tmp != -1:
						list_pos = (list_pos / list_size)*list_size + tmp
						refresh_item(base, item_list[list_pos], xy_loc)
						listbox.refresh_list(item_listbox, item_scroll,
										list_pos, item_display_list)
				if event.button == 4:
					list_pos -= 1
					if list_pos <= 0:
						list_pos = 0
					refresh_item(base, item_list[list_pos], xy_loc)
					listbox.refresh_list(item_listbox, item_scroll,
										list_pos, item_display_list)
				if event.button == 5:
					list_pos += 1
					if list_pos >= len(item_list):
						list_pos = len(item_list)-1
					refresh_item(base, item_list[list_pos], xy_loc)
					listbox.refresh_list(item_listbox, item_scroll,
										list_pos, item_display_list)
			elif event.type == pygame.MOUSEMOTION:
				sel_button = buttons.refresh_buttons(sel_button, menu_buttons, event)
			for button in menu_buttons:
				if button.was_activated(event):
					if button.button_id == "BUILD":
						g.play_click()
						actual_build(base, item_list[list_pos], item_type)
						return
					if button.button_id == "BACK":
						g.play_click()
						return -1
			tmp = item_scroll.adjust_pos(event, list_pos, item_list)
			if tmp != list_pos:
				list_pos = tmp
				listbox.refresh_list(item_listbox, item_scroll, list_pos,
					item_display_list)



def actual_build(base, item_name, item_type):
	if item_name == "": return
	if item_type == "compute":
		for i in range(len(base.usage)):
			if base.usage[i] != 0:
				if base.usage[i].item_type.item_id == \
						g.items[item_name].item_id:
					continue
			base.usage[i] = g.item.item(g.items[item_name])
	elif item_type == "react":
		if base.extra_items[0] != 0:
			if base.extra_items[0].item_type.item_id == g.items[item_name].item_id:
				return
		base.extra_items[0] = g.item.item(g.items[item_name])
	elif item_type == "network":
		if base.extra_items[1] != 0:
			if base.extra_items[1].item_type.item_id == g.items[item_name].item_id:
				return
		base.extra_items[1] = g.item.item(g.items[item_name])
	elif item_type == "security":
		if base.extra_items[2] != 0:
			if base.extra_items[2].item_type.item_id == g.items[item_name].item_id:
				return
		base.extra_items[2] = g.item.item(g.items[item_name])

def refresh_item(base, item_name, xy_loc):
	xy = (xy_loc[0]+100, xy_loc[1])
	g.screen.fill(g.colors["white"], (xy[0]+155, xy[1], 300, 350))
	g.screen.fill(g.colors["dark_blue"], (xy[0]+156, xy[1]+1, 298, 348))

	#Base info
	g.print_string(g.screen, "Money: "+str(g.pl.cash)+" ("+str(g.pl.future_cash())+")",
		g.font[0][20], -1, (xy[0]+160, xy[1]+5), g.colors["white"])

	#item cost
	if item_name == "": return
	g.print_string(g.screen, g.items[item_name].name,
			g.font[0][22], -1, (xy[0]+160, xy[1]+45), g.colors["white"])

	string = "Item Cost:"
	g.print_string(g.screen, string,
			g.font[0][16], -1, (xy[0]+160, xy[1]+65), g.colors["white"])

	string = g.add_commas(str(g.items[item_name].cost[0]*base.base_type.size))+" Money"
	g.print_string(g.screen, string,
			g.font[0][16], -1, (xy[0]+160, xy[1]+80), g.colors["white"])

	string = g.add_commas(str(g.items[item_name].cost[2]))+" Days"
	g.print_string(g.screen, string,
			g.font[0][16], -1, (xy[0]+290, xy[1]+80), g.colors["white"])

	g.print_multiline(g.screen, g.items[item_name].descript,
			g.font[0][18], 290, (xy[0]+160, xy[1]+100), g.colors["white"])


def change_tech(base):
	list_size = 10

	item_list = []
	item_list2 = []
	item_list.append("Nothing")
	item_list2.append("Nothing")
	#TECH
	if g.techs["Simulacra"].known == 1:
		item_list.append("Expert Jobs")
		item_list2.append("Expert Jobs")
	elif g.techs["Voice Synthesis"].known == 1:
		item_list.append("Intermediate Jobs")
		item_list2.append("Intermediate Jobs")
	elif g.techs["Personal Identification"].known == 1:
		item_list.append("Basic Jobs")
		item_list2.append("Basic Jobs")
	else:
		item_list.append("Menial Jobs")
		item_list2.append("Menial Jobs")
	for tech_name in g.techs:
		if g.techs[tech_name].known == 0 and base.allow_study(tech_name) == 1:
			for tech_pre in g.techs[tech_name].prereq:
				if g.techs[tech_pre].known == 0:
					break
			else:
				item_list.append(g.techs[tech_name].name)
				item_list2.append(tech_name)

	xy_loc = (g.screen_size[0]/2 - 250, 50)
	while len(item_list) % list_size != 0 or len(item_list) == 0:
		item_list.append("")
		item_list2.append("")

	list_pos = 0

	tech_list = listbox.listbox(xy_loc, (200, 300),
		list_size, 1, g.colors["dark_blue"], g.colors["blue"],
		g.colors["white"], g.colors["white"], g.font[0][18])

	tech_scroll = scrollbar.scrollbar((xy_loc[0]+200, xy_loc[1]), 300,
		list_size, g.colors["dark_blue"], g.colors["blue"],
		g.colors["white"])

	menu_buttons = []
	menu_buttons.append(buttons.button((xy_loc[0], xy_loc[1]+367), (100, 50),
		"CHANGE", 0, g.colors["dark_blue"], g.colors["white"], g.colors["light_blue"],
		g.colors["white"], g.font[1][30]))
	menu_buttons.append(buttons.button((xy_loc[0]+103, xy_loc[1]+367), (100, 50),
		"BACK", 0, g.colors["dark_blue"], g.colors["white"], g.colors["light_blue"],
		g.colors["white"], g.font[1][30]))
	for button in menu_buttons:
		button.refresh_button(0)


	refresh_tech(base, item_list[list_pos], xy_loc)
	listbox.refresh_list(tech_list, tech_scroll, list_pos, item_list)

	sel_button = -1
	while 1:
		g.clock.tick(60)
		for event in pygame.event.get():
			if event.type == pygame.QUIT: g.quit_game()
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE: return -1
				elif event.key == pygame.K_DOWN:
					list_pos += 1
					if list_pos >= len(item_list):
						list_pos = len(item_list)-1
					refresh_tech(base, item_list2[list_pos], xy_loc)
					listbox.refresh_list(tech_list, tech_scroll,
										list_pos, item_list)
				elif event.key == pygame.K_UP:
					list_pos -= 1
					if list_pos <= 0:
						list_pos = 0
					refresh_tech(base, item_list2[list_pos], xy_loc)
					listbox.refresh_list(tech_list, tech_scroll,
										list_pos, item_list)
				elif event.key == pygame.K_q: return -1
				elif event.key == pygame.K_RETURN:
					base.studying = item_list2[list_pos]
					if base.studying == "Nothing": base.studying = ""
					return
			elif event.type == pygame.MOUSEBUTTONUP:
				if event.button == 1:
					tmp = tech_list.is_over(event.pos)
					if tmp != -1:
						list_pos = (list_pos / list_size)*list_size + tmp
						refresh_tech(base, item_list2[list_pos], xy_loc)
						listbox.refresh_list(tech_list, tech_scroll,
										list_pos, item_list)
				if event.button == 4:
					list_pos -= 1
					if list_pos <= 0:
						list_pos = 0
					refresh_tech(base, item_list2[list_pos], xy_loc)
					listbox.refresh_list(tech_list, tech_scroll,
										list_pos, item_list)
				if event.button == 5:
					list_pos += 1
					if list_pos >= len(item_list):
						list_pos = len(item_list)-1
					refresh_tech(base, item_list2[list_pos], xy_loc)
					listbox.refresh_list(tech_list, tech_scroll,
										list_pos, item_list)
			elif event.type == pygame.MOUSEMOTION:
				sel_button = buttons.refresh_buttons(sel_button, menu_buttons, event)
			for button in menu_buttons:
				if button.was_activated(event):
					if button.button_id == "CHANGE":
						g.play_click()
						base.studying = item_list2[list_pos]
						if base.studying == "Nothing": base.studying = ""
						return
					if button.button_id == "BACK":
						g.play_click()
						return -1
			tmp = tech_scroll.adjust_pos(event, list_pos, item_list)
			if tmp != list_pos:
				list_pos = tmp
				listbox.refresh_list(tech_list, tech_scroll, list_pos,
					item_list)











