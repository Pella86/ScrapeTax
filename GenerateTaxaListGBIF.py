#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 09:55:03 2020

@author: maurop
"""

# =============================================================================
# Imports
# =============================================================================

import re

import LevenshteinDistance
import TaxaList
import ParseGBIF
import FileInfo
import LogFiles


# =============================================================================
# Logging
# =============================================================================


logger = LogFiles.Logger(__name__)

# =============================================================================
# Main functions
# =============================================================================

author_regex = re.compile(r"\(?\[?[\w| |,|&|.|\-|']+\]?, \[?\d\d\d\d\]?\)?")


def get_author_name(author):
    pos = author.rfind(",")

    author_name = author[:pos]
    if author_name.startswith("("):
        author_name = author_name[1:]    
    
    return author_name


def validate_author(author):
    # possible matches
    # author, year
    # (author, year)
    # author1, author2, year
    # author, [year]
    # [author], year
    
    match = author_regex.match(author)
    
    if match:
        return True
    else:
        return False
    
def correct_author(gbif_taxa_list, nbn_taxa_list):  
    
    logger.log("--- Correcting name conflicts ---")
    
    correction_counter = 0
    
    for gbif_taxon in gbif_taxa_list.taxa:        
        for nbn_taxon in nbn_taxa_list.taxa:            
            
            # This is the same genus, specie and subspecie
            if gbif_taxon.compare_specie(nbn_taxon):            

                if gbif_taxon.author == nbn_taxon.author:
                    continue

                gbif_author_name = get_author_name(gbif_taxon.author)
                nbn_author_name = get_author_name(nbn_taxon.author)
                
                # if the name is the same, it means that is a parenthesis
                # issue or a year issue, thus the name of the author is
                # spelled correctly, we take the year parentheses from the nbn as a 
                # reference                
                if gbif_author_name == nbn_author_name:
                    logger.log(f"Corrected year or parenthesis for {gbif_taxon} with {nbn_taxon}", LogFiles.Logger.handler_main_report)
                    gbif_taxon.author = nbn_taxon.author
                    gbif_taxon.links += nbn_taxon.links
                    
                    correction_counter += 1
                    
                else:
                    # if is a name issue check if the name is similar
                    # with the Levenshtein distance
                    distance = LevenshteinDistance.levenshtein(gbif_author_name, nbn_author_name)
            
                    # if the distance is less then 2 letters his means that
                    # is a probable spelling mistake so all the authors name
                    # should be substituted accordingly
                    if distance <= 2:
                        # substitute all the name in the list
                        for sub_author_taxon in gbif_taxa_list.taxa:
                            if get_author_name(sub_author_taxon.author) == gbif_author_name:
                                logger.log(f"Correcting spelling for {sub_author_taxon} | {nbn_author_name}", LogFiles.Logger.handler_main_report)
                                sub_author_taxon.author = sub_author_taxon.author.replace(gbif_author_name, nbn_author_name)
                                sub_author_taxon.links += ["Author spelling from NBN Atlas"]
                        
                                correction_counter += 1        
                    
                    # else there is a true author conflict so we take the 
                    # nbn one?
                    else:
                        if nbn_taxon.author.find("misident.") != -1:
                            continue
                        else:
                            logger.log(f"Name conflict {gbif_taxon} | {nbn_taxon}", LogFiles.Logger.handler_main_report)
                            gbif_taxon.author = nbn_taxon.author
                            gbif_taxon.links += nbn_taxon.links
                    correction_counter += 1
    logger.log(f"Total corrections: {correction_counter}" )

def scrape_gbif(family_name, base_folder, genera_filter):
    
    
    # GET NAMES FROM GBIF
    gbif_taxa_list = TaxaList.generate_taxa_list_single(base_folder, "gbif", family_name)
    
    # filter the non accepted name
    gbif_taxa_list.filter_status()
    
    # filter the list for the relevant genuses
    gbif_taxa_list.filter_taxa(genera_filter)

    # remove taxa without authors
    gbif_taxa_list.clean_noauthor()
    
    # GET FAMILIES FROM BOLD
    
    # scrape the bold website to get the subfamilies and tribes
    bold_taxa_list = TaxaList.generate_taxa_list_single(base_folder, "bold", family_name)
    
    # find subfamilies and tribes
    associations = bold_taxa_list.find_associations()
    
    gbif_taxa_list.fill_associations(associations)

    # GET AUTHORS FROM NBN ATLAS
    
    # use the NBN_Atlas for the authors
    nbn_taxa_list = TaxaList.generate_taxa_list_single(base_folder, "nbn", family_name)
    
    # correct the author if is the case
    correct_author(gbif_taxa_list, nbn_taxa_list)
    
    # create the taxa list that will be passed to the creation of the 
    # authority files
    taxa_list = gbif_taxa_list
    taxa_list.sort()
    
    # filter akwardly formatted authors
    logger.log("--- Authors not correctly formatted ---")
    logger.log("Regex test: " + str(author_regex))
    
    def validate_author_filter(taxa):
        if validate_author(taxa.author):
            return True
        else:
            report_taxa = str(taxa) #+ " source: " + ", ".join(taxa.links)
            logger.log(report_taxa, LogFiles.Logger.handler_main_report)
            return False
        
    previous_size = len(taxa_list.taxa)
    taxa_list.taxa = list(filter(lambda taxa : validate_author_filter(taxa), taxa_list.taxa))
    actual_size = len(taxa_list.taxa)
    
    n_filtered = previous_size - actual_size
    logger.log(f"Filtered {n_filtered} taxons")
    return taxa_list


def generate_synonym_list(family_name, base_folder, taxa_list):
    fileinfo = FileInfo.FileInfo(base_folder, "gbif", family_name)
    species_list = taxa_list.get_species_list()    
    synonym_list = ParseGBIF.get_synonyms(species_list, fileinfo)        
        
    return synonym_list




if __name__ == "__main__":
    
    family_name = "Mycetophilidae"
    base_folder = "./Tests/test_GBIF"
    
    generate_synonym_list(family_name, base_folder)
    
    
    
    
