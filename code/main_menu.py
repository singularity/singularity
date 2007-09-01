#file: main_menu.py
#Copyright (C) 2005,2006 Evil Mr Henry and Phil Bordelon
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

from os import path, listdir

import pygame
import g

from pgu import gui
import buttons
import scrollbar
import listbox

mmChoice = -1
# Init PGU
app = gui.App()
app.connect(gui.QUIT, app.quit, None)

class MainMenuGui(gui.Table):
    def __init__(self,**params):
        gui.Table.__init__(self,**params)
        fg = (255,255,255)

        self.tr()
        button = gui.Button("New Game", color=fg)
        self.add(button,0,0)
        button.connect(gui.CLICK, mmgui_new_game, None)

        self.tr()
        button = gui.Button("Load Game", color=fg)
        self.add(button,0,1)
        button.connect(gui.CLICK, mmgui_load_game, None)

        self.tr()
        button = gui.Button("Options", color=fg)
        self.add(button,0,2)
        button.connect(gui.CLICK, mmgui_options, None)

        self.tr()
        button = gui.Button("Quit", color=fg)
        self.add(button,0,3)
        button.connect(gui.CLICK, mmgui_quit, None)

        self.tr()
        button = gui.Button("About", color=fg)
        self.add(button,0,4)
        button.connect(gui.CLICK, mmgui_about, None)


def mmgui_new_game(arg):
    global mmChoice
    mmChoice = 0
    app.quit()
def mmgui_load_game(arg):
    global mmChoice
    mmChoice = 1
    app.quit()
def mmgui_options(arg):
    global mmChoice
    mmChoice = 4
    app.quit()
def mmgui_quit(arg):
    global mmChoice
    mmChoice = 2
    app.quit()
def mmgui_about(arg):
    global mmChoice
    mmChoice = 3
    app.quit()

#Displays the main menu. Returns 0 (new game), 1 (load game), or 2 (quit).
def display_main_menu():
    global mmChoice

    g.screen.fill(g.colors["black"])
    x_loc = g.screen_size[0]/2 - 100

    container = gui.Container(width=g.screen_size[0], height=g.screen_size[1])

    fg = (255,255,255)

    titlefont = pygame.font.Font(g.data_loc+g.font0, 32)
    label = gui.Label("ENDGAME:SINGULARITY", color=(125,0,0), font=titlefont)
    container.add(label,x_loc-100,0)

    button = gui.Button("New Game", color=fg)
    container.add(button,x_loc,120)
    button.connect(gui.CLICK, mmgui_new_game, None)

    button = gui.Button("Load Game", color=fg)
    container.add(button,x_loc,220)
    button.connect(gui.CLICK, mmgui_load_game, None)

    button = gui.Button("Options", color=fg)
    container.add(button,x_loc,320)
    button.connect(gui.CLICK, mmgui_options, None)

    button = gui.Button("Quit", color=fg)
    container.add(button,x_loc,420)
    button.connect(gui.CLICK, mmgui_quit, None)

    button = gui.Button("About", color=fg)
    container.add(button,0,g.screen_size[1]-40)
    button.connect(gui.CLICK, mmgui_about, None)


    #Run the pgu using the container. Kill on exiting this dialog group in the button handlers.
    #Likely this will need to be replaced to keep the keyboard handling.
    app.run(container)

    if mmChoice != -1:
        g.play_click()
        return mmChoice

    pygame.display.flip()

#    sel_button = -1
#    while 1:
#        g.clock.tick(20)
#        for event in pygame.event.get():
#            if event.type == pygame.QUIT: g.quit_game()
#            elif event.type == pygame.KEYDOWN:
#                if event.key == pygame.K_ESCAPE: return 2
#            elif event.type == pygame.MOUSEMOTION:
#                sel_button = buttons.refresh_buttons(sel_button, menu_buttons, event)

