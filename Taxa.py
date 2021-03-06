# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 10:07:07 2020

@author: maurop
"""

import pickle

import LogFiles

logger = LogFiles.Logger(__name__)


class Taxa:
    ''' Small class that contains the taxon information'''

    source_gbif = "g"
    source_nbn = "n"
    source_eol = "e"
    source_bold = "b"
    
    rank_subspecie = "subspecie"
    rank_specie = "specie"
    rank_genus = "genus"
    rank_tribe = "tribe"
    rank_subfamily = "subfamily"
    rank_family = "family"
    
    
    def __init__(self):        
        
        # taxonomic informations
        self.subspecie = None
        self.specie = None
        self.genus = None
        self.tribe = None
        self.subfamily = None
        self.family = None
        
        # Author corresponding to the rank        
        self.author = None
        
        # Relative links
        self.links = []
        
        # Source website
        self.source = None
        
        # rank of the taxonomic information
        self.rank = None
        
        # taxonomic status
        self.taxonomic_status = None
        
    def copy_taxonomy(self, taxa):
        ''' Copies the taxonomy from a given taxa'''
    
        self.specie = taxa.specie 
        self.subspecie = taxa.subspecie
        self.genus = taxa.genus
        self.tribe = taxa.tribe if taxa.tribe else self.tribe
        self.subfamily = taxa.subfamily if taxa.subfamily else self.subfamily
        self.family = taxa.family
        
    def copy_attributes(self, taxa):
        ''' Copy attributes not relevant to the taxonomy'''
        self.rank = taxa.rank
        self.source = taxa.source
    
    def copy_taxa(self, taxa):
        self.copy_attributes(taxa)
        self.copy_taxonomy(taxa)
    
    def print_extended(self):
        print(self.rank.upper(), self.family, self.subfamily, self.tribe, self.genus, self.specie, self.subspecie, self.author)
        
    
    def is_equal(self, taxa):
        ''' Function that tells if two taxa are equal, 
                if one field is None is considered as equal to an other but if
                is specie, genus or author than the taxa are different
        '''
        if self.subfamily != None and taxa.subfamily != None:
            if self.subfamily != taxa.subfamily:
                return False

        if self.tribe != None and taxa.tribe != None:
            if self.tribe != taxa.tribe:
                return False
        
        if self.author != None and taxa.author != None:
            if self.author != taxa.author:
                return False
        
        if self.genus == taxa.genus and self.specie == taxa.specie and self.subspecie == taxa.subspecie:
            return True
        else:
            return False
        
    def compare_specie(self, taxa):
        if self.genus == taxa.genus and self.specie == taxa.specie and self.subspecie == taxa.subspecie:
            return True
        return False
        
    def test_none(self, rank):
        if rank == None:
            return "z" * 20
        else:
            return rank
    
    def sort_key(self):

        subfamily = self.test_none(self.subfamily)
        tribe = self.test_none(self.tribe)
        genus = self.test_none(self.genus)
        specie = self.test_none(self.specie)
        subspecie = self.test_none(self.subspecie)

        return subfamily + tribe + genus + specie + subspecie


    def sort_key_genus(self):
        skey = ""
        
        skey += self.test_none(self.genus)
        skey += self.test_none(self.specie)
        skey += self.test_none(self.subspecie)

        return skey
    
    def str_author(self):
        return self.author if self.author else "No author available"
        
    def __str__(self):
        
        if self.is_specie():
            return self.genus + " " + self.specie + " | " + self.str_author()
        
        elif self.rank == self.rank_genus:
            return self.genus + " sp." + " | " + self.str_author()
        
        elif self.rank == self.rank_subspecie:
            return self.genus + " " + self.specie +  " " + self.subspecie + " | " + self.str_author()
        
        elif self.rank == self.rank_subfamily:
            return self.subfamily + " | " + self.str_author()
        
        elif self.rank == self.rank_tribe:
            return self.tribe + " | " + self.str_author()
        else:
            logger.log("Taxa feature not implemented: " + self.rank)
            raise Exception("Taxa feature not implemented: " + self.rank)
    
    def is_specie(self):
        return self.rank == self.rank_specie
    
    def is_subspecie(self):
        return self.rank == self.rank_subspecie
    
    def get_name(self):
        
        name = ""
        if self.genus:
            name += self.genus
        
        if self.specie:
            name += " " + self.specie
            
            if self.subspecie:
                name += " " + self.subspecie
                return name
            
            else:
                return name
            
        else:
            name += " sp."
            return name
        

def save_taxa_list(taxa_list, filename):
    with open(filename, "wb") as f:
        pickle.dump(taxa_list, f)
    
def load_taxa_list(filename):
    with open(filename, "rb") as f:
        data = pickle.load(f)
    return data

        
    
if __name__ == "__main__":
    
    taxa = Taxa()
    
    taxa.specie = "edra"
    taxa.genus = "Mycomiya"
    taxa.author = "Väisänen, 1994"
    taxa.rank = Taxa.rank_specie
    
    print(taxa)
    
    taxa.print_extended()
    
    
    
    