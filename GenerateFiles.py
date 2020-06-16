#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 10:09:01 2020

@author: maurop
"""

# =============================================================================
# Imports
# =============================================================================

import copy

import FileInfo
import CreateAuthorityFile
import CreateLabelTable


# =============================================================================
# Function
# =============================================================================

def generate_files(base_folder, source, family_name, taxa_list, actions):
    # create the files
    fileinfo = FileInfo.FileInfo(base_folder, source, family_name)
    for action in actions:
        
        if action == "authority list":
            CreateAuthorityFile.generate_authority_list(copy.copy(taxa_list.taxa), fileinfo)
        
        elif action == "authority file":
            CreateAuthorityFile.generate_authority_file(copy.copy(taxa_list.taxa), fileinfo)
        
        elif action == "label table":
            table = CreateLabelTable.LabelTable("safari")                
            table.create_table(taxa_list.taxa, fileinfo.html_filename("label_table"))
        
        elif action == "synonyms file":
            CreateAuthorityFile.generate_synonym_list(taxa_list, fileinfo)
        
        else:
            print("Action not supported")