# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 10:05:46 2020

@author: Media Markt
"""


import openpyxl


wb = openpyxl.load_workbook("./Data/Chrysididae_xls/Chrysididae Rosa ETH Zurich xlsx.xlsx")

ws_names = wb["Authors, total species"]

genus_col = ws_names["B"][2:]
specie_col = ws_names["c"][2:]
sub_specie_col = ws_names["D"][2:]
author_names_col = ws_names["E"][2:]


tax_dicts = []

for genus, specie, subspecie, author in zip(genus_col, specie_col, sub_specie_col, author_names_col):
    
    if genus.value and specie.value and author.value:
    
        tax_dict = {}
        tax_dict["genus"] = genus.value
        tax_dict["species"] = specie.value
        
        author_start = 2
        if subspecie.value:
            tax_dict["subspecies"] = subspecie.value
            author_start = 3
    
        author_parts = author.value.split(" ")
        
        # remove the species / genus information
        author_parts = author_parts[author_start:]
        author = "".join( part + " " for part in  author_parts)
        tax_dict["author"] = author
        
        tax_dicts.append(tax_dict)


    
    
    
wb_sub = openpyxl.load_workbook("./Data/Chrysididae_xls/Subfamilies - tribes.xlsx")


subfamilies_col = wb_sub.active["A"][2:]
tribes_col = wb_sub.active["B"][2:]
genus_col = wb_sub.active["c"][2:]

for subfam, tribe, genus in zip(subfamilies_col, tribes_col, genus_col):
    
    if genus.value:
        # select the genera and put in the subfamily designation the
        # corresponding subfamily / trinbe if it exists
        for tax_dict in tax_dicts:
            if tax_dict["genus"] == genus.value.split(" ")[0]:
                if subfam.value:
                    tax_dict["subfamily"] = subfam.value
                
                if tribe.value:
                    tax_dict["tribe"] = tribe.value
# sort the list?
tax_dicts.sort(key = lambda item : item["genus"])

import AuthorityFileCreation


AuthorityFileCreation.save_authority_file("./Data/Chrysididae/authority_file_xls.csv", tax_dicts)





