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
import GUIInterface
import ConsoleInterface

# =============================================================================
# Logging
# =============================================================================

logger = LogFiles.Logger(__name__)

# =============================================================================
# Main function
# =============================================================================
    
PRODUCTION = True   
CONSOLE = False

if __name__ == "__main__":
    # main program interfaces
    if PRODUCTION:
        
        # console version
        if CONSOLE:
            ConsoleInterface.console_inputs()
        
        # GUI version
        else:
            GUIInterface.GUI()
    
    # test cases
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
    


        
