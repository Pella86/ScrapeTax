# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 11:33:16 2020

@author: Media Markt
"""


import request_handler
import os

chrys_folder = "./Data/Chrysididae/Chrysis_net"
url = "https://chrysis.net/database/chr_checklist_en.php"

s = request_handler.get_soup(url, os.path.join(chrys_folder, "species_list_webpage.pickle"))

print(len(s.find_all("li")))

for li in s.find_all("li"):
    
    ref = li.find_all("a")
        
    if len(ref) == 2:
        name = ref[1]
    if len(ref) == 1:
        name = ref[0]     
    else:
        continue
    
    
    name_parts = name.text.split(" ")
    
    if len(name_parts) > 3 and name.text.find(",") != -1:
        genus = name_parts[0]
        specie = name_parts[1]
        
        
        author = "".join(part + " " for part in name_parts[2:])
        author = author[:-1]
        author = author.replace("[E]", "")
        
        print(genus, specie, author)
    else: 
        continue
    
    
# add the subfamilies by scraping the other webpage
# add the possibility to create an authority file