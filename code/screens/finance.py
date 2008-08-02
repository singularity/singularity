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
    sleeping_cpu = 0
    construction_cpu = 0
    research_cpu = 0
    job_cpu = 0
    maint_cpu = 0
    for base in g.all_bases():
        if base.done:
            total_cpu += base.processor_time()
            maint_cpu += base.maintenance[1]
            if base.studying == "Sleep":
                sleeping_cpu += base.processor_time()
            elif base.studying in ("CPU Pool", ""):
                construction_cpu += base.processor_time()
            else:
                if g.jobs.has_key(base.studying):
                    job_cpu += base.processor_time()
                else:
                    research_cpu += base.processor_time()
    return total_cpu, sleeping_cpu, construction_cpu, research_cpu, job_cpu, maint_cpu


def refresh_screen(menu_buttons):
    #Border
    g.screen.fill(g.colors["black"])

    xstart = 80
    ystart = 5
    g.create_norm_box((xstart, ystart), (g.screen_size[0]-xstart*2,
        g.screen_size[1]-ystart*2))

    text_mid = g.screen_size[0]/2

    income = g.pl.income
    maint = 0
    research = 0
    base_constr = 0
    item_constr = 0

    seconds_left = g.pl.seconds_to_next_day()

    for base in g.all_bases():
        cpu_left = base.processor_time() * seconds_left

        if base.done:
            maint += base.maintenance[0]
            for item in base.cpus:
                if not item: continue
                if item.done: continue
                item_constr += item.get_wanted(cash, cpu, cpu_left)
            for item in base.extra_items:
                if not item: continue
                if item.done: continue
                item_constr += item.get_wanted(cash, cpu, cpu_left)
            if g.techs.has_key(base.studying):
                research += g.techs[base.studying].get_wanted(cash,cpu,cpu_left)


        else:
            base_constr += base.get_wanted(cash, cpu, cpu_left)

    total_cpu, sleeping_cpu, construction_cpu, research_cpu, job_cpu, maint_cpu = cpu_numbers()

    jobs_cash, moldy_leftovers = g.pl.get_job_info(job_cpu * seconds_left)

    partial_sum = g.pl.cash-base_constr-item_constr
    interest = (g.pl.interest_rate * partial_sum) / 10000
    #Interest is actually unlikely to be exactly zero, but doing it the right
    #way is much harder.
    if interest < 0: interest = 0
    complete_sum = partial_sum+interest+income+jobs_cash-maint-research

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
    if jobs_cash > 0: jobs_col = "green"
    g.print_string(g.screen, g.to_money(jobs_cash),
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
            g.font[0][22], -1, (text_mid-5, 300), g.colors["white"], 2)

    g.print_string(g.screen, g.to_money(total_cpu),
            g.font[0][22], -1, (text_mid+150, 300), g.colors["white"], 2)

    #sleeping cpu
    g.print_string(g.screen, "-Sleeping CPU:",
            g.font[0][22], -1, (text_mid-5, 320), g.colors["white"], 2)

    g.print_string(g.screen, g.to_money(sleeping_cpu),
            g.font[0][22], -1, (text_mid+150, 320), g.colors["white"], 2)

    #research cpu
    g.print_string(g.screen, "- Research CPU:",
            g.font[0][22], -1, (text_mid-5, 340), g.colors["white"], 2)

    g.print_string(g.screen, g.to_money(research_cpu),
            g.font[0][22], -1, (text_mid+150, 340), g.colors["white"], 2)

    #job cpu
    g.print_string(g.screen, "- Job CPU:",
            g.font[0][22], -1, (text_mid-5, 360), g.colors["white"], 2)

    g.print_string(g.screen, g.to_money(job_cpu),
            g.font[0][22], -1, (text_mid+150, 360), g.colors["white"], 2)

    #maint cpu
    g.print_string(g.screen, "- Maint. CPU:",
            g.font[0][22], -1, (text_mid-5, 380), g.colors["white"], 2)

    if construction_cpu < maint_cpu:
        g.print_string(g.screen, g.to_money(construction_cpu),
                g.font[0][22], -1, (text_mid+150, 380), g.colors["red"], 2)
        g.print_string(g.screen, g.to_money((-(construction_cpu - maint_cpu)))+" shortfall",
                g.font[0][22], -1, (text_mid+160, 380), g.colors["red"])
    else:
        g.print_string(g.screen, g.to_money(maint_cpu),
                g.font[0][22], -1, (text_mid+150, 380), g.colors["white"], 2)

    g.screen.fill(g.colors["white"], (text_mid-50, 400, 200, 1))
    #construction cpu
    g.print_string(g.screen, "=R. CPU Pool:",
            g.font[0][22], -1, (text_mid-5, 405), g.colors["white"], 2)

    if construction_cpu < maint_cpu:
        g.print_string(g.screen, g.to_money(0),
                g.font[0][22], -1, (text_mid+150, 405), g.colors["red"], 2)
    else:
        g.print_string(g.screen, g.to_money(construction_cpu - maint_cpu),
                g.font[0][22], -1, (text_mid+150, 405), g.colors["white"], 2)
