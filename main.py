#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 09:21:27 2020

@author: maurop
"""
# =============================================================================
# Imports
# =============================================================================

import GenerateTaxaListGBIF
import GenerateFiles
import LogFiles
import FileInfo

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

from tkinter import Frame, Label, Entry, Button, filedialog, Checkbutton

class LabelEntry:
    
    def __init__(self, root_frame, text):
        
        self.pFrame = Frame(root_frame)
        
        label = Label(self.pFrame, text=text)
        label.grid(row=0, column=0)
        
        self.entry = Entry(self.pFrame)
        self.entry.grid(row=0, column=1)

class SelectFolder:
    
    def __init__(self, root_frame):
        self.pFrame = Frame(root_frame)
        
        select_button = Button(self.pFrame, text="Select a folder", command=lambda : self.select())
        select_button.pack()
        
        self.selected_directory = None
    
    def select(self):
        sel_dir = filedialog.askdirectory()
        
        if sel_dir:
            self.selected_directory = sel_dir
            
class ActionBox:
    
    def __init__(self, root_frame, text):
        pass
        
        
class GUI:
    
    def __init__(self):
        
        root = tkinter.Tk()
        
        family_entry = LabelEntry(root, "Family:")
        family_entry.pFrame.pack()
        
        ass_family_entry = LabelEntry(root, "Associated Families:")
        ass_family_entry.pFrame.pack()
        
        select_folder = SelectFolder(root)
        select_folder.pFrame.pack()
        
        genera_filter = LabelEntry(root, "Genera filter:")
        genera_filter.pFrame.pack()
        
        # make a selectable actions thingy
        
        
        
        root.mainloop()


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
        
        
