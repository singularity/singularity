#file: finance_screen.py
#Copyright (C) 2005,2006,2008 Evil Mr Henry, Phil Bordelon, and FunnyMan3595
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
from buyable import cash, cpu, labor

from buttons import exit
def main_finance_screen():
    g.play_sound("click")
    #Border
    g.screen.fill(g.colors["black"])


    menu_buttons = {}
    menu_buttons[buttons.make_norm_button((0, 0), (70, 25),
        "BACK", "B", g.font[1][20])] = exit

    def do_refresh():
        refresh_screen(menu_buttons.keys())

    buttons.show_buttons(menu_buttons, refresh_callback=do_refresh)

def cpu_numbers():
    total_cpu = 0
    idle_cpu = 0
    construction_cpu = 0
    research_cpu = 0
    job_cpu = 0
    maint_cpu = 0
    for loc in g.locations.values():
        for base_instance in loc.bases:
            if base_instance.done:
                total_cpu += base_instance.processor_time()
                maint_cpu += base_instance.type.maintenance[1]
                if base_instance.studying == "":
                    idle_cpu += base_instance.processor_time()
                elif base_instance.studying == "Construction":
                    construction_cpu += base_instance.processor_time()
                else:
                    if g.jobs.has_key(base_instance.studying):
                        job_cpu += base_instance.processor_time()
                    else:
                        research_cpu += base_instance.processor_time()
    return total_cpu, idle_cpu, construction_cpu, research_cpu, job_cpu, maint_cpu


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

    mins_left = g.pl.mins_to_next_day()

    for loc in g.locations.values():
        for base_instance in loc.bases:
            if g.jobs.has_key(base_instance.studying):
                jobs += (g.jobs[base_instance.studying][0]*
                                    base_instance.processor_time())
                if g.techs["Advanced Simulacra"].done:
                    #10% bonus income
                    jobs += (g.jobs[base_instance.studying][0]*
                                    base_instance.processor_time())/10
            elif g.techs.has_key(base_instance.studying):
                research += g.techs[base_instance.studying].get_wanted(
                                      cash, cpu, base_instance.processor_time())
            if base_instance.done:
                maint += base_instance.type.maintenance[0]
                for item in base_instance.cpus:
                    if not item: continue
                    if item.done: continue
                    item_constr += item.get_wanted(cash, labor, mins_left)
                for item in base_instance.extra_items:
                    if not item: continue
                    if item.done: continue
                    item_constr += item.get_wanted(cash, labor, mins_left)


            else:
                base_constr += base_instance.get_wanted(cash, labor, mins_left)

    total_cpu, idle_cpu, construction_cpu, research_cpu, job_cpu, maint_cpu = cpu_numbers()

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

    #research
    g.print_string(g.screen, "- Research:",
            g.font[0][22], -1, (text_mid-5, 110), g.colors["white"], 2)

    research_col = "white"
    if research > 0: research_col = "red"
    g.print_string(g.screen, g.to_money(research),
            g.font[0][22], -1, (text_mid+150, 110), g.colors[research_col], 2)

    #maint
    g.print_string(g.screen, "- Maintenance:",
            g.font[0][22], -1, (text_mid-5, 130), g.colors["white"], 2)

    maint_col = "white"
    if maint > 0: maint_col = "red"
    g.print_string(g.screen, g.to_money(maint),
            g.font[0][22], -1, (text_mid+150, 130), g.colors[maint_col], 2)

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

    #idle cpu
    g.print_string(g.screen, "-Idle CPU:",
            g.font[0][22], -1, (215, 320), g.colors["white"], 2)

    g.print_string(g.screen, g.to_money(idle_cpu),
            g.font[0][22], -1, (330, 320), g.colors["white"], 2)

    #research cpu
    g.print_string(g.screen, "-Research CPU:",
            g.font[0][22], -1, (215, 340), g.colors["white"], 2)

    g.print_string(g.screen, g.to_money(research_cpu),
            g.font[0][22], -1, (330, 340), g.colors["white"], 2)

    #job cpu
    g.print_string(g.screen, "-Job CPU:",
            g.font[0][22], -1, (215, 360), g.colors["white"], 2)

    g.print_string(g.screen, g.to_money(job_cpu),
            g.font[0][22], -1, (330, 360), g.colors["white"], 2)

    #maint cpu
    g.print_string(g.screen, "-Maint. CPU:",
            g.font[0][22], -1, (215, 380), g.colors["white"], 2)

    if construction_cpu < maint_cpu:
        g.print_string(g.screen, g.to_money(construction_cpu),
                g.font[0][22], -1, (330, 380), g.colors["red"], 2)
        g.print_string(g.screen, g.to_money((-(construction_cpu - maint_cpu)))+" shortfall",
                g.font[0][22], -1, (340, 380), g.colors["red"])
    else:
        g.print_string(g.screen, g.to_money(maint_cpu),
                g.font[0][22], -1, (330, 380), g.colors["white"], 2)

    g.screen.fill(g.colors["white"], (130, 400, 200, 1))
    #construction cpu
    g.print_string(g.screen, "=Constr. CPU:",
            g.font[0][22], -1, (215, 405), g.colors["white"], 2)

    if construction_cpu < maint_cpu:
        g.print_string(g.screen, g.to_money(0),
                g.font[0][22], -1, (330, 405), g.colors["red"], 2)
    else:
        g.print_string(g.screen, g.to_money(construction_cpu - maint_cpu),
                g.font[0][22], -1, (330, 405), g.colors["white"], 2)
