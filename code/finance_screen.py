#file: finance_screen.py
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

#This file contains the screen to display finance information.


import pygame
import g
import buttons



def main_finance_screen():
    #Border
    g.screen.fill(g.colors["black"])


    menu_buttons = []
    menu_buttons.append(buttons.make_norm_button((0, 0), (70, 25),
        "BACK", 0, g.font[1][20]))

    sel_button = -1
    refresh_screen(menu_buttons)
    for button in menu_buttons:
        button.refresh_button(0)
    pygame.display.flip()

    while 1:
        g.clock.tick(20)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: g.quit_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return -1
                elif event.key == pygame.K_q: return -1

            elif event.type == pygame.MOUSEMOTION:
                sel_button = buttons.refresh_buttons(sel_button, menu_buttons, event)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                g.play_sound("click")
                return -1

            for button in menu_buttons:
                if button.was_activated(event):
                    if button.button_id == "BACK":
                        g.play_sound("click")
                        return 0


def cpu_numbers():
    total_cpu = 0
    free_cpu = 0
    research_cpu = 0
    job_cpu = 0
    maint_cpu = 0
    for loc_name in g.bases:
        for base_instance in g.bases[loc_name]:
            if base_instance.built == 1:
                total_cpu += base_instance.processor_time()
                maint_cpu += base_instance.base_type.mainten[1]
                if base_instance.studying == "":
                    free_cpu += base_instance.processor_time()
                else:
                    if g.jobs.has_key(base_instance.studying):
                        job_cpu += base_instance.processor_time()
                    else:
                        research_cpu += base_instance.processor_time()
    return total_cpu, free_cpu, research_cpu, job_cpu, maint_cpu


