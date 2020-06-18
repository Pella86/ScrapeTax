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
import RequestsHandler
import Taxa
import FileInfo
import LogFiles

# =============================================================================
# Logging
# =============================================================================

logger = LogFiles.Logger(__name__)

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
    logger.main_log("Generating taxa list from GBIF database...")
    logger.log_short_report("Input name: " + family_name)
    
    # establish the first query
    
    #file_info = FileInfo.FileInfo(base_folder, family_name.lower())
    
    param = {"name" : family_name}
    family_query = RequestsHandler.Request(match_api_url, file_info.cache_filename("family_query"), param)
    family_query.load()
    
    
    family_json = family_query.get_json()
    
    if family_json.get("family") != None: 
        family = family_json['family']
        confidence = family_json['confidence']
        match_type = family_json["matchType"]
        log_str = f"Found: {family} Confidence: {confidence}% match type: {match_type}"
        logger.log_short_report(log_str)
    else:
        logger.log_short_report("GBIF: Name not found because: " +  str(family_json))
        raise Exception("GBIF: Name not found because: " +  str(family_json))
    
    # get the family main page
    
    family_page = RequestsHandler.Request(taxon_page(family_json["familyKey"]), file_info.cache_filename("family_page"))
    family_page.load()
    family_json = family_page.get_json()
 
    
    # Get the childrens of the family
    limit_param = {"limit" : family_json["numDescendants"]}
    
    children_req = RequestsHandler.Request(children_url(family_json["familyKey"]), file_info.cache_filename("children"), limit_param)
    children_req.load()
    children_json = children_req.get_json()
    
    # Create the taxon reference for the family
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
        
    logger.console_log("Gathering child taxa...")
    genus_list = []
    species_list = []
    
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
            filename = file_info.cache_filename(tax.genus)
            
            genus_child = RequestsHandler.Request(url,
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
        


#        if taxon["rank"] != "GENUS" and taxon["rank"] != "SPECIES":
#            if not ( "BOLD" in  taxon["scientificName"]):
#                print(taxon["scientificName"])
#                print(taxon["rank"])
        
    
    
    n_genera = len(genus_list)
    n_species = len(species_list)
    logger.log_short_report(f"Genus retrived: {n_genera} Species retrived: {n_species}")
    return genus_list, species_list


def mp_taxa_specie(gbif_taxon):
    taxa = Taxa.Taxa()
    
    name = gbif_taxon["scientificName"].replace(gbif_taxon["authorship"], "").strip()
    name_parts = name.split(" ")
    
    taxa.genus = name_parts[0]
    taxa.specie = name_parts[1]
    taxa.rank = Taxa.Taxa.rank_specie
    
    author = gbif_taxon["authorship"].strip()      
    taxa.author = author
    
    return taxa

class Synonym:
    
    def __init__(self, synonym_taxa, accepted_taxa):
        self.synonym_taxa = synonym_taxa
        self.accepted_taxa = accepted_taxa

def get_synonyms(taxa_list, file_info):
    
    
    synonym_list = []
    
    for taxa in taxa_list:

        url = taxa.links[0] + "/synonyms"
        filename = file_info.cache_filename(f"{taxa.genus}_{taxa.specie}_synonym")
        
        req = RequestsHandler.Request(url, filename)
        
        jreq = req.get_json()

        results = jreq["results"]
        
        if len(results) > 0:
            #print(taxa)
            pass
        
        for taxon in results:
            # get genus
            
            if taxon["scientificName"].find(":") != -1:
                continue
            
            syn = mp_taxa_specie(taxon)
            #print(" = ", syn)
            
            synonym_list.append(Synonym(syn, taxa))
                
    synonym_list.sort(key= lambda t : t.synonym_taxa.sort_key_genus())
    
    return synonym_list
    
#    max_len = max(map(lambda t : len(str(t.synonym_taxa)), synonym_list))
#
#    s = ""
#    for taxa in synonym_list:
#        fmt = "{0:.<" + str(max_len) + "}{1}\n"
#        s += fmt.format(str(taxa.synonym_taxa), str(taxa.accepted_taxa))
#        
#    with open(file_info.txt_filename("synonym_list"), "w") as f:
#        f.write(s)       
    
    
#    s = ""
#    for taxa in synonym_list:
#        print(taxa.synonym_taxa, taxa.accepted_taxa)
#        s += str(taxa.synonym_taxa) + "
#        
#    with open(file_info.txt_filename("synonym_list"), "w") as f:
#        for taxa in synonym_list:
#            f.write(taxa.synonym_taxa, taxa.accepted_taxa)        


if __name__ == "__main__":    
    family_name = "Mycetophilidae"
    base_folder = "./Tests/test_GBIF"
    file_info = FileInfo.FileInfo(base_folder, "gbif", family_name)
    
    genus_list, species_list = generate_lists(family_name, file_info)
    
    get_synonyms(species_list, file_info)
    
#    for genus in genus_list:
#        print(genus)
#        
#        
#    for specie in species_list:
#        print(specie)
    
       
#    AuthorityFileCreation.generate_authority_list(genus_list, species_list, file_info)    
    
    
    
    