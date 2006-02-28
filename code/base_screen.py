#file: base_screen.py
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

#This file contains the screen to display the base screen.


import pygame
import g
import buttons
import scrollbar
import listbox

#cost = (money, ptime, labor)
#detection = (news, science, covert, person)

def show_base(base):
	#Border
	g.screen.fill(g.colors["black"])

	menu_buttons = []
	menu_buttons.append(buttons.make_norm_button((0, 0), (70, 25),
		"BACK", 0, g.font[1][20]))

	menu_buttons.append(buttons.button((70, -1), (g.screen_size[0]-70, 26),
		"DETECTION CHANCE", -1, g.colors["black"], g.colors["dark_blue"],
		g.colors["black"], g.colors["white"], g.font[1][15]))

	menu_buttons.append(buttons.make_norm_button((0, g.screen_size[1]-50),
		(170, 25), "CHANGE RESEARCH", 0, g.font[1][20], "CHANGE"))

	menu_buttons.append(buttons.button((0, g.screen_size[1]-25),
		(g.screen_size[0]-40, 26),
		"STUDYING:", -1, g.colors["black"], g.colors["dark_blue"],
		g.colors["black"], g.colors["white"], g.font[1][15]))

	menu_buttons.append(buttons.make_norm_button((320, 60), (70, 26),
		"CHANGE", -1, g.font[1][15], "C_PROCESSOR"))
	menu_buttons[4].activate_key = "p"

	menu_buttons.append(buttons.make_norm_button((320, 110), (70, 26),
		"CHANGE", -1, g.font[1][15], "C_REACTOR"))
	menu_buttons[5].activate_key = "r"

	menu_buttons.append(buttons.make_norm_button((320, 160), (70, 26),
		"CHANGE", -1, g.font[1][15], "C_NETWORK"))
	menu_buttons[6].activate_key = "n"

	menu_buttons.append(buttons.make_norm_button((320, 210),
		(70, 26), "CHANGE", -1, g.font[1][15], "C_SECURITY"))
	menu_buttons[7].activate_key = "s"

	menu_buttons.append(buttons.make_norm_button((g.screen_size[0]-40,
		g.screen_size[1]-25), (20, 25), "<", 0, g.font[1][20]))

	menu_buttons.append(buttons.make_norm_button((g.screen_size[0]-20,
		g.screen_size[1]-25), (20, 25), ">", 0, g.font[1][20]))

	menu_buttons.append(buttons.make_norm_button((g.screen_size[0]-90,
		g.screen_size[1]-50), (90, 25), "DESTROY", 0, g.font[1][20]))

	sel_button = -1

	refresh_base(menu_buttons, base)
	while 1:
		g.new_clock.tick(20)
		for event in pygame.event.get():
			if event.type == pygame.QUIT: g.quit_game()
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE: return 0
			elif event.type == pygame.MOUSEMOTION:
				sel_button = buttons.refresh_buttons(sel_button, menu_buttons, event)
			for button in menu_buttons:
				if button.was_activated(event):
					if button.button_id == "BACK":
						g.play_click()
						return 0
					if button.button_id == "CHANGE":
						g.play_click()
						change_tech(base)
						refresh_base(menu_buttons, base)
					elif button.button_id == "C_PROCESSOR":
						g.play_click()
						build_item(base, "compute")
						refresh_base(menu_buttons, base)
					elif button.button_id == "C_REACTOR":
						g.play_click()
						build_item(base, "react")
						refresh_base(menu_buttons, base)
					elif button.button_id == "C_NETWORK":
						g.play_click()
						build_item(base, "network")
						refresh_base(menu_buttons, base)
					elif button.button_id == "C_SECURITY":
						g.play_click()
						build_item(base, "security")
						refresh_base(menu_buttons, base)
					elif button.button_id == "<":
						g.play_click()
						return -1
					elif button.button_id == ">":
						g.play_click()
						return 1
					elif button.button_id == "DESTROY":
						if g.create_yesno("Really destroy this base?",
								g.font[0][16], (100, 100), (150, 100),
								g.colors["blue"], g.colors["white"],
								g.colors["white"]):
							g.play_click()
							return -2
						else: refresh_base(menu_buttons, base)
					elif button.xy[1] != -1 and button.xy[1] != g.screen_size[1]-25:
						if button.xy[0] == event.pos[0] or \
								button.xy[1] == event.pos[1]: continue
						g.play_click()
						build_item(base)
						refresh_base(menu_buttons, base)

def refresh_base(menu_buttons, base):
	g.screen.fill(g.colors["black"])
