#file: singularity.py
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

#This file is the starting file for the game. Run it to start the game.

import pygame, sys
import g, main_menu, map_screen


pygame.init()
pygame.font.init()

#Handle the program arguments.
set_fullscreen = 0
sys.argv.pop(0)
for argument in sys.argv:
	if argument.lower() == "-fullscreen":
		set_fullscreen = 1
	elif argument.lower() == "-640":
		g.screen_size = (640, 480)
	elif argument.lower() == "-800":
		g.screen_size = (800, 600)
	elif argument.lower() == "-1024":
		g.screen_size = (1024, 768)
	elif argument.lower() == "-1280":
		g.screen_size = (1280, 960)
	elif argument.lower() == "-cheater":
		g.cheater = 1
	elif argument.lower() == "-nosound":
		g.nosound = 1
	else:
		print "Unknown argument of " + argument
		print "Allowed arguments: -fullscreen, -640, -800, -1024, -1280, -nosound"
		sys.exit()


pygame.display.set_caption("Endgame: Singularity")

#set the display.
if set_fullscreen == 1:
	g.screen = pygame.display.set_mode(g.screen_size, pygame.FULLSCREEN)
else:
	g.screen = pygame.display.set_mode(g.screen_size)

#Create the fonts:
for i in range(8, 51):
	g.font[0][i] = pygame.font.Font(None, i)
	g.font[1][i] = pygame.font.Font("../data/acknowtt.ttf", i)

#init data:
g.fill_colors()
g.load_pictures()

g.load_sounds()

#Display the main menu
while 1:
	game_action = main_menu.display_main_menu()

	if game_action == 0: #New
		game_action = map_screen.map_loop()
	if game_action == 1: #Load
		load_action = main_menu.display_load_menu()
		if load_action != -1 and load_action != "":
			load_okay = g.load_game(load_action)
			if load_okay != -1:
				game_action = map_screen.map_loop()
			break
	elif game_action == 2: #Quit
		g.quit_game()


