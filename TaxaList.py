#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 29 09:21:10 2020

@author: maurop
"""
# =============================================================================
# Imports
# =============================================================================

import os
import pickle

import Taxa
import ParseNBN
import ParseEOL
import ParseGBIF
import ParseBOLD
import FileInfo
import LogFiles

# =============================================================================
# Logging
# =============================================================================

logger = LogFiles.Logger(__name__)

# =============================================================================
# Functions
# =============================================================================

class AssociatedTaxa:
    ''' class that couples a taxa with a list of subtaxa, like a subfamily
        coupled with a genus
    '''
        
    def __init__(self, main_taxa, rank):
        
        self.rank = rank
        self.main_taxa = main_taxa
        self.associates = []
    
    def add_associate(self, associate):
        self.associates.append(associate)
    
    def __eq__(self, other):
        return self.main_taxa == other
    
    def __str__(self):
        
        associates_str = "".join(associate + ", " for associate in self.associates)
        associates_str = associates_str[:-2]
        return "- " + self.main_taxa + ": " + associates_str


class TaxaList:
    ''' This class manages the generation and chaching of the taxa list,
    the taxa list may include any taxons from genus to species, to subspecies
    '''
    
    
    def __init__(self, taxa_list = None):
        self.taxa = taxa_list

    def generate_list(self, family_name, fileinfo, source):
        ''' The function generates the list given the source'''
        source_module = {"nbn"  : ParseNBN,
                         "eol"  : ParseEOL,
                         "gbif" : ParseGBIF,
                         "bold" : ParseBOLD
                         }
        
        logger.log_short_report("--- Generating the taxa list from the module: " + source.upper() + " ---")
        
        genus_list, species_list = source_module[source].generate_lists(family_name, fileinfo)
        self.taxa = genus_list + species_list        

    
    def add_lists(self, taxa_lists):
        ''' The function fuses multiple taxa list together'''
        
        fusion_list = self.taxa
        
        # Now scan the other lists for duplicates and fill in missing informations
        for taxa_list in taxa_lists:
            
            # for each taxa in the list
            for taxa in taxa_list.taxa:
                
                # compare it with the taxa, if is already there add the links 
                # sources and eventual taxonomy differences
                for ftaxa in fusion_list:
                    
                    # if the taxon is present fuses the taxonmy and various
                    # information
                    if ftaxa.is_equal(taxa):
                        ftaxa.copy_taxonomy(taxa)
                        
                        if ftaxa.author == None and taxa.author != None:
                            ftaxa.author = taxa.author
                        
                        ftaxa.source += taxa.source
                        ftaxa.links += taxa.links
                        break
                # appends the taxa if is not found in the fused list
                else:
                    fusion_list.append(taxa)
                    
        self.taxa = fusion_list
    
    
    def filter_taxa(self, genera_filter):
        ''' The function filters the taxa list according to genera'''
        
        if genera_filter:
        
            genus_filtered = []
        
            # little debug counter to check how many are selected    
            
            genus_count = {}
                
            for g in genera_filter:
                genus_count[g] = 0
            
            for taxa in self.taxa:
                
                for filt in genera_filter:
                    if taxa.genus.find(filt) != -1:
                        genus_filtered.append(taxa)
                        genus_count[filt] += 1
            
            logger.log_short_report("--- Items found in genus filtering ---")
            for genus_name, count in genus_count.items():
                logger.log_short_report(f"  {genus_name}: {count}")
            logger.log_short_report("--------------------------------------")
        
            self.taxa = genus_filtered
        
    def filter_status(self):
        ''' Tests wether the status of the taxonomic name is accepted, the
            taxonomic status information are retrived from the GBIF database
        '''
        
        logger.log_short_report("--- Filter names with non accepted status ---")
        previous_size = len(self.taxa)
        
        def check_status(item):
            if item.taxonomic_status != None:
                if item.taxonomic_status == "ACCEPTED":
                    return True
                else:
                    logger.log_report(f"{item} status: {item.taxonomic_status}")
            else:
                return True
        
        self.taxa = list(filter(lambda item : check_status(item), self.taxa))
        
        actual_size = len(self.taxa)
        
        n_filtered = previous_size - actual_size
        logger.log_short_report(f"Filtered {n_filtered} taxons")
    
    
    def add_taxon(self, taxon):
        self.taxa.append(taxon)
        
    def save(self, fileinfo, name):
        logger.main_log("Taxa list saved in: " + fileinfo.mptaxa_filename(name))
        with open(fileinfo.mptaxa_filename(name), "wb") as f:
            pickle.dump(self.taxa, f)
        
    def load(self, fileinfo, name):
        logger.main_log("Taxa list loaded from: " + fileinfo.mptaxa_filename(name))
        with open(fileinfo.mptaxa_filename(name), "rb") as f:
            self.taxa = pickle.load(f)
    
    def load_existing(self, fileinfo, name):
        ''' loads the file from disk if present else it returns false'''
        if fileinfo.mptaxa_exists(name):
            self.load(fileinfo, name)
            logger.log_short_report(f"Loaded {len(self.taxa)} taxa from disk {fileinfo.prefix}_{name}.mptaxa")
            return True
        else:
            return False
        
    def find_associations(self):
        ''' Function that finds from a taxa list which subfamilies and tribes are
        associated wit which genus'''
        
        subfamilies = []
        tribes = []    
        
        # generates the associations between genus and subfamily or tribe
        
        # first looks for all the subfamilies and tribes in the list
        for taxa in self.taxa:
            if taxa.subfamily not in subfamilies and taxa.subfamily != None:
                main_taxon = AssociatedTaxa(taxa.subfamily, Taxa.Taxa.rank_subfamily)
                subfamilies.append(main_taxon)
    
            if taxa.tribe not in tribes and taxa.tribe != None:
                main_taxon = AssociatedTaxa(taxa.tribe, Taxa.Taxa.rank_tribe)
                tribes.append(main_taxon)
        
        # then fills which genera are associated with the given subfamily
        for taxa in self.taxa:
            
            for subfamily in subfamilies:
                
                if taxa.subfamily == subfamily:
                    
                    if taxa.genus not in subfamily.associates:
                        subfamily.add_associate(taxa.genus)
            
            
            for tribe in tribes:
                
                if taxa.tribe == tribe:
                    
                    if taxa.genus not in tribe.associates:
                        tribe.add_associate(taxa.genus)
        
        # little debug to show how many have been found
        
        logger.log_short_report("--- Subfamilies / Tribes with associated genera ---")
        logger.log_report("Subfamilies")
        
        for subfamily in subfamilies:
            logger.log_report("  " + subfamily.main_taxa)
            for genus in subfamily.associates:
                logger.log_report("    " + genus)
                
        logger.log_short_report("Subfamilies found: " + str(len(subfamilies)))
        
        logger.log_report("Tribes")
        for tribe in tribes:
            logger.log_report("  " + tribe.main_taxa)
            for genus in tribe.associates:
                logger.log_report("    " + genus)        

        logger.log_short_report("Tribes found: " + str(len(subfamilies)))
                         
        return subfamilies, tribes


    def fill_associations(self, associations = None):
        ''' the function acts on the list itself and fills in which genera
        are still missing the subfamily/tribe selected form the function
        find_associations'''
        
        if associations:
            subfamilies = associations[0]
            tribes = associations[1]
        else:
            subfamilies, tribes = self.find_associations()
        
        for taxa in self.taxa:
            if taxa.subfamily == None:
                for subfamily in subfamilies:
                    if taxa.genus in subfamily.associates:
                        taxa.subfamily = subfamily.main_taxa
                        break
    
            if taxa.tribe == None:
                for tribe in tribes:
                    if taxa.genus in tribe.associates:
                        taxa.tribe = tribe.main_taxa
                        break
        
    def sort(self, rank = None):
        self.taxa.sort(key=lambda t : t.sort_key())

    def clean_noauthor(self):
        # function that checks and logs the author
        
        logger.log_short_report("--- Names excluded because no author is available ---")
        
        def no_author(item):
            if item.author:
                return True
            else:
                logger.log_report(f"{item}")
                return False
        
        previous_size = len(self.taxa)
        self.taxa = list(filter(lambda item : no_author(item), self.taxa))
        actual_size = len(self.taxa)
        
        n_filtered = previous_size - actual_size
        logger.log_short_report(f"Filtered {n_filtered} taxons")
    
    def get_species_list(self):
        return list(filter(lambda t : t.is_specie() or t.is_subspecie(), self.taxa))
        
        
            


# =============================================================================
# Function that generate the list giving the basic parameter
# =============================================================================

def generate_taxa_list_single(base_folder, source, family_name):
    
    fileinfo = FileInfo.FileInfo(base_folder, source, family_name)
    
    taxa_list = TaxaList()
    
    # load the files from disk if they exists, else generate the lists
    
    if taxa_list.load_existing(fileinfo, "taxa_list"):
        pass
    else:
        taxa_list.generate_list(family_name, fileinfo, source)
        taxa_list.save(fileinfo, "taxa_list")
    
    return taxa_list

def generate_taxa_list(base_folder, sources, family_name, genera_filter):
    
    taxa_lists = []
    
    # retrive the data from the different sources
    
    for source in sources:
        fileinfo = FileInfo.FileInfo(base_folder, source, family_name)
        
        taxa_list = TaxaList()
        
        # load the files from disk if they exists, else generate the lists
        
        if taxa_list.load_existing(fileinfo, "taxa_list"):
            pass
        else:
            taxa_list.generate_list(family_name, fileinfo, source)
            taxa_list.save(fileinfo, "taxa_list")
        
        taxa_lists.append(taxa_list)
     
    # fuse the taxas in one big list, always cgeck if there is a file cached
    fileinfo = FileInfo.FileInfo(base_folder, "_".join(sources), family_name)    
    taxa_list_fused = TaxaList()
    
    if taxa_list_fused.load_existing(fileinfo, "taxa_list"):
        pass
    else:
        taxa_list_fused = taxa_lists[0]
        taxa_list_fused.add_lists(taxa_lists[1:]) 
        taxa_list_fused.save(fileinfo, "taxa_list")
        
    taxa_list_filtered = TaxaList()
    
    # filter the list with given genera
    
    # file contaning the previous filters 
    genera_filter_file = fileinfo.txt_filename("previous_genera_filter")
    
    # function that filters the list accordingly, save the new list
    # saves the prveious genera
    def filter_list(taxa_list):
        
        with open(genera_filter_file, "w") as f:
            f.write(", ".join(genera_filter))
            
        taxa_list = taxa_list_fused
        taxa_list.filter_status()
        taxa_list.filter_taxa(genera_filter)
        taxa_list.save(fileinfo, "filtered_taxa_list")
        
        return taxa_list
    
    # Check if the previous genera exists, else creates the list
    # Check if the genera are the same as the current filter
    # if they are different generates a new list
    # if they are the same and a file already exists containing the filtered
    # taxa list then loads it, else generates the file
    
    if os.path.isfile(genera_filter_file):
        with open(genera_filter_file, "r") as f:
            data = f.read()
        
        previous_genera = data.split(",")
        previous_genera = [genus.strip() for genus in previous_genera]
        
        if set(genera_filter) == set(previous_genera):
            if taxa_list_filtered.load_existing(fileinfo, "filtered_taxa_list"):
                pass
            else:
                taxa_list_filtered = filter_list(taxa_list_filtered)  
        else:
            taxa_list_filtered = filter_list(taxa_list_filtered)                  
    else:
        taxa_list_filtered = filter_list(taxa_list_filtered)    
    
    # Fills in the subfamiles and tribes
    taxa_list_filtered.fill_associations()
    
    # sorts the list after subfamily/tribe/genus...
    taxa_list_filtered.sort()
    
    return taxa_list_filtered


    

if __name__ == "__main__":
    
    base_folder = "./Tests/test_TaxaList/"
    sources = ["eol", "nbn", "gbif", "bold"]
    family_name = "Chrysididae"
    genera_filter = []
    logger.set_run_log_filename(base_folder + "TaxaList")
    
    taxa_list = generate_taxa_list(base_folder, sources, family_name, genera_filter)
    
    
    for taxa in taxa_list.taxa:
        if taxa.subfamily or taxa.tribe:
            print(taxa)
        
    import CreateAuthorityFile
    
    
    fileinfo = FileInfo.FileInfo(base_folder, "_".join(sources), family_name) 
    CreateAuthorityFile.generate_authority_file(taxa_list.taxa, fileinfo)
        
    print("Taxa in  the list:", len(taxa_list.taxa))
    
    
    
    