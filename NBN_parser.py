# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 09:55:42 2020

@author: Media Markt
"""

import bs4
import pickle
import os

import request_handler
import Taxa


NBN_HOME = "https://species.nbnatlas.org"   


def gather_child_taxa(url, filename):
    # download the website
    req = request_handler.Request(url, filename)
    req.load()
    
    soup = bs4.BeautifulSoup(req.response.text, "html.parser")
    
    # search for the child taxa section that contains all the names
    children = soup.find("dl", class_="child-taxa")
    
    # names with hierarchy tags (subfamily, genus, ...)
    dts = children.find_all("dt")
    
    # the real names
    dds = children.find_all("dd")
    
    if len(dts) != len(dds):
        raise Exception("Gather child taxa: dts / dds different length")
    
    print("Child taxa found:", len(dts))

    # return the zipped
    return zip(dts, dds)



# hierarchy tag should be "known" so it could be defined in an external file

def parse_html_taxa(taxa, hierarchy_tag, supertaxa):
    
    taxa_names = []
    
    for html_tag, html_name in taxa:
        
        current_hirerarchy_tag = html_tag.get_text()
        
        if current_hirerarchy_tag == hierarchy_tag :
            name = html_name.find("span", class_="name")
            if name:
                name = name.get_text()
            
            author = html_name.find("span", class_="author")
            if author:
                author = author.get_text()
            
                
            link = html_name.find("a")
            if link:
                link = link.get("href")
            
            supertaxa = supertaxa
            
            if name and author and link:
                taxa_names.append(Taxa.Taxa(name, author, link, supertaxa))
    
    return taxa_names

def generate_taxa_list(base_url, data_filename, hierarchy_tag, supertaxa):
    taxa_names = gather_child_taxa(base_url, data_filename)
    taxa_list = parse_html_taxa(taxa_names, hierarchy_tag, supertaxa)
    return taxa_list




def generate_lists(url, base_folder, filename_prefix, save_lists = True):
    
    # Gather the genuses
    
    genus_tag = "_genus"
    
    filename = os.path.join(base_folder, filename_prefix + genus_tag + "_website" + ".pickle")

    genus_list = generate_taxa_list(url, filename, "genus", None)
    
    if save_lists:
        list_filename = os.path.join(base_folder, filename_prefix + genus_tag + "_list" + ".mptaxa")
        Taxa.save_taxa_list(genus_list, list_filename)
    
    # Gather the species
        
    specie_tag = "_specie"
    
    uid = 1
    species_list = []
    for genus in genus_list:
        filename = os.path.join(base_folder, genus.name + specie_tag + "_" + str(uid) + ".pickle")
        url = NBN_HOME + "/" + genus.link
        
        species = generate_taxa_list(url, filename, "species", genus)
        
        for specie in species:
            species_list.append(specie)
            
        uid += 1
    
    if save_lists:
        list_filename = os.path.join(base_folder, filename_prefix + specie_tag + "_list" + ".mptaxa")
        Taxa.save_taxa_list(species_list, list_filename)
    
    
    return genus_list, species_list