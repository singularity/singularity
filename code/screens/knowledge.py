#file: knowledge.py
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

#This file is used to display the knowledge lists.

from code import g
from code.graphics import text, button, dialog, widget, constants, listbox, g as gg


#def display_items(item_type):
    #list_size = 16
    #list = []
    #display_list = []

    #if item_type == "tech":
        #items = [tech for tech in g.techs.values() if tech.available()]
    #elif item_type == "concept":
        #items = [ [item[1][0], item[0]] for item in g.help_strings.items()]
        #items.sort()
    #else:
        #items = [item for item in g.items.values() 
                      #if item.item_type == item_type and item.available()]

    #if item_type != "concept":
        #items = [ [item.name, item.id ] for item in items]
        #items.sort()

    #for name, id in items:
        #list.append(id)
        #display_list.append(name)

    #xy_loc = (g.screen_size[0]/2 - 289, 50)
    #listbox.resize_list(list, list_size)

    #menu_buttons = {}
    #menu_buttons[buttons.make_norm_button((xy_loc[0]+103, xy_loc[1]+367), (100, 50), "BACK", "B", g.font[1][30])] = listbox.exit

    #def do_refresh(item_pos):
        #if item_type == "tech":
            #refresh_tech(list[item_pos], xy_loc)
        #elif item_type == "concept":
            #refresh_concept(list[item_pos], xy_loc)
        #else:
            #refresh_items(list[item_pos], xy_loc)

    #listbox.show_listbox(display_list, menu_buttons, 
                         #list_size=list_size,
                         #loc=xy_loc, box_size=(230, 350), 
                         #pos_callback=do_refresh, return_callback=listbox.exit)
    ##details screen

#def refresh_tech(tech_name, xy):
    #xy = (xy[0]+100, xy[1])
    #g.screen.fill(g.colors["white"], (xy[0]+155, xy[1], 300, 350))
    #g.screen.fill(g.colors["dark_blue"], (xy[0]+156, xy[1]+1, 298, 348))
    #if tech_name == "": 
        #return
    #g.print_string(g.screen, g.techs[tech_name].name,
            #g.font[0][22], -1, (xy[0]+160, xy[1]+5), g.colors["white"])

    ##Building cost
    #if not g.techs[tech_name].done:
        #string = "Research Cost:"
        #g.print_string(g.screen, string,
                #g.font[0][18], -1, (xy[0]+160, xy[1]+30), g.colors["white"])

        #string = g.to_money(g.techs[tech_name].cost_left[0])+" Money"
        #g.print_string(g.screen, string,
                #g.font[0][16], -1, (xy[0]+160, xy[1]+50), g.colors["white"])

        #string = g.to_cpu(g.techs[tech_name].cost_left[1]) + " CPU"
        #g.print_string(g.screen, string,
                #g.font[0][16], -1, (xy[0]+160, xy[1]+70), g.colors["white"])
    #else:
        #g.print_string(g.screen, "Research complete.",
                #g.font[0][22], -1, (xy[0]+160, xy[1]+30), g.colors["white"])

    ##Danger
    #if g.techs[tech_name].danger == 0:
        #string = "Study anywhere."
    #elif g.techs[tech_name].danger == 1:
        #string = "Study underseas or farther."
    #elif g.techs[tech_name].danger == 2:
        #string = "Study off-planet."
    #elif g.techs[tech_name].danger == 3:
        #string = "Study far away from this planet."
    #elif g.techs[tech_name].danger == 4:
        #string = "Do not study in this dimension."
    #g.print_string(g.screen, string,
            #g.font[0][20], -1, (xy[0]+160, xy[1]+90), g.colors["white"])

    #if g.techs[tech_name].done:
        #g.print_multiline(g.screen, g.techs[tech_name].description+" \\n \\n "+
                #g.techs[tech_name].result,
                #g.font[0][18], 290, (xy[0]+160, xy[1]+120), g.colors["white"])
    #else:
        #g.print_multiline(g.screen, g.techs[tech_name].description,
                #g.font[0][18], 290, (xy[0]+160, xy[1]+120), g.colors["white"])

