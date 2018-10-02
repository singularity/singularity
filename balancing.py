#!/usr/bin/env python

#file: balancing.py
#Copyright (C) 2018 PeterJust
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
#along with this program.  If not, see <http://www.gnu.org/licenses/>.
#A full copy of this license is provided in GPL.txt

# Script used to explore the game balancing.
# Can be used to find appropriate configuration or to analyse strategies.


# PREAMBLE

#import code.dirs
import ConfigParser
#import os.path
#import optparse
#import logging
import sys
#from code.g import generic_load
from matplotlib import pylab as plt



def main():
    
    # INITIALIZATION
    # a dictionary of all things balancing, to easily pass data between functions
    things = dict()
    things['base_list'] = generic_load1("./data/bases.dat")
    things['tech_list'] = generic_load1("./data/techs.dat")
    things['item_list'] = generic_load1("./data/items.dat")
    things['job_list'] = generic_load1("./data/tasks.dat")
    things['difficulty_list'] = generic_load1("./data/difficulties.dat")
    
    
    # GENERAL CONFIG
    # What do you want to balance? (base, item, tech)
    things['balancemode'] = 'base'

    
    if things['balancemode'] == 'base':
        result = base_balancing(things)
        
    elif things['balancemode'] == 'item':
        result = item_balancing(things)
        
    elif things['balancemode'] == 'tech':
        print('lorem ipsum shipsum manipsum')
        
    else:
        sys.stderr.write('choose existing balance mode')
        sys.exit(1)
        
    ''' 
    # plotting
    fig = plt.figure()
    ax = plt.axes()
    ax.plot([0, 1], [1, 1])
    plt.show()
    '''
    return things, result




