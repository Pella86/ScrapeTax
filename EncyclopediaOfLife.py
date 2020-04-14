# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 10:30:51 2020

@author: Media Markt
"""

import request_handler
import json

import Taxa

eol_api = "https://eol.org/api/search/1.0.json"
eol_test_folder ="./Data/EOL_test/"

params = {}
params["q"] = "mycetophilidae"
# params["filter_by_hierarchy_entry_id"] = "any hierarchy id"

# params["page"] = 1
# params["exact"] = False

# params["filter_by_taxon_concept_id"] = "any taxon_id"

# params["filter_by_string"] = "???"
# params["cache_ttl"] = "n seconds in cache"

eol_main = "https://eol.org"


req = request_handler.Request(eol_api, eol_test_folder + "eol_test.pickle", params)
req.load()

json_data = req.response.json()

print(json.dumps(json_data, indent=2))


result_link  = json_data["results"][0]["link"]
result_title = json_data["results"][0]["title"]

print(result_title)
print(result_link)


myceto_page_eol = result_link + "/names"


# req = request_handler.Request(myceto_page_eol, eol_test_folder + "myceto_home_webpage.pickle")
# req.load()


s = request_handler.get_soup(myceto_page_eol, eol_test_folder + "myceto_home_webpage.pickle")

samples = s.select("body > div.l-basic-main > div.l-content > div > div.ui.segments > div:nth-child(1)")

print(len(samples))

print(samples[0])

divs = samples[0].find_all("div")

names = divs[0].find_all("a")


genus_list = []
collect_genus = False

for name in names:
    print("-"*79)
    print(name.text)
    
    if collect_genus == True:
        
        if name.text[::-1][0:4] == "idae"[::-1]:
            collect_genus = False
        else: 
            print("collecting...")
            genus_list.append(Taxa.Taxa(name.text, None, eol_main + name.get("href"), None))
        
    
    if name.text == "Mycetophilidae":
        print("name found")
        collect_genus = True
    
    # how do I get the taxonomic rank?
    # keep searching until the family name is found
    # then collect the names till you find a name with -iae as ending

species_list = []
for taxa in genus_list:
    
    #open the website, look for author and specie list

    # open the website
    s = request_handler.get_soup(taxa.link, eol_test_folder + taxa.name + ".pickle")
    
    # samples = s.select("body > div.l-basic-main > div.l-content > div")
    # print(samples)
    
    div = s.find("div", {"class": "page-children"})
    
    links = div.find_all("a")
    
    for link in links:
        print("-"*79)
        
        parts = link.text.split(" ")
        
        if len(parts) < 3:
            print(f"Name is not rightfully formatted: {link.text}")
            continue
            

        specie_name = parts[0] + " " + parts[1]
        author_name = "".join(p + " " for p in parts[2 : ])[:-1]
        
        specie_link = eol_main + link.get("href")
        
        print(specie_name)
        print(author_name)
        
        specie = Taxa.Taxa(specie_name, author_name,  specie_link, taxa)
        species_list.append(specie)



for taxa in species_list:
    print(taxa)


# create a function for the authority file independent from NBN Atlas
# craete a function for EoL that returns the dict
    
    



