# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 10:30:51 2020

@author: Media Markt
"""

import request_handler
import json

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
            genus_list.append((name.text, eol_main + name.get("href")))
        
    
    if name.text == "Mycetophilidae":
        print("name found")
        collect_genus = True
    
    # how do I get the taxonomic rank?
    # keep searching until the family name is found
    # then collect the names till you find a name with -iae as ending

print(genus_list)


for name, link in genus_list:
    pass
    #open the website, look for author and specie list



