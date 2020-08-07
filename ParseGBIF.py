#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  8 10:28:00 2020

@author: maurop
"""

# =============================================================================
# Imports
# =============================================================================

import pickle

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
# parse gbif taxon
# =============================================================================


class ParseTaxon:
    
    def __init__(self, gbif_taxon, fam_taxa):
        self.gbif_taxon = gbif_taxon
        
        # copy the attributes of the family
        self.taxa = Taxa.Taxa()
        self.taxa.copy_taxa(fam_taxa)
        
        # prepare the scientific name
        self.prepare_name = self.gbif_taxon["scientificName"].replace(self.gbif_taxon["authorship"], "").strip()
        
        # assign the author
        self.taxa.author = self.gbif_taxon["authorship"].strip()
        
        # assign the taxonomic status
        self.taxa.taxonomic_status = self.gbif_taxon["taxonomicStatus"]
        
    
    def get_specie(self):
        # define the name
        name_parts = self.prepare_name.split(" ")
        
        self.taxa.genus = name_parts[0]
        self.taxa.specie = name_parts[1]
        
        # define rank
        self.taxa.rank = Taxa.Taxa.rank_specie
        
        # define source link
        taxon_id = self.gbif_taxon["speciesKey"]
        
        link = taxon_page(taxon_id)[:-1]
        self.taxa.links.append(link)
        
        return self.taxa
    
    def get_genus(self):
        # define the name
        self.taxa.genus = self.prepare_name
        
        #define the rank
        self.taxa.rank = Taxa.Taxa.rank_genus
        
        # define source link
        taxon_id = self.gbif_taxon["genusKey"]
        
        link = taxon_page(taxon_id)[:-1]
        self.taxa.links.append(link)     
        
        return self.taxa
    
    def get_subspecie(self):
        name_parts = self.prepare_name.split(" ")
        
        self.taxa.genus = name_parts[0]
        self.taxa.specie = name_parts[1]
        self.taxa.subspecie = name_parts[2]
        
        # define rank
        self.taxa.rank = Taxa.Taxa.rank_subspecie
        
        # define source link
        taxon_id = self.gbif_taxon["speciesKey"]
        
        link = taxon_page(taxon_id)[:-1]
        self.taxa.links.append(link)
        
        return self.taxa 

# =============================================================================
# Inputs
# =============================================================================

#family_name = "Mycetophilidae"
#base_folder = "./Data/GBIF_test"

def get_children(taxon_key, filename, limit_params={"limit" : 1000, "offset" : 0}):
    url = children_url(taxon_key)
    #filename = file_info.cache_filename(name)
    req = RequestsHandler.Request(url, filename, limit_params)
    return req.get_json()

def generate_lists(family_name, file_info, load_lists = True):
    logger.main_log("Generating taxa list from GBIF database...")
    logger.log_short_report("Input name: " + family_name)
    
    # establish the first query
    param = {"name" : family_name}
    family_query = RequestsHandler.Request(match_api_url, file_info.cache_filename("family_query"), param)
    family_query.load()
        
    family_json = family_query.get_json()
    
    # check if the name is found
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
    
    
    # request the pages of results belonging to the family
    children_json = dict()
    children_json["endOfRecords"] = False
    offset = 0
    
    # append the filenames of the cached pages so that can be analyzed later
    # without cluttering the memory
    pages = []

    while children_json["endOfRecords"] != True: # and len(pages) < 1:
        # Get the childrens of the family
        limit_param = {"limit" : 1000,
                       "offset" : offset}
        
        filename = file_info.cache_filename("children_page_" + str(offset))
        
        children_json = get_children(family_json["familyKey"], filename, limit_param)
        
#        children_req = RequestsHandler.Request(children_url(family_json["familyKey"]), 
#                                               filename,
#                                               limit_param)
#        children_req.load()
#        children_json = children_req.get_json()
        
        offset += 1
        
        pages.append(filename)
        
        logger.main_log(f"record page: {offset} end of record: {children_json['endOfRecords']}")
        
    logger.report_log(f"Pages found: {len(pages)}")
    
    
    
    # Create the taxon reference for the family
    fam_taxa = Taxa.Taxa()
    fam_taxa.family = family_name
    fam_taxa.source = "g"
    fam_taxa.rank = Taxa.Taxa.rank_family
    
           
    
    # scroll through the pages, and results to find the sub taxa
    logger.console_log("Gathering child taxa...")
    
    genus_list = []
    species_list = []
    
    # every page contains 1000 results
    for page in pages:
        
        # load the page information
        children_json = None
        with open(page, "rb") as f:
            children_json = pickle.load(f).json()
        
        # process the results
        for i, taxon in enumerate(children_json["results"]):
            pt = ParseTaxon(taxon, fam_taxa)
                        
            # search for the genus, and if is a genus, find the children species
            if taxon["rank"] == "GENUS":    
                # put genus in genus list
                tax = pt.get_genus()
                genus_list.append(tax)
                
                # look for species associated with the genus
                genus_id = taxon["genusKey"]
                                
#                filename = file_info.cache_filename(str(genus_id) + "_genus_children")
#                species_response = get_children(genus_id, filename)
#                
#                if not species_response["endOfRecords"]:
#                    raise Exception(f"ParseGBIF genus: {tax.genus} has more than 1000 species")
                    
                    
                # cycle throught the response pages
                
                results = []

                species_response = dict()
                species_response["endOfRecords"] = False
                
                limit_param = dict()
                limit_param["limit"] = 1000
                
                offset = 0
                while not species_response["endOfRecords"]:
                    
                    limit_param["offset"] = offset
                    
                    filename = file_info.cache_filename(f"{genus_id}_genus_children_page_{offset}")
                    species_response = get_children(genus_id, filename, limit_param)
                    
                    results += species_response["results"]
                    offset += 1
                    
                
                
                # navigate through the child taxa of the genus
                for specie in results:
    
                    if specie["rank"] == "SPECIES":
                        pt = ParseTaxon(specie, fam_taxa)
                        
                        # append the specie
                        stax = pt.get_specie()
                        species_list.append(stax)
                        
                        # look for subspecies associated with the specie
                        specie_id = specie["speciesKey"]
                        
                        filename = file_info.cache_filename(str(specie_id) + "_specie_children")
                        species_children = get_children(specie_id, filename)
                        
                        if not species_children["endOfRecords"]:
                            raise Exception(f"ParseGBIF genus: {tax.specie} has more than 1000 substuff")
                                                
                        for sc in species_children["results"]:

                            if sc["rank"] == "SUBSPECIES":
                                pt = ParseTaxon(sc, fam_taxa)
                                sctax = pt.get_subspecie()
                                species_list.append(sctax)
                                
            
            # pick the species that don't have a genus apparently
            if taxon["rank"] == "SPECIES":
                stax = pt.get_specie()
                species_list.append(stax)       
            
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
    
    if gbif_taxon["rank"] == "SPECIES":
        taxa.rank = Taxa.Taxa.rank_specie
    
    if gbif_taxon["rank"] == "SUBSPECIES":
        taxa.subspecie = name_parts[2]
        taxa.rank = Taxa.Taxa.rank_subspecie        
        
    
    author = gbif_taxon["authorship"].strip()      
    taxa.author = author
    
    return taxa

class Synonym:
    
    def __init__(self, synonym_taxa, accepted_taxa):
        self.synonym_taxa = synonym_taxa
        self.accepted_taxa = accepted_taxa

def get_synonyms(taxa_list, file_info):
    synonym_list = []
    
    # Create the taxon reference for the family
    fam_taxa = Taxa.Taxa()
    fam_taxa.family = file_info.family_name
    fam_taxa.source = "g"
    fam_taxa.rank = Taxa.Taxa.rank_family    
    
    for taxa in taxa_list:

        url = taxa.links[0] + "/synonyms"
        if taxa.is_subspecie():
            filename = file_info.cache_filename(f"{taxa.genus}_{taxa.specie}_{taxa.subspecie}_synonym")
        else:
            filename = file_info.cache_filename(f"{taxa.genus}_{taxa.specie}_synonym")
        
        req = RequestsHandler.Request(url, filename)
        req.load()
        
        
        if req.response.status_code == 503:
            logger.log_report_console(f"Response 503 from server: {taxa.genus} {taxa.specie} no synonyms retrived")
            logger.log_report_console(f"url: {url}")
            continue

        jreq = req.get_json()

        results = jreq["results"]
        
        if len(results) > 0:
            #print(taxa)
            pass
        
        for taxon in results:
            # get genus
            if taxon["scientificName"].find(":") != -1:
                continue
            
            
            p_syn = ParseTaxon(taxon, fam_taxa)
            
            if taxon["rank"] == "SPECIES":
                syn = p_syn.get_specie()
                
            elif taxon["rank"] == "SUBSPECIES":
                syn = p_syn.get_subspecie()
            else:
                continue
            
            #print(" = ", syn)
            
            synonym_list.append(Synonym(syn, taxa))
                
    synonym_list.sort(key= lambda t : t.synonym_taxa.sort_key_genus())
    
    return synonym_list

# format synonyms    
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
    family_name = "Noctuidae"
    base_folder = "./Tests/test_GBIF"
    file_info = FileInfo.FileInfo(base_folder, "gbif", family_name)
    logger.set_run_log_filename(base_folder + "/" + family_name + "/gbif_test")
    
    genus_list, species_list = generate_lists(family_name, file_info)
    
    with open(file_info.name_only("genus_list.log") , "w") as f:
        for genus in genus_list:
            f.write(str(genus) + "\n")
    
#    get_synonyms(species_list, file_info)
    
#    for genus in genus_list:
#        print(genus)
#        
#        
#    for specie in species_list:
#        print(specie)
    
#    import CreateAuthorityFile
#    CreateAuthorityFile.generate_authority_list(genus_list, species_list, file_info)    
    
    
    
    