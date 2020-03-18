# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 09:55:42 2020

@author: Media Markt
"""

import bs4
import pickle

import request_handler
import Taxa


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
        
        if current_hirerarchy_tag == hierarchy_tag:
            name = html_name.find("span", class_="name").get_text()
            author = html_name.find("span", class_="author").get_text()
            link = html_name.find("a").get("href")
            supertaxa = supertaxa
            
            taxa_names.append(Taxa.Taxa(name, author, link, supertaxa))
    
    return taxa_names

def generate_taxa_list(base_url, data_filename, hierarchy_tag, supertaxa):
    taxa_names = gather_child_taxa(base_url, data_filename)
    taxa_list = parse_html_taxa(taxa_names, hierarchy_tag, supertaxa)
    return taxa_list

def save_taxa_list(taxa_list, filename):
    with open(filename, "wb") as f:
        pickle.dump(taxa_list, f)
    
def laod_taxa_list(filename):
    with open(filename, "rb") as f:
        data = pickle.load(f)
    return data