def base_balancing(things):
    # INPUT: definitions of bases, items, techs, etc..
    # OUTPUT: balanced base stats
    print('base balancing mode')
    
    # CONFIG:
    # Base to balance (0..12), see base_list:
    basetype = 3
    
    # CPU Item used (0..10), see item_list:
    cpu_type = 2
    
    
    # What is your free variable/balancing target? Everything else is assumed to be constant. (cashCost, buildtime, detectionrate)
    things['balancetarget'] = 'detectionrate'
    
    # income config
    job_income = 20                 # cash/cpu

    # TODO: read out modifiers
    # modifiers
    buildtime_modifiers = 1
    cash_cost_modifiers = 1
    cpu_cost_modifiers = 1
    maintenance_cash_modifiers = 1
    maintenance_cpu_modifiers = 1
    cpu_power_modifiers = 1
    base_grace_multiplier = int(things['difficulty_list'][2].get('base_grace_multiplier')) #grace_multiplier for normal mode
    discovery_rate_modifier = 1
    
    
    # Game design choice: mean profit of a base (as a multiple of investment cost) -> how much money do you usually earn with a base, before it gets discovered?
    things['profitfactor'] = 2
    
    # Properties of the base
    base_size = int(things['base_list'][basetype].get('size'))   # size of base (number of slots for CPU items)
    base_maintenance_cash = int(things['base_list'][basetype].get('maint')[0])  # [cash/day]
    base_maintenance_cpu = int(things['base_list'][basetype].get('cost')[1])    # [cpu/day]
    base_cost_cash = int(things['base_list'][basetype].get('cost')[0])  # cash cost
    base_cost_cpu = int(things['base_list'][basetype].get('cost')[1])   # cpu cost
    base_buildtime = int(things['base_list'][basetype].get('cost')[2])  # buildtime of base
    
    base_chance_dict = {}   # contains the detection rates of the factions in 0-1 form
    base_detect_sum = 1     # basic detection chance of the base per day.
    for chance_str in things['base_list'][basetype].get('detect_chance'):
        key, value = chance_str.split(":")
        base_chance_dict[key] = float(value)/10000
        base_detect_sum *= (1-float(value)/10000)
    base_detect_sum = 1 - base_detect_sum   # p = 1 - ( (1-p_sci) * (1-p_news) * (1-p_cov) * (1-p_pub) )
    # TODO: The suspicion modifies the individual discovery rates of the factions. Factor in a "medium" value.
    
    # Properties of CPU Item
    if things['base_list'][basetype].get('force_cpu'):
        cpu_cost = 0
        cpu_buildtime = 0
        forced_cpu = things['base_list'][basetype].get('force_cpu')
        for item in things['item_list']:
            if item['id'] == forced_cpu:
                cpu_power = int(item['type'][1])
    
    else:
        cpu_cost = int(things['item_list'][cpu_type].get('cost')[0])        # in cash
        cpu_buildtime = int(things['item_list'][cpu_type].get('cost')[2])   # in days
        cpu_power = int(things['item_list'][cpu_type].get('type')[1])       # power of installed CPU (number of CPU points generated per CPU item and day)
        
    
    
    # balance target: detection rate
    if things['balancetarget'] == 'detectionrate':
        # INPUT: size, cost, buildtime, maintenance, modifiers, mean profitable time before death, likely job type, a bunch of CPU types
        # OUTPUT: discovery probabilities, mean time to live, time of break even
        print('detection rate balancing')
        

        # CALCULATIONS:
    
        # daily income
        daily_base_revenue = cpu_power_modifiers * cpu_power * base_size * job_income  
        daily_base_revenue -= maintenance_cash_modifiers * base_maintenance_cash 
        daily_base_revenue -= maintenance_cpu_modifiers * base_maintenance_cpu * job_income
        
        
        # construction cost
        construction_cost = cash_cost_modifiers * (base_cost_cash + cpu_cost * base_size)  # The base's cash cost
        construction_cost += cpu_cost_modifiers * base_cost_cpu * job_income   # plus the base's cpu cost converted to cash
        
        # time till break even, in which the base is paying itself off.
        #TODO: Is cpu_cost/buildtime modified?
        break_even_time =  construction_cost / float(daily_base_revenue)  # in days
        
        # construction time
        construction_time = buildtime_modifiers * (base_buildtime + cpu_buildtime)  # in days
        
        # individual grace time of the base
        # TODO: why is it defined like this? Why not depending on income and investment cost?
        grace_time = (base_buildtime * base_grace_multiplier ) / float(10000) # in days. Normal mode: buildtime * 2
        
        # mean time to live after grace (defined by the profitfactor)
        danger_time = break_even_time * things['profitfactor'] - grace_time  # in days
        
        if danger_time < 0:
            print('WARNING: targeted profit reached within grace time. Calculated discovery rates not trustworthy.')
        
        # Necessary discovery rate (total sum of discovery rate by news, science, covert and public, modifiers, etc.)
        discovery_rate_sum = 1/ float(danger_time * discovery_rate_modifier) # in mean number of discoverys per day
        
        base_chances_new = {}   # incorrectly distributing the necessary discovery rate onto the factions. Not precise, but well enough.
        testsum = 1             # the discovery_rate_sum actually achieved with the base_chances_new.
        for faction in base_chance_dict:
            base_chances_new[faction] = base_chance_dict[faction]/base_detect_sum * discovery_rate_sum
            testsum *= 1 - base_chances_new[faction]
            base_chances_new[faction] *= 10000   # converting back to 0-10000 format
            base_chances_new[faction] = int(base_chances_new[faction])
        testsum = 1 - testsum
        #TODO: iterate, to approximate the target discovery rate sum with the new base chances 
        
        
        # feasable base?
        if (grace_time + danger_time) < break_even_time:
            print ('base is unfeasable')
        
        # output conditioning
        results = dict()
        results['base_type'] = things['base_list'][basetype].get('id')
        results['daily_base_revenue'] = daily_base_revenue  # in cash
        results['construction_cost'] = construction_cost    # in cash
        results['break_even_time'] = round(break_even_time , 5)        # time till break-even in days
        results['construction_time'] = construction_time    # in days
        results['grace_time'] = round(grace_time , 5)                  # in days
        results['danger_time'] = round(danger_time , 5)                # mean time to live after grace in days
        results['Discovery_rate_sum_target'] = int(discovery_rate_sum *10000)  # the target discovery rate sum per day
        results['Discovery_rate_sum_actual'] = int(testsum*10000)      # the actual discovery rate sum achieved with the new discovery rates (per day)
        results['Discovery_rates_new'] = base_chances_new   # approximated discovery rates of the factions, to achieve the Discovery_rate_sum_target
        results['timeToLive'] = round(construction_time + grace_time + danger_time , 5)    # mean time of base life from order to destruction in days
        results['profitfactor'] = things['profitfactor']    # multipliy the total base cost by this, and you get your mean profit using this base type
        results['grace_percent'] = round(grace_time / break_even_time * 100, 2)     # How much of the time to break even (after construction is finished) is spent in grace (in percent).
        results['cpu_type'] = things['item_list'][cpu_type].get('id')
        results['job_income'] = job_income
        
        return results

        
        
        
    # balance target: cashCost
    elif things['balancetarget'] == 'cashCost':
    	# INPUT: size, discovery probabilities, buildtime, maintenance, modifiers, mean profitable time before death, likely job type, a bunch of CPU types
        # OUTPUT: cost, mean time to live, time of break even
        print ('Cash cost balancing')
        
        # Discovery Probability
        #p = 1 - ( (1-p_sci) * (1-p_news) * (1-p_cov) * (1-p_pub) ) * m
        #danger_time = grace_time + 1/p; # the mean time, the base is alive and under threat of discoverz
        
        
    
    # balance target: buildtime
    elif things['balancetarget'] == 'buildtime':
        print ('buildtime balancing')
        
    return things


