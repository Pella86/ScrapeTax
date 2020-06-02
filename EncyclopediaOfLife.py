# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 10:30:51 2020

@author: maurop
"""

# =============================================================================
# Imports
# =============================================================================

import request_handler
import re

import Taxa
import ProgressBar

# =============================================================================
# Constants
# =============================================================================

eol_api = "https://eol.org/api/search/1.0.json"
eol_main = "https://eol.org"

eol_test_folder ="./Data/EOL_test/"


# =============================================================================
# Functions
# =============================================================================

def generate_lists(family_name, fileinfo, load_lists = True):
    ''' Function that generates both the genera and species lists'''
    
    print("Generating taxa list from Encyclopedia of Life (EOL)...")
    print("Input name: ", family_name)
    
    # performs a query to the website
    params = {"q":family_name.lower()}
    
    # different parameters for the query on eol
    # params["filter_by_hierarchy_entry_id"] = "any hierarchy id"
    # params["page"] = 1
    # params["exact"] = False
    # params["filter_by_taxon_concept_id"] = "any taxon_id"
    # params["filter_by_string"] = "???"
    # params["cache_ttl"] = "n seconds in cache"
    
    path = fileinfo.pickle_filename("eol_query")
    req = request_handler.Request(eol_api, path, params)
    req.load()

    json_data = req.response.json()
    
    # shows the results
    print("Possible matches: ", len(json_data["results"]))
    for result in json_data["results"]:
        print("    -", result["title"])

    # select the first result in the query
    result_link  = json_data["results"][0]["link"]
    
    # creates the reference link
    family_page = result_link + "/names"
    
    print("Downloading data from:", family_page)

    # soups the link
    path = fileinfo.pickle_filename("eol_webpage")
    s = request_handler.get_soup(family_page, path)
    
    

    # select the section corresponding to the Hierarchical tree
    samples = s.select("body > div.l-basic-main > div.l-content > div > div.ui.segments > div:nth-child(1)")
    

    # gather the names encapsulated in the divs
    divs = samples[0].find_all("div")

    names = divs[0].find_all("a")

    # create the genus list based on the detection of the next family
    #  family1 == family_name -- start
    #    genus1
    #    genus2
    #  family2 (ending -idae) -- stop
    
    genus_list = []
    collect_genus = False
    
    fam_taxa = Taxa.Taxa()
    fam_taxa.family = family_name
    fam_taxa.source = Taxa.Taxa.source_eol
    fam_taxa.rank = Taxa.Taxa.rank_family
    
    for name in names:
        
        if collect_genus == True:
            
            # match the family ending (-idae)
            if name.text[::-1][0:4] == "idae"[::-1]:
                collect_genus = False
            else: 
                genus = Taxa.Taxa()
                genus.copy_taxa(fam_taxa)
                genus.rank = Taxa.Taxa.rank_genus
                genus.genus = name.text
                genus.links.append(eol_main + name.get("href"))
                genus_list.append(genus)
            
        
        if name.text == family_name:
            collect_genus = True
    
    
    pbar = ProgressBar.ProgressBar(len(genus_list))

    species_list = []
    for i, taxa in enumerate(genus_list):
        
        #open the website, look for specie list
        
        filename = fileinfo.pickle_filename(taxa.genus)

        s = request_handler.get_soup(taxa.links[0], filename)
        
        div = s.find("div", {"class": "page-children"})
        
        links = div.find_all("a")
        
        # once found all the links in the section gather the information
        for link in links:
            
            # the html link element contains the species name and authors
            parts = link.text.split(" ")
            
            if len(parts) < 3:
                #print(f"Name is not rightfully formatted: {link.text}")
                continue
            
            n_specie = 1
            
            # this is a sub genus
            if parts[n_specie].startswith("("):
                n_specie = 2
                
            # first 2 elements are the binomial nomenclature
            specie_name = parts[n_specie]
            
            # the rest is the author name
            author_name = "".join(p + " " for p in parts[n_specie + 1 : ])[:-1]
            
            # add the comma before the year
            author_name = re.sub(" (\d\d\d\d)", r", \1", author_name)
            
            specie_link = eol_main + link.get("href")
            
            specie = Taxa.Taxa()
            specie.copy_taxa(taxa)
            specie.rank = Taxa.Taxa.rank_specie
            specie.specie = specie_name
            specie.author = author_name
            specie.links.append(specie_link)
            
            species_list.append(specie)
    
        pbar.draw_bar(i)

        
    print("Genus retrived:", len(genus_list), "Species retrived:", len(species_list))
    return genus_list, species_list


if __name__ == "__main__":
    family_name = "Mycetophilidae"
    base_folder = "./Data/EOL_test"
    
    import FileInfo
    fileinfo = FileInfo.FileInfo(base_folder, "eol", family_name)
        
    genus_list, specie_list = generate_lists(family_name, fileinfo)
    
    
    import AuthorityFileCreation
    
    
    AuthorityFileCreation.generate_authority_list(genus_list + specie_list, fileinfo)
    
    AuthorityFileCreation.generate_authority_file(genus_list + specie_list, fileinfo)
    