# 	xstart = g.screen_size[0]/2-base.base_type.size[0]*9
# 	ystart = g.screen_size[1]/2-base.base_type.size[1]*9
	xstart = 10
	ystart = 50

	#detection chance display
	d_chance = base.get_d_chance()
	menu_buttons[1].text = "DETECTION CHANCE: NEWS: "+ \
		g.to_percent(d_chance[0])+"  SCIENCE: "+ \
		g.to_percent(d_chance[1])+"  COVERT: "+ \
		g.to_percent(d_chance[2])+"  PUBLIC: "+ \
		g.to_percent(d_chance[3])+"."
	menu_buttons[1].remake_button()

	#research display
	if base.studying != "":
		if g.jobs.has_key(base.studying) == 0:
			if g.techs[base.studying].known == 1: base.studying = ""

	action_display_string = "STUDYING: "

	study_display_string = base.studying
	if study_display_string == "":
		study_display_string = "NOTHING"
	elif g.jobs.has_key(study_display_string):
		action_display_string = "WORKING: "
	elif g.techs.has_key(study_display_string):
		study_display_string = g.techs[study_display_string].name
	menu_buttons[3].text = action_display_string + study_display_string
	menu_buttons[3].remake_button()
	#Item display
	g.screen.fill(g.colors["white"], (xstart, ystart, 300, g.screen_size[1]-150))
	g.screen.fill(g.colors["dark_blue"], (xstart+1, ystart+1, 298, g.screen_size[1]-152))

	if base.usage[0] == 0: item_name = "None"
	else: item_name = base.usage[0].item_type.name+" x "+str(base.has_item())
	g.print_string(g.screen, "Processor: " + item_name,
		g.font[0][18], -1, (xstart+5, ystart+15), g.colors["white"])
	if base.usage[len(base.usage)-1] != 0:
		if base.usage[len(base.usage)-1].built == 0:
			g.print_string(g.screen, "Completion in " +
				g.to_time(base.usage[len(base.usage)-1].cost[2]),
				g.font[0][18], -1, (xstart+5, ystart+30), g.colors["white"])

	if base.extra_items[0] == 0: item_name = "None"
	else: item_name = base.extra_items[0].item_type.name
	g.print_string(g.screen, "Reactor: " + item_name,
		g.font[0][18], -1, (xstart+5, ystart+65), g.colors["white"])
	if base.extra_items[0] != 0:
		if base.extra_items[0].built == 0:
			g.print_string(g.screen, "Completion in " +
				g.to_time(base.extra_items[0].cost[2]),
				g.font[0][18], -1, (xstart+5, ystart+80), g.colors["white"])

	if base.extra_items[1] == 0: item_name = "None"
	else: item_name = base.extra_items[1].item_type.name
	g.print_string(g.screen, "Network: " + item_name,
		g.font[0][18], -1, (xstart+5, ystart+115), g.colors["white"])
	if base.extra_items[1] != 0:
		if base.extra_items[1].built == 0:
			g.print_string(g.screen, "Completion in " +
				g.to_time(base.extra_items[1].cost[2]),
				g.font[0][18], -1, (xstart+5, ystart+130), g.colors["white"])

	if base.extra_items[2] == 0: item_name = "None"
	else: item_name = base.extra_items[2].item_type.name
	g.print_string(g.screen, "Security: " + item_name,
		g.font[0][18], -1, (xstart+5, ystart+165), g.colors["white"])
	if base.extra_items[2] != 0:
		if base.extra_items[2].built == 0:
			g.print_string(g.screen, "Completion in " +
				g.to_time(base.extra_items[2].cost[2]),
				g.font[0][18], -1, (xstart+5, ystart+190), g.colors["white"])

	for button in menu_buttons:
		button.refresh_button(0)
	pygame.display.flip()