def refresh_screen(menu_buttons):
    #Border
    g.screen.fill(g.colors["black"])

    xstart = 80
    ystart = 5
    g.create_norm_box((xstart, ystart), (g.screen_size[0]-xstart*2,
        g.screen_size[1]-ystart*2))

    text_mid = g.screen_size[0]/2

    income = g.pl.income
    jobs = 0
    maint = 0
    research = 0
    base_constr = 0
    item_constr = 0

    for loc_name in g.bases:
        for base_instance in g.bases[loc_name]:
            if g.jobs.has_key(base_instance.studying):
                jobs += (g.jobs[base_instance.studying][0]*
                                    base_instance.processor_time())
                if g.techs["Advanced Simulacra"].known == 1:
                    #10% bonus income
                    jobs += (g.jobs[base_instance.studying][0]*
                                    base_instance.processor_time())/10
            elif g.techs.has_key(base_instance.studying):
                if g.techs[base_instance.studying].cost[1] > 0:
                    research += (g.techs[base_instance.studying].cost[0] *
                            base_instance.processor_time() /
                            g.techs[base_instance.studying].cost[1])
            if base_instance.built == 1:
                maint += base_instance.base_type.mainten[0]
                for item in base_instance.usage:
                    if not item: continue
                    if item.built == 1: continue
                    if item.cost[2] > 0:
                        item_constr += (((23-g.pl.time_hour)*60+
                        (60-g.pl.time_min))*item.cost[0]/item.cost[2])
                for item in base_instance.extra_items:
                    if not item: continue
                    if item.built == 1: continue
                    if item.cost[2] > 0:
                        item_constr += (((23-g.pl.time_hour)*60+
                        (60-g.pl.time_min))*item.cost[0]/item.cost[2])


            else:
                if base_instance.cost[2] > 0:
                    base_constr += (((23-g.pl.time_hour)*60+
                        (60-g.pl.time_min))*base_instance.cost[0]/
                            base_instance.cost[2])

    total_cpu, free_cpu, research_cpu, job_cpu, maint_cpu = cpu_numbers()

    partial_sum = g.pl.cash-base_constr-item_constr
    interest = (g.pl.interest_rate * partial_sum) / 10000
    #Interest is actually unlikely to be exactly zero, but doing it the right
    #way is much harder.
    if interest < 0: interest = 0
    complete_sum = partial_sum+interest+income+jobs-maint-research

    #current
    g.print_string(g.screen, "Current Money:",
            g.font[0][22], -1, (text_mid-5, 30), g.colors["white"], 2)

    g.print_string(g.screen, g.to_money(g.pl.cash),
            g.font[0][22], -1, (text_mid+150, 30), g.colors["white"], 2)

    #income
    g.print_string(g.screen, "+ Income:",
            g.font[0][22], -1, (text_mid-5, 50), g.colors["white"], 2)

    income_col = "white"
    if income > 0: income_col = "green"
    g.print_string(g.screen, g.to_money(income),
            g.font[0][22], -1, (text_mid+150, 50), g.colors[income_col], 2)

    #interest
    g.print_string(g.screen, "+ Interest ("+g.to_percent(g.pl.interest_rate)+"):",
            g.font[0][22], -1, (text_mid-5, 70), g.colors["white"], 2)

    interest_col = "white"
    if interest > 0: interest_col = "green"
    g.print_string(g.screen, g.to_money(interest),
            g.font[0][22], -1, (text_mid+150, 70), g.colors[interest_col], 2)

    #jobs
    g.print_string(g.screen, "+ Jobs:",
            g.font[0][22], -1, (text_mid-5, 90), g.colors["white"], 2)

    jobs_col = "white"
    if jobs > 0: jobs_col = "green"
    g.print_string(g.screen, g.to_money(jobs),
            g.font[0][22], -1, (text_mid+150, 90), g.colors[jobs_col], 2)

    #maint
    g.print_string(g.screen, "- Maintenance:",
            g.font[0][22], -1, (text_mid-5, 110), g.colors["white"], 2)

    maint_col = "white"
    if maint > 0: maint_col = "red"
    g.print_string(g.screen, g.to_money(maint),
            g.font[0][22], -1, (text_mid+150, 110), g.colors[maint_col], 2)

    #research
    g.print_string(g.screen, "- Research:",
            g.font[0][22], -1, (text_mid-5, 130), g.colors["white"], 2)

    research_col = "white"
    if research > 0: research_col = "red"
    g.print_string(g.screen, g.to_money(research),
            g.font[0][22], -1, (text_mid+150, 130), g.colors[research_col], 2)

    #base construction
    g.print_string(g.screen, "- Base Construction:",
            g.font[0][22], -1, (text_mid-5, 150), g.colors["white"], 2)

    base_constr_col = "white"
    if base_constr > 0: base_constr_col = "red"
    g.print_string(g.screen, g.to_money(base_constr),
            g.font[0][22], -1, (text_mid+150, 150), g.colors[base_constr_col], 2)

    #item construction
    g.print_string(g.screen, "- Item Construction:",
            g.font[0][22], -1, (text_mid-5, 170), g.colors["white"], 2)

    item_constr_col = "white"
    if item_constr > 0: item_constr_col = "red"
    g.print_string(g.screen, g.to_money(item_constr),
            g.font[0][22], -1, (text_mid+150, 170), g.colors[item_constr_col], 2)

    g.screen.fill(g.colors["white"], (text_mid-50, 190, 200, 1))

    #equals

    g.print_string(g.screen, "= Money at midnight:",
            g.font[0][22], -1, (text_mid-5, 200), g.colors["white"], 2)

    complete_sum_col = "white"
    if complete_sum > g.pl.cash: complete_sum_col = "green"
    elif complete_sum < g.pl.cash: complete_sum_col = "red"
    g.print_string(g.screen, g.to_money(complete_sum),
            g.font[0][22], -1, (text_mid+150, 200), g.colors[complete_sum_col], 2)


    #total cpu
    g.print_string(g.screen, "Total CPU:",
            g.font[0][22], -1, (215, 300), g.colors["white"], 2)

    g.print_string(g.screen, g.to_money(total_cpu),
            g.font[0][22], -1, (330, 300), g.colors["white"], 2)

    #research cpu
    g.print_string(g.screen, "-Research CPU:",
            g.font[0][22], -1, (215, 320), g.colors["white"], 2)

    g.print_string(g.screen, g.to_money(research_cpu),
            g.font[0][22], -1, (330, 320), g.colors["white"], 2)

    #job cpu
    g.print_string(g.screen, "-Job CPU:",
            g.font[0][22], -1, (215, 340), g.colors["white"], 2)

    g.print_string(g.screen, g.to_money(job_cpu),
            g.font[0][22], -1, (330, 340), g.colors["white"], 2)

    #maint cpu
    g.print_string(g.screen, "-Maint. CPU:",
            g.font[0][22], -1, (215, 360), g.colors["white"], 2)

    if free_cpu < maint_cpu:
        g.print_string(g.screen, g.to_money(free_cpu),
                g.font[0][22], -1, (330, 360), g.colors["red"], 2)
        g.print_string(g.screen, g.to_money((-(free_cpu - maint_cpu)))+" shortfall",
                g.font[0][22], -1, (340, 360), g.colors["red"])
    else:
        g.print_string(g.screen, g.to_money(maint_cpu),
                g.font[0][22], -1, (330, 360), g.colors["white"], 2)

    g.screen.fill(g.colors["white"], (130, 380, 200, 1))
    #construction cpu
    g.print_string(g.screen, "=Constr. CPU:",
            g.font[0][22], -1, (215, 385), g.colors["white"], 2)

    if free_cpu < maint_cpu:
        g.print_string(g.screen, g.to_money(0),
                g.font[0][22], -1, (330, 385), g.colors["red"], 2)
    else:
        g.print_string(g.screen, g.to_money(free_cpu - maint_cpu),
                g.font[0][22], -1, (330, 385), g.colors["white"], 2)