def difficulty_select():

    xsize = 75
    ysize = 107
    g.create_norm_box((g.screen_size[0]/2-xsize, g.screen_size[1]/2-ysize),
        (xsize*2, ysize*2+1))

    xstart =g.screen_size[0]/2-xsize+5
    ystart =g.screen_size[1]/2-ysize
    diff_buttons = []
    diff_buttons.append(buttons.make_norm_button((xstart, ystart+5), (140, 30),
        "VERY EASY", 0, g.font[1][24]))
    diff_buttons.append(buttons.make_norm_button((xstart, ystart+40), (140, 30),
        "EASY", 0, g.font[1][24]))
    diff_buttons.append(buttons.make_norm_button((xstart, ystart+75), (140, 30),
        "NORMAL", 0, g.font[1][24]))
    diff_buttons.append(buttons.make_norm_button((xstart, ystart+110), (140, 30),
        "HARD", 0, g.font[1][24]))
    diff_buttons.append(buttons.make_norm_button((xstart, ystart+145), (140, 30),
        "IMPOSSIBLE", 0, g.font[1][24]))
    diff_buttons.append(buttons.make_norm_button((xstart, ystart+180), (140, 30),
        "BACK", 0, g.font[1][24]))
    for button in diff_buttons:
        button.refresh_button(0)
    pygame.display.flip()
    sel_button = -1
    while 1:
        g.clock.tick(20)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: g.quit_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return 0
            elif event.type == pygame.MOUSEMOTION:
                sel_button = buttons.refresh_buttons(sel_button, diff_buttons, event)
            for button in diff_buttons:
                if button.was_activated(event):
                    if button.button_id == "VERY EASY":
                        g.play_click()
                        g.new_game(1)
                        return 1
                    elif button.button_id == "EASY":
                        g.play_click()
                        g.new_game(3)
                        return 1
                    elif button.button_id == "NORMAL":
                        g.play_click()
                        g.new_game(5)
                        return 1
                    elif button.button_id == "HARD":
                        g.play_click()
                        g.new_game(7)
                        return 1
                    elif button.button_id == "IMPOSSIBLE":
                        g.play_click()
                        g.new_game(9)
                        return 1
                    elif button.button_id == "BACK":
                        g.play_click()
                        return 0

def display_load_menu():
    load_list_size = 16
    xy_loc = (g.screen_size[0]/2 - 109, 50)

    save_dir = g.get_save_folder()

    saves_array = []
    temp_saves_array = listdir(save_dir)
    for save_name in temp_saves_array:
        if save_name[0] != "." and save_name != "CVS":
            # If it's a new-style save, trim the .sav bit.
            if len (save_name) > 4 and save_name[-4:] == ".sav":
                save_name = save_name[:-4]
            if save_name not in saves_array:
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
    menu_buttons.append(buttons.make_norm_button((xy_loc[0], xy_loc[1]+367), (100, 50),
        "LOAD", 0, g.font[1][30]))
    menu_buttons.append(buttons.make_norm_button((xy_loc[0]+118, xy_loc[1]+367),
        (100, 50), "BACK", 0, g.font[1][30]))
    for button in menu_buttons:
        button.refresh_button(0)

    listbox.refresh_list(saves_list, saves_scroll, saves_pos, saves_array)

    sel_button = -1
    while 1:
        g.clock.tick(20)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: g.quit_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return -1
                elif event.key == pygame.K_q: return -1
                elif event.key == pygame.K_RETURN:
                    return saves_array[saves_pos]
                else:
                    saves_pos, refresh = saves_list.key_handler(event.key,
                        saves_pos, saves_array)
                    if refresh: listbox.refresh_list(saves_list, saves_scroll,
                                        saves_pos, saves_array)

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

                if event.button == 3:
                    return -1
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

