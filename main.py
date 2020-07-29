#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 09:21:27 2020

@author: maurop
"""
# =============================================================================
# Imports
# =============================================================================

import os

import GenerateTaxaListGBIF
import GenerateFiles
import LogFiles
import FileInfo
import RememberPaths

# =============================================================================
# Logging
# =============================================================================

logger = LogFiles.Logger(__name__)

# =============================================================================
# User Input class 
# =============================================================================
            
class UserInput:

    def __init__(self):
        self.title = None
        self.input_sentence = None
        self.default = None
        self.comma_values = False
        
        self.user_input = None
    
    def get_user_input(self):
        logger.console_log("-" * 79)
        logger.console_log(self.title)
        
        if self.default:
            logger.console_log("Default:" + str(self.default))
        
        choice = input(self.input_sentence + " >")
        
        if choice == "":
            choice = self.default
        
        self.user_input = choice  
        
    def parse_comma_separated(self):
        if self.user_input:
            parts = self.user_input.split(",")
            val = [v.strip() for v in parts]
            
            self.user_input = val
    
    def get_input(self):
        
        self.get_user_input()
        
        if self.comma_values:
            self.parse_comma_separated()
        
        logger.console_log("Input:" + str(self.user_input))
        
        return self.user_input
    

import tkinter    

from tkinter import Frame, Label, Entry, Button, filedialog, Checkbutton, StringVar, IntVar, LabelFrame, Text



class LabelEntry:
    
    def __init__(self, root_frame, text, uid):
        
        self.pFrame = Frame(root_frame)
        
        label = Label(self.pFrame, text=text)
        label.grid(row=0, column=0)
        
        
        self.entry = Entry(self.pFrame)
        self.entry.grid(row=0, column=1)
        
        self.filename = "./settings/" + uid + ".txt"

        if os.path.isfile(self.filename):
            self.read()
        
    def read(self):
        with open(self.filename, "r") as f:
            data = f.read()
        
        data = data.strip()
        self.entry.delete(0, tkinter.END)
        self.entry.insert(0, data)
    
    def write(self):
        with open(self.filename, "w") as f:
            f.write(self.entry.get())      
        
    def get(self):
        self.write()
        
        return self.entry.get()
    
    def get_csv(self):
        self.write()
        
        v = self.entry.get().split(",")
        
        print("strip", v)
        
        if v[0]:
            v = map(lambda s : s.strip(), v)
            return list(v)
        
        else:
            v = []
            return v
        

class SelectFolder:
    
    def __init__(self, root_frame):
        self.pFrame = Frame(root_frame)
        
        select_button = Button(self.pFrame, text="Select a folder", command=lambda : self.select())
        select_button.grid(row=0, column=0)
        
        self.selected_directory = RememberPaths.RememberPath("seldir", "/")
        
        self.selected_dir_str = StringVar()
        self.selected_dir_str.set(self.selected_directory.get())
        
        lfolder = Label(self.pFrame, textvariable=self.selected_dir_str)
        lfolder.grid(row=1, column=0)
        
        
        
    def get(self):
        return self.selected_directory.get()
    
    def select(self):
        sel_dir = filedialog.askdirectory(title="Select a directory", initialdir=self.selected_directory.get())
        
        if sel_dir:
            self.selected_directory.assign(sel_dir)
            
            self.selected_dir_str.set(self.selected_directory.get())
            
class ActionButton:
    
    def __init__(self, root_frame, text, actions):
        self.actions = actions
        self.text = text
        
        self.pFrame = Frame(root_frame)
        
        self.var = IntVar()
        self.var.set(1 if self.actions.action_choice[self.text] else 0)
        
        cb = Checkbutton(self.pFrame, text=self.text, variable=self.var, command=self.cb)
        cb.grid(row=0, column=0)
        

    
    def cb(self):
        self.actions.action_choice[self.text] = True if self.var.get() == 1 else False
        self.actions.write()
    
    
class Actions:
    
    choice_file = "./settings/choice.txt"
    possible_actions = ["Authority list", "Authority file", "Label table", "Synonym list"]
    
    def __init__(self, root_frame):
        self.pFrame = LabelFrame(root_frame, text="Actions")
        
        
        
        self.action_choice = {}
        for action in self.possible_actions:
            self.action_choice[action] = False
        
        
        if os.path.isfile(self.choice_file):
            self.read()
        
        for action in self.possible_actions:
            
            ab = ActionButton(self.pFrame, action, self)
            ab.pFrame.pack()
            
            if self.action_choice[action]:
                ab.var.set(1)
            else:
                ab.var.set(0)

            
            self.write()
    
    def read(self):
        with open(self.choice_file, "r") as f:
            lines = f.readlines()
            
        for line in lines:
            parts = line.split("=")
            
            choice = True if parts[1].strip() == "1" else False
            self.action_choice[parts[0].strip()] = choice
    
    def write(self):
        with open(self.choice_file, "w") as f:
            for name, choice in self.action_choice.items():
                if choice:
                    f.write(f"{name}=1\n")
                else:
                    f.write(f"{name}=0\n")
class OConsole:
    
    def __init__(self, root_frame, root):
        
        self.pFrame = Frame(root_frame)
        
        self.text = Text(self.pFrame, height=20)
        self.text.pack()
        
        self.root = root
    
    def add_line(self, line):
        self.text.insert(tkinter.END, line + "\n")
        self.text.yview_pickplace("end")
        self.root.update()
        
    
        
class GUI:
    
    def __init__(self):
        
        root = tkinter.Tk()
        
        # family options
        
        fam_frame = LabelFrame(root, text="Family details")
        fam_frame.pack()
        
        self.family_entry = LabelEntry(fam_frame, "Family:", "family")
        self.family_entry.pFrame.pack()
        
        self.ass_family_entry = LabelEntry(fam_frame, "Associated Families:", "associated_family")
        self.ass_family_entry.pFrame.pack()

        self.genera_filter = LabelEntry(fam_frame, "Genera filter:", "genera filter")
        self.genera_filter.pFrame.pack()
        
        # folder options
        
        folder_frame = LabelFrame(root, text="Data Folder")
        folder_frame.pack()
        
        self.select_folder = SelectFolder(folder_frame)
        self.select_folder.pFrame.pack()
        

        # make a selectable actions thingy
        
        self.action_frame = Actions(root)
        self.action_frame.pFrame.pack()
        
        # run button
        
        run_button = Button(root, text="RUN", command=self.run)
        run_button.pack()
        
        # output console
        
        output_console_frame = LabelFrame(text="Output console")
        output_console_frame.pack()
        
        self.oconsole = OConsole(output_console_frame, root)
        self.oconsole.pFrame.pack()
        
        
        root.mainloop()

    def run(self):
        
        # read the family name
        
        family = self.family_entry.get()
        
        print(family)
        
        ass_family = self.ass_family_entry.get_csv()
        
        print(ass_family)
        
        genera = self.genera_filter.get_csv()
        
        print(genera)
        
        base_folder = self.select_folder.get()
        
        print(base_folder)
        
        fi = FileInfo.FileInfo(base_folder, "gbif", family)
        
        # set logging files
        logger.set_run_log_filename(fi.name_only("report_log"))  
        logger.set_gui_log(self.oconsole)
        
        logger.log_short_report("#### Scrape Tax ####")
                                
        # scrape the thing
        taxa_list = GenerateTaxaListGBIF.scrape_gbif(family, ass_family, base_folder, genera)
        
        # do the actions like creating files and stuff
        
        actions = []
        
        for action_name, action_value in self.action_frame.action_choice.items():
            
            if "synonym" in action_name.lower():
                continue
            
            if action_value:
                actions.append(action_name.lower())
        
        print(actions)
        
        GenerateFiles.generate_files(base_folder, "gbif", family, taxa_list, actions)
        
        
        # create synonyms
        if  self.action_frame.action_choice["Synonym list"]:
            synonym_list = GenerateTaxaListGBIF.generate_synonym_list(family, base_folder, taxa_list)  
                
            GenerateFiles.generate_files(base_folder, "gbif", family, synonym_list, ["synonyms file"])           
        

# =============================================================================
# User input main        
# =============================================================================

def prod_main():

    #title    
    print("#### Scrape Tax ####")
    print("Program to gather informations from online databases about species and genuses")
    
   
    
    # get the base folder
    base_folder_input = UserInput()
    base_folder_input.title = "The path to the folder where the file will be saved, the folder must already exist. Use dot (.) to access the current folder"
    base_folder_input.input_sentence = "path"
    base_folder_input.default = "./Data"
    
    base_folder = base_folder_input.get_input()

    # Get the family
    family_name_input = UserInput()
    family_name_input.title = "Input the family name"
    family_name_input.input_sentence = "family"
    family_name_input.default = "Papilionidae"
    
    family_name = family_name_input.get_input()
    
    # Add the option to filter by genus
    genera_input = UserInput()
    genera_input.title = "Give genera names to be filtered comma separated, if the input is an empty list, all the genera will be considered"
    genera_input.input_sentence = "genera"
    genera_input.default = []
    genera_input.comma_values = True
    
    genera_filter = genera_input.get_input()
    
    actions = ["authority list", "authority file", "label table"]
    
    
    fi = FileInfo.FileInfo(base_folder, "gbif", family_name)
    
    # set logging files
    logger.set_run_log_filename(fi.name_only("report_log"))  
    
    logger.log_short_report("#### Scrape Tax ####")
    # add date?
    
    logger.log_short_report("--- User inputs ---")
    logger.log_short_report("Family name: " + family_name)

    logger.log_short_report("Output Folder: " + fi.base_path)
    logger.log_short_report("Genera Filter: " + str(genera_filter))
    logger.log_short_report("Actions: " + str(actions))    
    
    
    taxa_list = GenerateTaxaListGBIF.scrape_gbif(family_name, base_folder, genera_filter)
    
    GenerateFiles.generate_files(base_folder, "gbif", family_name, taxa_list, actions)
    
    
    synonym_list = GenerateTaxaListGBIF.generate_synonym_list(family_name, base_folder, taxa_list)  
        
    GenerateFiles.generate_files(base_folder, "gbif", family_name, synonym_list, ["synonyms file"])        
    
# =============================================================================
# Main function
# =============================================================================
    

    
    

PRODUCTION = True   
CONSOLE = False

if __name__ == "__main__":
    if PRODUCTION:
        if CONSOLE:
            prod_main()
        else:
            GUI()
    else:
        
        family_name = "Noctuidae"
        base_folder = "./Tests/test_main"
        genera_filter = []
        actions = ["authority list", "authority file", "label table"]

        fi = FileInfo.FileInfo(base_folder, "gbif", family_name)
        
        logger.set_run_log_filename(fi.name_only("run_log"))
        
        logger.log_short_report("Family name: " + family_name)

        logger.log_short_report("Output Folder: " + fi.base_path)
        logger.log_short_report("Genera Filter: " + str(genera_filter))
        logger.log_short_report("Actions: " + str(actions))
        
        taxa_list = GenerateTaxaListGBIF.scrape_gbif(family_name, base_folder, genera_filter)
    
        GenerateFiles.generate_files(base_folder, "gbif", family_name, taxa_list, actions)
        
        
        synonym_list = GenerateTaxaListGBIF.generate_synonym_list(family_name, base_folder, taxa_list)  
        
        GenerateFiles.generate_files(base_folder, "gbif", family_name, synonym_list, ["synonyms file"])
    

# =============================================================================
# Chrysidide specific stuff
# =============================================================================
        # family = "Chrysididae"
        # prefix = family.lower()

        # base_folder = "./Data/Chrysididae"
        
        # url = "https://species.nbnatlas.org/species/NBNSYS0000159685"
        
        
        # _, species_list_chr = Chrysis_net.generate_lists(base_folder, prefix)
        # spec_dict = Chrysis_net.generate_specie_dictionary(species_list_chr)
        
        # CreateAuthorityFile.generate_authority_file(spec_dict, base_folder, "chr_" + prefix)
        
        # _, species_list_nbn = NBN_parser.generate_lists(url, base_folder, prefix)
        # _, species_list_eol = EncyclopediaOfLife.generate_lists(family, base_folder, prefix)
        # _, species_list_chr = Chrysis_net.generate_lists(base_folder, prefix)
        # print(len(species_list_nbn), len(species_list_eol), len(species_list_chr))
        
        
        # csv = '"Present in","NBN Atlas","EOL Database","Chrysis.net"\n'
        
        # complete_list = []
        
        # for nbn_specie in species_list_nbn:
        #     complete_list.append(nbn_specie)
            
        # for eol_specie in species_list_eol:
        #     if eol_specie.name in [sp.name for sp in complete_list]:
        #         continue
        #     else:
        #         complete_list.append(eol_specie)
            
        # for chr_specie in species_list_chr:
        #     if chr_specie.name in [sp.name for sp in complete_list]:
        #         continue
        #     else:
        #         complete_list.append(chr_specie)
        # complete_list.sort(key= lambda item : item.name)  
        
        # lines = ""
        # for sp in complete_list:
        #     line = f'"{sp.name}",'
            
        #     if sp.name in [s.name for s in species_list_nbn]:
        #         line += "x,"
        #     else:
        #         line += ","
                    
        #     if sp.name in [s.name for s in species_list_eol]:
        #         line += "x,"
        #     else:
        #         line += ","                    
                    
        #     if sp.name in [s.name for s in species_list_chr]:
        #         line += "x"
        #     else:
        #         line += ""
            
        #     lines += line + "\n"
                
        # csv += lines
                
        # filename = os.path.join(base_folder, "list_compare.csv")
        
        # with open(filename, "wb") as f:
        #     f.write(csv.encode("utf8"))
        
        