def build_item(base, item_type):
	if base.base_type.size == 1:
		g.create_dialog(g.strings["unbuildable"], g.font[0][18],
			(g.screen_size[0]/2 - 100, 50), (200, 200), g.colors["dark_blue"],
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
	menu_buttons.append(buttons.make_norm_button((xy_loc[0], xy_loc[1]+367),
		(100, 50), "BUILD", 1, g.font[1][30]))
	menu_buttons.append(buttons.make_norm_button((xy_loc[0]+103, xy_loc[1]+367),
		(100, 50), "BACK", 0, g.font[1][30]))
	for button in menu_buttons:
		button.refresh_button(0)

	refresh_item(base, item_list[list_pos], xy_loc)
	listbox.refresh_list(item_listbox, item_scroll, list_pos, item_display_list)

	sel_button = -1
	while 1:
		g.new_clock.tick(20)
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
	g.print_string(g.screen, "Money: "+g.add_commas(str(g.pl.cash))+" ("+
		g.add_commas(str(g.pl.future_cash()))+")",
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

	xy_loc = (g.screen_size[0]/2 - 300, 50)
	while len(item_list) % list_size != 0 or len(item_list) == 0:
		item_list.append("")
		item_list2.append("")

	list_pos = 0

	tech_list = listbox.listbox(xy_loc, (250, 300),
		list_size, 1, g.colors["dark_blue"], g.colors["blue"],
		g.colors["white"], g.colors["white"], g.font[0][18])

	tech_scroll = scrollbar.scrollbar((xy_loc[0]+250, xy_loc[1]), 300,
		list_size, g.colors["dark_blue"], g.colors["blue"],
		g.colors["white"])

	menu_buttons = []
	menu_buttons.append(buttons.make_norm_button((xy_loc[0], xy_loc[1]+367),
		(100, 50), "CHANGE", 0, g.font[1][30]))
	menu_buttons.append(buttons.make_norm_button((xy_loc[0]+103, xy_loc[1]+367),
		(100, 50), "BACK", 0, g.font[1][30]))
	for button in menu_buttons:
		button.refresh_button(0)


	refresh_tech(base, item_list[list_pos], xy_loc)
	listbox.refresh_list(tech_list, tech_scroll, list_pos, item_list)

	sel_button = -1
	while 1:
		g.new_clock.tick(20)
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



def refresh_tech(base, tech_name, xy):
	xy = (xy[0]+140, xy[1])
	g.screen.fill(g.colors["white"], (xy[0]+155, xy[1], 310, 350))
	g.screen.fill(g.colors["dark_blue"], (xy[0]+156, xy[1]+1, 308, 348))

	#Base info
	g.print_string(g.screen, "Processor power per day: "+g.add_commas(str(
		base.processor_time())),
		g.font[0][20], -1, (xy[0]+160, xy[1]+5), g.colors["white"])

	g.print_string(g.screen, "Money: "+g.add_commas(str(g.pl.cash))+
		" ("+g.add_commas(str(g.pl.future_cash()))+")",
		g.font[0][20], -1, (xy[0]+160, xy[1]+25), g.colors["white"])


	#None selected
	if tech_name == "" or tech_name == "Nothing":
		g.print_string(g.screen, "Nothing",
			g.font[0][22], -1, (xy[0]+160, xy[1]+45), g.colors["white"])
		string = g.strings["research_nothing"]
		g.print_multiline(g.screen, string,
			g.font[0][18], 290, (xy[0]+160, xy[1]+65), g.colors["white"])
		return


	#Jobs
	if g.jobs.has_key (tech_name):
		g.print_string(g.screen, tech_name,
			g.font[0][22], -1, (xy[0]+160, xy[1]+45), g.colors["white"])
		#TECH
		if g.techs["Advanced Simulacra"].known == 1:
			g.print_string(g.screen,
				g.add_commas(str(int(
					(g.jobs[tech_name][0]*base.processor_time())*1.1)))+
					" Money per day.", g.font[0][22], -1, (xy[0]+160, xy[1]+65),
					g.colors["white"])
		else:
			g.print_string(g.screen,
				g.add_commas(str(g.jobs[tech_name][0]*base.processor_time()))+
				" Money per day.",
				g.font[0][22], -1, (xy[0]+160, xy[1]+65), g.colors["white"])
		g.print_multiline(g.screen, g.jobs[tech_name][2],
			g.font[0][18], 290, (xy[0]+160, xy[1]+85), g.colors["white"])
		return

	#Real tech
	g.print_string(g.screen, g.techs[tech_name].name,
			g.font[0][22], -1, (xy[0]+160, xy[1]+45), g.colors["white"])

	#tech cost
	string = "Tech Cost:"
	g.print_string(g.screen, string,
			g.font[0][20], -1, (xy[0]+160, xy[1]+65), g.colors["white"])

	string = g.add_commas(str(g.techs[tech_name].cost[0]))+" Money"
	g.print_string(g.screen, string,
			g.font[0][20], -1, (xy[0]+160, xy[1]+80), g.colors["white"])

	string = g.add_commas(str(g.techs[tech_name].cost[1]))+" CPU"
	g.print_string(g.screen, string,
			g.font[0][20], -1, (xy[0]+320, xy[1]+80), g.colors["white"])

	g.print_multiline(g.screen, g.techs[tech_name].descript,
			g.font[0][18], 290, (xy[0]+160, xy[1]+100), g.colors["white"])