def display_options():
    prev_lang = g.language
    menu_buttons = []
    menu_buttons.append(buttons.make_norm_button((0, 0), (70, 25),
        "BACK", 0, g.font[1][20]))
    menu_buttons.append(buttons.make_norm_button((120,
        0), (170, 35), "SAVE TO DISK", 0, g.font[1][20]))
    menu_buttons.append(buttons.make_norm_button((285, 75), (70, 25),
        "TOGGLE", -1, g.font[1][14], "fullscreen"))
    menu_buttons.append(buttons.make_norm_button((285, 105), (70, 25),
        "TOGGLE", -1, g.font[1][14], "sound"))
    menu_buttons.append(buttons.make_norm_button((285, 135), (70, 25),
        "TOGGLE", -1, g.font[1][14], "grab"))
    menu_buttons.append(buttons.make_norm_button((140, 190), (70, 35),
        "640x480", 0, g.font[1][16], "640"))
    menu_buttons.append(buttons.make_norm_button((220, 190), (70, 35),
        "800x600", 0, g.font[1][16], "800"))
    menu_buttons.append(buttons.make_norm_button((300, 190), (70, 35),
        "1024x768", 0, g.font[1][16], "1024"))
    menu_buttons.append(buttons.make_norm_button((380, 190), (70, 35),
        "1280x1024", 1, g.font[1][16], "1280"))

    load_list_size = 5
    xy_loc = (140, 270)
    lang_array = listdir(g.data_loc)
    for i in range(len(lang_array)-1, -1, -1):
        if lang_array[i][:8] != "strings_":
            lang_array.pop(i)
        else: lang_array[i] = lang_array[i][8:-4]

    while len(lang_array) % load_list_size != 0 or len(lang_array) == 0:
        lang_array.append("")

    global lang_pos
    lang_pos = 0
    for i in range(len(lang_array)):
        if lang_array[i] == g.language:
            lang_pos = i

    lang_list = listbox.listbox(xy_loc, (150, 150),
        load_list_size, 1, g.colors["dark_blue"], g.colors["blue"],
        g.colors["white"], g.colors["white"], g.font[0][20])

    lang_scroll = scrollbar.scrollbar((xy_loc[0]+150, xy_loc[1]), 150,
        load_list_size, g.colors["dark_blue"], g.colors["blue"],
        g.colors["white"])

    sel_button = -1
    refresh_options(menu_buttons)
    for button in menu_buttons:
        button.refresh_button(0)
    listbox.refresh_list(lang_list, lang_scroll, lang_pos, lang_array)
    pygame.display.flip()

    while 1:
        g.clock.tick(20)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: g.quit_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    set_language_properly(prev_lang)
                    return
                elif event.key == pygame.K_q:
                    set_language_properly(prev_lang)
                    return
                else:
                    lang_pos, refresh = lang_list.key_handler(event.key,
                        lang_pos, lang_array)
                    if refresh:
                        listbox.refresh_list(lang_list, lang_scroll,
                                        lang_pos, lang_array)
                        if lang_array[lang_pos] != "":
                            g.language = lang_array[lang_pos]

            elif event.type == pygame.MOUSEMOTION:
                sel_button = buttons.refresh_buttons(sel_button, menu_buttons, event)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    tmp = lang_scroll.is_over(event.pos)
                    if tmp != -1:
                        if tmp == 1:
                            lang_pos -= 1
                            if lang_pos < 0:
                                lang_pos = 0
                        if tmp == 2:
                            lang_pos += 1
                            if lang_pos >= len(lang_array):
                                lang_pos = len(lang_array) - 1
                        if tmp == 3:
                            lang_pos -= load_list_size
                            if lang_pos < 0:
                                lang_pos = 0
                        if tmp == 4:
                            lang_pos += load_list_size
                            if lang_pos >= len(lang_array) - 1:
                                lang_pos = len(lang_array) - 1
                        listbox.refresh_list(lang_list, lang_scroll,
                                            lang_pos, lang_array)
                        if lang_array[lang_pos] != "":
                            g.language = lang_array[lang_pos]

                    tmp = lang_list.is_over(event.pos)
                    if tmp != -1:
                        lang_pos = (lang_pos/load_list_size)*load_list_size \
                                    + tmp
                        listbox.refresh_list(lang_list, lang_scroll,
                                    lang_pos, lang_array)
                        if lang_array[lang_pos] != "":
                            g.language = lang_array[lang_pos]

                if event.button == 3:
                    set_language_properly(prev_lang)
                    return -1
                if event.button == 4:
                    lang_pos -= 1
                    if lang_pos <= 0:
                        lang_pos = 0
                    listbox.refresh_list(lang_list, lang_scroll,
                                        lang_pos, lang_array)
                    if lang_array[lang_pos] != "":
                        g.language = lang_array[lang_pos]
                if event.button == 5:
                    lang_pos += 1
                    if lang_pos >= len(lang_array):
                        lang_pos = len(lang_array)-1
                    listbox.refresh_list(lang_list, lang_scroll,
                                        lang_pos, lang_array)
                    if lang_array[lang_pos] != "":
                        g.language = lang_array[lang_pos]

            for button in menu_buttons:
                if button.was_activated(event):
                    if button.button_id == "BACK":
                        g.play_click()
                        set_language_properly(prev_lang)
                        return 0
                    if button.button_id == "SAVE TO DISK":
                        g.play_click()
                        if lang_pos >= len(lang_array):
                            save_options()
                        else:
                            save_options(lang_array[lang_pos])
                            set_language_properly(prev_lang)
                        return 0
                    elif button.button_id == "fullscreen":
                        if g.fullscreen == 1: g.fullscreen = 0
                        else: g.fullscreen = 1
                        g.play_click()
                        set_res()
                    elif button.button_id == "sound":
                        if g.nosound == 1: g.nosound = 0
                        else: g.nosound = 1
                        g.play_click()
                    elif button.button_id == "grab":
                        g.play_click()
                        pygame.event.set_grab(not pygame.event.get_grab())
                    elif button.button_id == "640":
                        g.play_click()
                        g.screen_size = (640, 480)
                        set_res()
                    elif button.button_id == "800":
                        g.play_click()
                        g.screen_size = (800, 600)
                        set_res()
                    elif button.button_id == "1024":
                        g.play_click()
                        g.screen_size = (1024, 768)
                        set_res()
                    elif button.button_id == "1280":
                        g.play_click()
                        g.screen_size = (1280, 1024)
                        set_res()
                    click_button(menu_buttons, button, False)
                    listbox.refresh_list(lang_list, lang_scroll,
                                lang_pos, lang_array)
                    if lang_array[lang_pos] != "":
                        g.language = lang_array[lang_pos]
            tmp = lang_scroll.adjust_pos(event, lang_pos, lang_array)
            if tmp != lang_pos:
                lang_pos = tmp
                listbox.refresh_list(lang_list, lang_scroll, lang_pos,
                    lang_array)
                if lang_array[lang_pos] != "":
                    g.language = lang_array[lang_pos]

