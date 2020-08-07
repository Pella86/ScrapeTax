#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  7 09:23:22 2020

@author: maurop
"""

# =============================================================================
# Imports
# =============================================================================

import LogFiles
import FileInfo
import GenerateTaxaListGBIF
import GenerateFiles

# =============================================================================
# Logger
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
    
# =============================================================================
# User input main        
# =============================================================================

def console_inputs():

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
    
    # Get associated families
    associated_input = UserInput()
    associated_input.title = "Give additional family that are related to the original family"
    associated_input.input_sentence = "families"
    associated_input.default = []
    associated_input.comma_values = True
    
    associated_families = associated_input.get_input()
    
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
    
    
    taxa_list = GenerateTaxaListGBIF.scrape_gbif(family_name, associated_families, base_folder, genera_filter)
    
    GenerateFiles.generate_files(base_folder, "gbif", family_name, taxa_list, actions)
    
    
    synonym_list = GenerateTaxaListGBIF.generate_synonym_list(family_name, base_folder, taxa_list)  
        
    GenerateFiles.generate_files(base_folder, "gbif", family_name, synonym_list, ["synonyms file"]) 