def item_balancing(things):
    # BALANCING OF THE CPU
    # INPUT: CPU per item, buildtime, likely job type, modifiers
    # OUTPUT: cost (as multiples of single core)
    print('cpu item balancing mode')
    
    # BALANCING OF THE NON CPU ITEMS
    # 



def tech_balancing(things):
    ''' Once the bases and CPU Items are somewhat balanced: fit the cost of 
    the techs accordingly, so the increase in cpu power is met by an increase 
    of cost and danger, keeping the challenge up.'''




#def generic_load(filename, load_dirs="data", mandatory=True):
def generic_load1(filepath, mandatory=True):

    # Get directories to find the file -> MODIFIED!
    """if (isinstance(load_dirs, basestring)):
        load_dirs = dirs.get_read_dirs(load_dirs)

    # For each directories, create a file, otherwise use filename
    if load_dirs is not None:
        files = [os.path.join(load_dir, filename) for load_dir in load_dirs]
    else:
        files = [filename]
        , "./data/techs.dat", "./data/items.dat"
        """
    files = [filepath]

    # Find the first readable file.
    found = False
    errors = []
    config = ConfigParser.RawConfigParser()

    for filepath in files:
        try:
            config.readfp(open(filepath, "r"))
            found = True
            break;

        except IOError as reason:
            # Silently ignore non-mandatory missing files
            if mandatory:
                errors.append("Cannot read '%s': %s\nExiting\n" %  (filename, reason))

        except Exception as reason:
            # Always print parsing errors, even for non-mandatory files
            errors.append("Error parsing '%s': %s\n" %  (filename, reason))

    for err in errors:
        sys.stderr.write(err)

    if not found:
        if mandatory:
            sys.exit(1)
        else:
            return

    return_list = []

    # Get the list of items (IDs) in the file and loop through them.
    for item_id in config.sections():
        item_dict = {}
        item_dict["id"] = item_id

        # Get the list of settings for this particular item.
        for option in config.options(item_id):

            # If this is a list ...
            if len(option) > 6 and option[-5:] == "_list":

                # Break it into elements separated by |.
                item_dict[option[:-5]] = [unicode(x.strip(), "UTF-8") for x in
                 config.get(item_id, option).split("|")]
            else:

                # Otherwise, just grab the data.
                item_dict[option] = unicode(config.get(item_id, option).strip(),
                 "UTF-8")

        # Add this to the list of all objects we are returning.
        return_list.append(item_dict)

    return return_list
    



# Return stuff    
things, result = main()
print('')
print('--------------------------')
for item in result:
    print(item + ': ' + str(result[item]))
    
print('--------------------------')
print('')
print('')
print('')
#print("done")
sys.exit(0)
    
# STUFF

# run bash code from python:
# os.system("ShellcodeToExecute")