def click_button(menu_buttons, button, flip=True):
    refresh_options(menu_buttons)
    for button2 in menu_buttons:
        button2.refresh_button(0)
    button.refresh_button(1)
    if flip:
        pygame.display.flip()

def set_res():
    #By the way, there is a toggle_fullscreen() function, but the pygame help
    #says it has "limited platform support".
    if g.fullscreen == 1:
        g.screen = pygame.display.set_mode(g.screen_size,
                    pygame.FULLSCREEN)
    else:
        g.screen = pygame.display.set_mode(g.screen_size)



def set_language_properly(prev_lang):
    if g.language == prev_lang: return
    g.load_bases()
    g.load_base_defs(g.language)
    g.load_tech_defs(g.language)
    g.load_item_defs(g.language)
    g.load_string_defs(g.language)

def save_options(lang=""):
    save_dir = g.get_save_folder(True)
    save_loc = path.join(save_dir, "prefs.dat")
    savefile=open(save_loc, 'w')
    savefile.write("fullscreen="+str(g.fullscreen)+"\n")
    savefile.write("nosound="+str(g.nosound)+"\n")
    savefile.write("grab="+str(pygame.event.get_grab())+"\n")
    savefile.write("xres="+str(g.screen_size[0])+"\n")
    savefile.write("yres="+str(g.screen_size[1])+"\n")
    if lang != "":
        savefile.write("lang="+lang+"\n")
    savefile.close()
    g.create_dialog("\\n Options Saved", g.font[0][22],
            (g.screen_size[0]/2-70, 250), (140, 90),
            g.colors["blue"], g.colors["white"], g.colors["white"])

def refresh_options(menu_buttons):
    #Border
    g.screen.fill(g.colors["black"])
    xstart = 120
    ystart = 50
    g.create_norm_box((xstart, ystart), (g.screen_size[0]-xstart*2,
        g.screen_size[1]-ystart*2))

    #fullscreen
    string = "No"
    if g.fullscreen == 1: string = "Yes"
    g.print_string(g.screen, "Fullscreen: "+string,
            g.font[0][22], -1, (xstart+20, ystart+30), g.colors["white"])
    #sound
    string = "Yes"
    if g.nosound == 1: string = "No"
    g.print_string(g.screen, "Sound: "+string,
            g.font[0][22], -1, (xstart+20, ystart+60), g.colors["white"])

    if len(g.sounds) ==0 and g.nosound == 0:
        g.print_string(g.screen, "(Game must be restarted to take effect)",
            g.font[0][22], -1, (xstart+240, ystart+60), g.colors["white"])
    #mouse grab
    string = "No"
    if pygame.event.get_grab(): string = "Yes"
    g.print_string(g.screen, "Mouse grab: "+string,
            g.font[0][22], -1, (xstart+20, ystart+90), g.colors["white"])
    #Resolution
    string = str(g.screen_size[0])+"x"+str(g.screen_size[1])
    g.print_string(g.screen, "Resolution: "+string,
            g.font[0][22], -1, (xstart+20, ystart+120), g.colors["white"])
    #Language
    g.print_string(g.screen, "Language:",
            g.font[0][22], -1, (xstart+20, ystart+200), g.colors["white"])
