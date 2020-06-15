#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 10:11:43 2020

@author: maurop
"""

# =============================================================================
# Imports
# =============================================================================

import FileInfo
import TaxaList

# =============================================================================
# Functions
# =============================================================================

def scrape_taxonomy(family_name, base_folder, sources, genera_filter, actions):
    fileinfo = FileInfo.FileInfo(base_folder, "_".join(sources), family_name)

    taxa_list = TaxaList.generate_taxa_list(base_folder, sources, family_name, genera_filter)
    
    
    taxa_list.clean_noauthor()
    
    return taxa_list
