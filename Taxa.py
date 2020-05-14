# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 10:07:07 2020

@author: maurop
"""

import pickle


class Taxa:
    ''' Small class that contains the taxon information'''

    source_gbif = "g"
    source_nbn = "n"
    source_eol = "e"
    
    rank_subspecie = "subspecie"
    rank_specie = "specie"
    rank_genus = "genus"
    rank_family = "family"
    
    def __init__(self):        
        
        self.specie = None
        self.subspecie = None
        self.genus = None
        self.tribe = None
        self.subfamily = None
        self.family = None
        
        self.author = None
        
        self.links = []
        
        self.source = None
        
        self.rank = None
        
    def copy_taxonomy(self, taxa):
        self.specie = taxa.specie
        self.subspecie = taxa.subspecie
        self.genus = taxa.genus
        self.tribe = taxa.tribe
        self.subfamily = taxa.subfamily
        self.family = taxa.family
        
    def copy_attributes(self, taxa):
        self.rank = taxa.rank
        self.source = taxa.source
    
    def copy_taxa(self, taxa):
        self.copy_attributes(taxa)
        self.copy_taxonomy(taxa)
    
    def print_extended(self):
        
        print(self.rank.upper(), self.family, self.subfamily, self.tribe, self.genus, self.specie, self.subspecie, self.author)
        
    def __str__(self):
        
        if self.rank == self.rank_specie:
            return self.genus + " " + self.specie + " | " + self.author
        
        elif self.rank == self.rank_genus:
            return self.genus + " sp." + " | " + self.author
        
        elif self.rank == self.rank_subspecie:
            return self.genus + " " + self.specie +  " " + self.subspecie + " | " + self.author
        
        else:
            raise Exception("Taxa feature not implemented")
        

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
    taxa.author = "Vaisanen, 1994"
    taxa.rank = Taxa.rank_specie
    
    print(taxa)
    
    taxa.print_extended()
    
    
    
    