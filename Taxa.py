# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 10:07:07 2020

@author: maurop
"""

import pickle


class Taxa:
    ''' Small class that contains the taxon information'''
    
    def __init__(self, name, author, link, supertaxa):
        # Name of the taxon, binomial for species, single for genus
        self.name = str(name)
        
        # author of the taxon
        self.author = str(author)
        
        # reference link, might change to reference links
        self.link = link
        
        # possible taxa connected to this taxa, never used?
        self.super_taxa = supertaxa
        
        # the website source, g for gbif, n for nbn, e for eol
        self.source = ""
        
    def __str__(self):
        return self.name + " | " + self.author    

def save_taxa_list(taxa_list, filename):
    with open(filename, "wb") as f:
        pickle.dump(taxa_list, f)
    
def load_taxa_list(filename):
    with open(filename, "rb") as f:
        data = pickle.load(f)
    return data
    
    
if __name__ == "__main__":
    
    filename = "./Data/Vespidae/vespidae_genus_list.mptaxa"
    
    
    genus_list = load_taxa_list(filename)
    
    print(genus_list[0].link)
    
    
    