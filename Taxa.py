# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 10:07:07 2020

@author: Media Markt
"""

import pickle


class Taxa:
    
    def __init__(self, name, author, link, supertaxa):
        self.name = str(name)
        self.author = str(author)
        self.link = link
        self.super_taxa = supertaxa
        
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
    
    
    genus_list = laod_taxa_list(filename)
    
    print(genus_list[0].link)
    
    
    