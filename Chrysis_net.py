# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 11:33:16 2020

@author: maurop
"""

# =============================================================================
# Impports
# =============================================================================

import request_handler
import os

import Taxa

# =============================================================================
# To dos
# =============================================================================



# add the subfamilies by scraping the other webpage
# add the possibility to create an authority file

chrys_test_folder = "./Data/Chrysididae/Chrysis_net"
species_check_page_url = "https://chrysis.net/database/chr_checklist_en.php"
family = "Chrysididae"
    

def generate_lists(base_folder, prefix, save_lists = False):
    
    filename = os.path.join(base_folder, prefix + "_species_list_webpage.pickle")
    s = request_handler.get_soup(species_check_page_url, filename)
    
    genus_list = []
    species_list = []
    
    # find all the listed items
    
    print("Gathering species from chrysis.net...")
    
    for li in s.find_all("li"):
        
        # find the links inside the listed items
        ref = li.find_all("a")
        
        # select the right link
        if len(ref) == 2:
            name = ref[1]
        if len(ref) == 1:
            name = ref[0]     
        else:
            continue
        
        # split the name
        name_parts = name.text.split(" ")
        
        # %s %s %s %s, %year this is the right format for an author
        if len(name_parts) > 3 and name.text.find(",") != -1:
            genus = name_parts[0]
            specie = name_parts[1]

            if len(name_parts[2]) > 0:
                 # add the subspecie
                specie += " " + name_parts[2]
                author = "".join(part + " " for part in name_parts[3:])
                
            else:
                author = "".join(part + " " for part in name_parts[2:])

            author = author[:-1]
            author = author.replace("[E]", "")            
            
            species_list.append(Taxa.Taxa(genus + " " + specie, author, None, None))
        else: 
            continue    
    
    return genus_list, species_list

def generate_specie_dictionary(species_list):
    species_dicts = []
    for specie in species_list:
        sdict = {}
        sdict["family"] = family
        
        name_parts = specie.name.split(" ")
        
        
        sdict["genus"] = name_parts[0]
        sdict["species"] = name_parts[1]
        if len(name_parts) == 3:
            sdict["subspecies"] = name_parts[2]
        
        sdict["author"] = specie.author
        species_dicts.append(sdict)
    
    return species_dicts


if __name__ == "__main__":
    
    
    family = "Chrysididae"
    prefix = family.lower()

    base_folder = "./Data/Chrysididae"
    
    url = "https://species.nbnatlas.org/species/NBNSYS0000159685"
    
    glist, slist = generate_lists(base_folder, prefix)
    sd = generate_specie_dictionary(slist)
    for d in sd:
       #print(d.get("subspecies"))
        pass