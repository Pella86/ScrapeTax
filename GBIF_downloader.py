#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  8 10:28:00 2020

@author: maurop
"""

# =============================================================================
# Imports
# =============================================================================

# my imports
import request_handler
import Taxa
import FileInfo
import ProgressBar


# =============================================================================
# Constants
# =============================================================================

api_url = "https://api.gbif.org/v1"

species = "/species/"

match = "/species/match/"

match_api_url = f"{api_url}{match}"

def taxon_page(key):
    return f"{api_url}/species/{key}/"

def children_url(key):
    return taxon_page(key) + "children/"


# =============================================================================
# Inputs
# =============================================================================

family_name = "Mycetophilidae"
base_folder = "./Data/GBIF_test"

def generate_lists(family_name, file_info, load_lists = True):
    print("Generating taxa list from GBIF database...")
    print("Input name: ", family_name)
    
    # establish the first query
    
    #file_info = FileInfo.FileInfo(base_folder, family_name.lower())
    
    param = {"name" : family_name}
    family_query = request_handler.Request(match_api_url, file_info.pickle_filename("family_query"), param)
    family_query.load()
    
    
    family_json = family_query.get_json()
    
    if family_json.get("family") != None: 
        print("Found:", family_json["family"], "Confidence:", str(family_json["confidence"]) + "%", "match type:", family_json["matchType"])
    else:
        raise Exception("GBIF: Name not found because: " +  str(family_json))
    
    # Json structure of the family json
    #import json
    #print(json.dumps(family_json, indent=2))
    #
    #{
    #  "usageKey": 5565,
    #  "scientificName": "Mycetophilidae",
    #  "canonicalName": "Mycetophilidae",
    #  "rank": "FAMILY",
    #  "status": "ACCEPTED",
    #  "confidence": 94,
    #  "matchType": "EXACT",
    #  "kingdom": "Animalia",
    #  "phylum": "Arthropoda",
    #  "order": "Diptera",
    #  "family": "Mycetophilidae",
    #  "kingdomKey": 1,
    #  "phylumKey": 54,
    #  "classKey": 216,
    #  "orderKey": 811,
    #  "familyKey": 5565,
    #  "synonym": false,
    #  "class": "Insecta"
    #}
    
    
    # get the family main page
    
    family_page = request_handler.Request(taxon_page(family_json["familyKey"]), file_info.pickle_filename("family_page"))
    family_page.load()
    family_json = family_page.get_json()
    
    #import json
    #print(json.dumps(family_json, indent=2))
    #{
    #  "key": 5565,
    #  "nubKey": 5565,
    #  "nameKey": 7242389,
    #  "taxonID": "gbif:5565",
    #  "sourceTaxonKey": 155863502,
    #  "kingdom": "Animalia",
    #  "phylum": "Arthropoda",
    #  "order": "Diptera",
    #  "family": "Mycetophilidae",
    #  "kingdomKey": 1,
    #  "phylumKey": 54,
    #  "classKey": 216,
    #  "orderKey": 811,
    #  "familyKey": 5565,
    #  "datasetKey": "d7dddbf4-2cf0-4f39-9b2a-bb099caae36c",
    #  "constituentKey": "7ddf754f-d193-4cc9-b351-99906754a03b",
    #  "parentKey": 811,
    #  "parent": "Diptera",
    #  "scientificName": "Mycetophilidae",
    #  "canonicalName": "Mycetophilidae",
    #  "authorship": "",
    #  "nameType": "SCIENTIFIC",
    #  "rank": "FAMILY",
    #  "origin": "SOURCE",
    #  "taxonomicStatus": "ACCEPTED",
    #  "nomenclaturalStatus": [],
    #  "remarks": "",
    #  "numDescendants": 7215,
    #  "lastCrawled": "2019-09-06T05:41:48.812+0000",
    #  "lastInterpreted": "2019-09-06T04:35:49.995+0000",
    #  "issues": [],
    #  "synonym": false,
    #  "class": "Insecta"
    #}
    
    
    # Get the childrens of the family
    limit_param = {"limit" : family_json["numDescendants"]}
    
    children_req = request_handler.Request(children_url(family_json["familyKey"]), file_info.pickle_filename("children"), limit_param)
    children_req.load()
    children_json = children_req.get_json()
    
   
    
    # content of children json
    # children_json keys:
    # dict_keys(['offset', 'limit', 'endOfRecords', 'results'])
    
    # example of the first element of the resulst (children_json[”results"][0])
    #  "authorship": "Hutton, 1904",
    #  "canonicalName": "Anomalomyia",
    #  "class": "Insecta",
    #  "classKey": 216,
    #  "constituentKey": "7ddf754f-d193-4cc9-b351-99906754a03b",
    #  "datasetKey": "d7dddbf4-2cf0-4f39-9b2a-bb099caae36c",
    #  "family": "Mycetophilidae",
    #  "familyKey": 5565,
    #  "genus": "Anomalomyia",
    #  "genusKey": 1615502,
    #  "issues": [],
    #  "key": 1615502,
    #  "kingdom": "Animalia",
    #  "kingdomKey": 1,
    #  "lastCrawled": "2019-09-06T05:41:48.812+0000",
    #  "lastInterpreted": "2019-09-06T04:35:55.714+0000",
    #  "nameKey": 709396,
    #  "nameType": "SCIENTIFIC",
    #  "nomenclaturalStatus": [],
    #  "nubKey": 1615502,
    #  "numDescendants": 13,
    #  "order": "Diptera",
    #  "orderKey": 811,
    #  "origin": "SOURCE",
    #  "parent": "Mycetophilidae",
    #  "parentKey": 5565,
    #  "phylum": "Arthropoda",
    #  "phylumKey": 54,
    #  "publishedIn": "Index Faunae N. Zealand",
    #  "rank": "GENUS",
    #  "remarks": "",
    #  "scientificName": "Anomalomyia Hutton, 1904",
    #  "sourceTaxonKey": 156980061,
    #  "synonym": false,
    #  "taxonID": "gbif:1615502",
    #  "taxonomicStatus": "ACCEPTED"
    
    
    fam_taxa = Taxa.Taxa()
    fam_taxa.family = family_name
    fam_taxa.source = "g"
    fam_taxa.rank = Taxa.Taxa.rank_family
    
    # Small function to convert the json info in a Taxa
    def generate_mp_taxa(gbif_taxon, mp_taxa_parent_genus):
        name = gbif_taxon["scientificName"].replace(gbif_taxon["authorship"], "").strip()
        author = gbif_taxon["authorship"].strip()        
        
        taxa = Taxa.Taxa()
        taxa.copy_taxa(fam_taxa)
        
        if gbif_taxon["rank"] == "GENUS":
            taxa.genus = name
            taxa.rank = Taxa.Taxa.rank_genus
            taxon_id = gbif_taxon["genusKey"]
            
        else:
            if mp_taxa_parent_genus:
                taxa.copy_taxonomy(mp_taxa_parent_genus)
            taxa.specie = name
            taxa.rank = Taxa.Taxa.rank_specie
            taxon_id = gbif_taxon["speciesKey"]
        
        link = f"{api_url}/species/{taxon_id}"
        
        taxa.links.append(link)
        taxa.author = author
        
        return taxa
    
    def generate_genus(gbif_taxon):
        name = gbif_taxon["scientificName"].replace(gbif_taxon["authorship"], "").strip()
        author = gbif_taxon["authorship"].strip()        
        
        taxa = Taxa.Taxa()
        taxa.copy_taxa(fam_taxa)
        
        taxa.genus = name
        taxa.rank = Taxa.Taxa.rank_genus
        
        taxon_id = gbif_taxon["genusKey"]
        link = f"{api_url}/species/{taxon_id}"
        
        taxa.links.append(link)
        taxa.author = author
        
        taxa.taxonomic_status = gbif_taxon["taxonomicStatus"]
        
        return taxa
        
    def generate_specie(gbif_taxon):    
        
        taxa = Taxa.Taxa()
        taxa.copy_taxa(fam_taxa)
        
        name = gbif_taxon["scientificName"].replace(gbif_taxon["authorship"], "").strip()
        name_parts = name.split(" ")
        
        taxa.genus = name_parts[0]
        taxa.specie = name_parts[1]
        taxa.rank = Taxa.Taxa.rank_specie
        taxon_id = gbif_taxon["speciesKey"]
    
        link = f"{api_url}/species/{taxon_id}"
        
        taxa.links.append(link)
        
        author = gbif_taxon["authorship"].strip()      
        taxa.author = author
        
        taxa.taxonomic_status = gbif_taxon["taxonomicStatus"]
        
        return taxa        
        
    print("Gathering child taxa...")
    genus_list = []
    species_list = []
    
    #pbar = ProgressBar.ProgressBar(len(children_json["results"]))
    

    num_desc = family_json["numDescendants"]
    num_res  = len(children_json["results"])
    
    if num_res != num_desc:
        print(f"GBIF_downlaoder: Results({num_res}) dont match num descendant({num_desc})")
    
    for i, taxon in enumerate(children_json["results"]):
        
        # search for the genus, and if is a genus, find the children species
        if taxon["rank"] == "GENUS":
            
            
            
            tax = generate_genus(taxon)
            
            #print(tax.genus)
            if tax.genus == "Fotella":
                print(tax)
            
            genus_list.append(tax)
            
            # look for the next 
            limit_param["limit"] = taxon["numDescendants"]
            
            genus_id = taxon["genusKey"]
            
            url = children_url(genus_id)
            filename = file_info.pickle_filename(tax.genus)
            
            genus_child = request_handler.Request(url,
                                                  filename,
                                                  limit_param)
            genus_child.load()
            
            species_response = genus_child.get_json()
            
            # navigate throught the child taxa of the genus
            for specie in species_response["results"]:

                
                if specie["rank"] == "SPECIES":
                    stax = generate_specie(specie)
                    
                    
                
                    species_list.append(stax)
                                   
        
        # pick the species that don't have a genus apparently
        if taxon["rank"] == "SPECIES":
            stax = generate_specie(taxon)
            species_list.append(stax)
        
        #pbar.draw_bar(i)
        


#        if taxon["rank"] != "GENUS" and taxon["rank"] != "SPECIES":
#            if not ( "BOLD" in  taxon["scientificName"]):
#                print(taxon["scientificName"])
#                print(taxon["rank"])
        
    
    
    
    print("Genus retrived:", len(genus_list), "Species retrived:", len(species_list))
    return genus_list, species_list


if __name__ == "__main__":    
    family_name = "Noctuidae"
    base_folder = "./Data/GBIF_test"
    file_info = FileInfo.FileInfo(base_folder, "gbif", family_name)
    
    genus_list, species_list = generate_lists(family_name, file_info)
    
#    for genus in genus_list:
#        print(genus)
#        
#        
#    for specie in species_list:
#        print(specie)
    
       
#    AuthorityFileCreation.generate_authority_list(genus_list, species_list, file_info)    
    
    
    
    