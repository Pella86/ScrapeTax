# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 09:55:42 2020

@author: Media Markt
"""

import bs4
import os

import request_handler
import Taxa


NBN_HOME = "https://species.nbnatlas.org"   


def get_soup(url, filename):
    req = request_handler.Request(url, filename)
    req.load()
    return bs4.BeautifulSoup(req.response.text, "html.parser")




def gather_child_taxa(url, filename):
    
    soup = get_soup(url, filename)
    
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


def gather_taxonomy(url, filename):
    soup = get_soup(url, filename)
    children = soup.find("section", id="classification")
    
    dts = children.find_all("dt")
    dds = children.find_all("dd")

    html_parts = zip(dts, dds)
    
    species = []
    
    species.append({})
    
    for dt, dd in html_parts:
        if dt.text == "subspecies":
            subspecie_name = dd.find("span", class_="name").text.split(" ")[3]
            subspecie_author = dd.find("span", class_="author").text
            species.append({"subspecies" : subspecie_name, "author" : subspecie_author})
    

    for dt, dd in zip(dts, dds):
        if dt.text == "subspecies":
            continue
        
        for specie in species:
            name =  dd.find("span", class_="name").text
            
            if dt.text == "species":
                name = name.split(" ")[1]
            
            specie[dt.text] = name
        
    
    print(species)
        
    

    # tax_dict = {}
    
    # # check for subspecies
    
    # for dt, dd in zip(dts, dds):

    #   # dt.text is the tax category (genus, specie, family), while the 
    #   # dd is the name of the specie, genus and so on
      
      
    #   if dt.text == "subspecies":
    #       if tax_dict.get(dt.text) == None:
    #           tax_dict[dt.text] = []
    #       tax_dict[dt.text].append(dd.find("span", class_="name").text)
    #       print(dd.find("span", class_="author"))
    #       print("*"*79)
    #       print(tax_dict[dt.text])
    #   else:
    #       tax_dict[dt.text] = dd.find("span", class_="name").text
             
    return species


def create_authority_line(n_base, specie, base_path):
    print(f"Creating csv line for {specie}...")
    
    link = NBN_HOME + "/" + specie.link
    filename = os.path.join(base_path, "tax_" + specie.name.replace(" ", "_") + ".pickle")
    
    species = gather_taxonomy(link, filename)
     
    # add the author
    species[0]["author"] = specie.author
    
    elements = ["family", "subfamily", "tribe", "genus", "species", "subspecies", "InfraspecificRank", "Infraspecific Epitheth", "author"]
    
    
    lines = []
    
    for tax_dict in species:
    
        elements_list = []
            
        elestr = []
        for el in elements:
            sp = tax_dict.get(el)
            if sp:
                elestr.append(sp)
            else:
                elestr.append(" ")
                
        elements_list.append(elestr)
        
        print(elestr)
        
        
        # subspecies_n = tax_dict.get("subspecies")
        
        # if subspecies_n != None:
        #     for subsp in subspecies_n:
        #         elestr = []
        #         for el in elements:
                    
        #             sp = tax_dict.get(el)
        #             if sp != None:
        #                 if el == "species":
        #                     sp = sp.split(" ")[1]
                        
        #                 elif el == "subspecies":
        #                     sp = subsp.split(" ")[3]
        #                 elestr.append(sp)
        #             else:
        #                 elestr.append(" ")  
        #         elements_list.append(elestr)
    
      
        # get the author from the taxa
        line = ""
        for elestr in elements_list:
            
            line += str(n_base) + "\t"
            
            for i, el in enumerate(elestr):
                if i == len(elestr) - 1:
                    line += el
                else:
                    line += el + "\t"
            line += "\n"
            
            n_base += 1
        
        lines.append(line)
    
    return n_base, lines
        