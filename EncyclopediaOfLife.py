# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 10:30:51 2020

@author: Media Markt
"""

import request_handler
import json
import os

import Taxa

eol_api = "https://eol.org/api/search/1.0.json"
eol_main = "https://eol.org"

eol_test_folder ="./Data/EOL_test/"
family = "Mycetophilidae"

def generate_lists(family_name, base_folder, prefix, save_lists = True):
    
    
    params = {}
    params["q"] = family_name.lower()
    
    # different parameters for the query on eol
    # params["filter_by_hierarchy_entry_id"] = "any hierarchy id"
    # params["page"] = 1
    # params["exact"] = False
    # params["filter_by_taxon_concept_id"] = "any taxon_id"
    # params["filter_by_string"] = "???"
    # params["cache_ttl"] = "n seconds in cache"
    
    print("Downloading infos from the query with parameters:", params)
    
    path = os.path.join(base_folder, prefix + "_eol_query.pickle")
    req = request_handler.Request(eol_api, path, params)
    req.load()

    json_data = req.response.json()
    
    for n, result in enumerate(json_data["results"]):
        print(n, result["title"])

    # select the first result in the query
    result_link  = json_data["results"][0]["link"]
    #result_title = json_data["results"][0]["title"]
    
    family_page = result_link + "/names"


    path = os.path.join(base_folder, prefix + "_eol_webpage.pickle")
    s = request_handler.get_soup(family_page, path)

    # select the section corresponding to the Hierarchical tree
    samples = s.select("body > div.l-basic-main > div.l-content > div > div.ui.segments > div:nth-child(1)")

    # gather the names encapsulated in the divs
    divs = samples[0].find_all("div")

    names = divs[0].find_all("a")

    # create the genus list based on the detection of the next family
    #  family1 (ending -idae) -- start
    #    genus1
    #    genus2
    #  family2 (ending -idae) -- stop
    
    genus_list = []
    collect_genus = False
    
    for name in names:
        
        if collect_genus == True:
            
            # match the family ending (-idae)
            if name.text[::-1][0:4] == "idae"[::-1]:
                collect_genus = False
            else: 
                genus = Taxa.Taxa(name.text,
                                  None, # no author
                                  eol_main + name.get("href"),
                                  None)  # no super taxa
                genus_list.append(genus)
            
        
        if name.text == family_name:
            collect_genus = True
    

    species_list = []
    for taxa in genus_list:
        
        #open the website, look for author and specie list
        
        filename = os.path.join(base_folder, taxa.name + ".pickle")

        s = request_handler.get_soup(taxa.link, filename)
        
        div = s.find("div", {"class": "page-children"})
        
        links = div.find_all("a")
        
        # once found all the links in the section gather the information
        for link in links:
            
            # the html link element contains the species name and authors
            parts = link.text.split(" ")
            
            if len(parts) < 3:
                #print(f"Name is not rightfully formatted: {link.text}")
                continue
                
            # first 2 elements are the binomial nomenclature
            specie_name = parts[0] + " " + parts[1]
            # the rest is the author name
            author_name = "".join(p + " " for p in parts[2 : ])[:-1]
            
            specie_link = eol_main + link.get("href")
            
            specie = Taxa.Taxa(specie_name, author_name,  specie_link, taxa)
            species_list.append(specie)
    
    
    return genus_list, species_list


def generate_specie_dictionary(species_list, family):
    species_dicts = []
    for specie in species_list:
        
        sdict = {}
        sdict["family"] = family
        name_parts = specie.name.split(" ")
        sdict["genus"] = name_parts[0]
        sdict["species"] = name_parts[1]
        sdict["author"] = specie.author
        species_dicts.append(sdict)
    return species_dicts
    
    


# create a function for the authority file independent from NBN Atlas
# craete a function for EoL that returns the dict
    

if __name__ == "__main__":
    family_name = "Formicidae"
    base_folder = "./Data/Formicidae"
    prefix = "formicidae"
    _, species_list = generate_lists(family_name, base_folder, prefix)
    spec_dict = generate_specie_dictionary(species_list, family_name)
    
    for d in spec_dict:
        print(d)
    
    