#def refresh_items(item_name, xy):
    #xy = (xy[0]+100, xy[1])
    #g.screen.fill(g.colors["white"], (xy[0]+155, xy[1], 300, 350))
    #g.screen.fill(g.colors["dark_blue"], (xy[0]+156, xy[1]+1, 298, 348))
    #if item_name == "": 
        #return
    #g.print_string(g.screen, g.items[item_name].name,
            #g.font[0][22], -1, (xy[0]+160, xy[1]+5), g.colors["white"])

    ##Building cost
    #string = "Building Cost:"
    #g.print_string(g.screen, string,
            #g.font[0][18], -1, (xy[0]+160, xy[1]+30), g.colors["white"])

    #string = g.to_money(g.items[item_name].cost[0])+" Money"
    #g.print_string(g.screen, string,
            #g.font[0][16], -1, (xy[0]+160, xy[1]+50), g.colors["white"])

    #string = g.to_time(g.items[item_name].cost[2])
    #g.print_string(g.screen, string,
            #g.font[0][16], -1, (xy[0]+160, xy[1]+70), g.colors["white"])

    ##Quality
    #if g.items[item_name].item_type == "compute":
        #string = "CPU per day: "+str(g.items[item_name].item_qual)
    #elif g.items[item_name].item_type == "react":
        #string = "Detection chance reduction: "+g.to_percent(g.items[item_name].item_qual)
    #elif g.items[item_name].item_type == "network":
        #string = "CPU bonus: "+g.to_percent(g.items[item_name].item_qual)
    #elif g.items[item_name].item_type == "security":
        #string = "Detection chance reduction: "+g.to_percent(g.items[item_name].item_qual)
    #g.print_string(g.screen, string,
            #g.font[0][20], -1, (xy[0]+160, xy[1]+90), g.colors["white"])

    #g.print_multiline(g.screen, g.items[item_name].description,
            #g.font[0][18], 290, (xy[0]+160, xy[1]+120), g.colors["white"])

#def refresh_concept(concept_name, xy):
    #xy = (xy[0]+100, xy[1])
    #g.screen.fill(g.colors["white"], (xy[0]+155, xy[1], 300, 350))
    #g.screen.fill(g.colors["dark_blue"], (xy[0]+156, xy[1]+1, 298, 348))
    #if concept_name == "": 
        #return
    #g.print_string(g.screen, g.help_strings[concept_name][0],
            #g.font[0][22], -1, (xy[0]+160, xy[1]+5), g.colors["white"])
    #g.print_multiline(g.screen, g.help_strings[concept_name][1],
            #g.font[0][18], 290, (xy[0]+160, xy[1]+30), g.colors["white"])




class KnowledgeScreen(dialog.Dialog):
    def __init__(self, *args, **kwargs):
        super(KnowledgeScreen, self).__init__(*args, **kwargs)

        self.knowledge_type_list = ("Techs", "Items", "Concepts")
        self.desc_func = self.on_change
        self.cur_knowledge_type = "Techs"
        self.cur_knowledge = None
        self.knowledge_inner_list = ()
        self.knowledge_inner_list_key = ()

        self.knowledge_choice = \
            listbox.UpdateListbox(self, (.17, .18), (.21, .25),
                                  list=self.knowledge_type_list,
                                  update_func=self.set_knowledge_type)

        self.knowledge_inner = \
            listbox.UpdateListbox(self, (.42, .18), (.21, .25),
                                  list=self.knowledge_inner_list,
                                  update_func=self.set_knowledge)

        self.back_button = button.ExitDialogButton(self, (0.17, 0.46), (-.3, -.1),
                                                   anchor=constants.TOP_LEFT,
                                                   text="BACK", hotkey="b")
        self.set_knowledge_type(0)


    def set_inner_list(self, item_type):
        if item_type == "Techs":
            items = [tech for tech in g.techs.values() if tech.available()]
        elif item_type == "Concepts":
            items = [ [item[1][0], item[0]] for item in g.help_strings.items()]
            items.sort()
        else:
            items = [item for item in g.items.values()
                        if item.available()]

        if item_type != "Concepts":
            items = [ [item.name, item.id ] for item in items]
            items.sort()

        return_list1 = []
        return_list2 = []
        for name, id in items:
            return_list1.append(id)
            return_list2.append(name)
        return return_list1, return_list2


    def set_knowledge_type(self, list_pos):
        if getattr(self, "knowledge_choice", None) is None:
            self.knowledge_inner_list, self.knowledge_inner_list_key = \
                        self.set_inner_list(self.cur_knowledge_type)
            return # Not yet initialized.
        prev_know = self.cur_knowledge_type
        if 0 <= list_pos < len(self.knowledge_choice.list):
            self.cur_knowledge_type = self.knowledge_choice.list[list_pos]
        if prev_know != self.cur_knowledge_type:
            self.knowledge_inner.list, self.knowledge_inner_list_key = \
                        self.set_inner_list(self.cur_knowledge_type)

    def set_knowledge(self, list_pos):
        if getattr(self, "knowledge_inner", None) is None:
            return # Not yet initialized.
        prev_know = self.cur_knowledge
        if 0 <= list_pos < len(self.knowledge_inner.list):
            self.cur_knowledge = self.knowledge_choice.list[list_pos]
        if prev_know != self.cur_knowledge:
            print self.cur_knowledge

    def on_change(self, description_pane, base_type):
        if knowledge_type_list is not None:
            base_info = base_type.get_info(self.parent.location)
            text.Text(description_pane, (0, 0), (-1, -1), text=base_info,
                      background_color=gg.colors["dark_blue"],
                      align=constants.LEFT, valign=constants.TOP,
                      borders=constants.ALL)


    def show(self):
        return super(KnowledgeScreen, self).show()


