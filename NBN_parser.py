# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 09:55:42 2020

@author: maurop
"""

import request_handler
import Taxa
import FileInfo


NBN_HOME = "https://species.nbnatlas.org"   


def gather_child_taxa(url, filename):
    '''Function that scans the web page and gathers the child taxa of the url'''
    
    soup = request_handler.get_soup(url, filename)
    
    # search for the child taxa section that contains all the names
    children = soup.find("dl", class_="child-taxa")
    
    # names with hierarchy tags (subfamily, genus, ...)
    dts = children.find_all("dt")
    
    # the real names
    dds = children.find_all("dd")
    
    if len(dts) != len(dds):
        raise Exception("Gather child taxa: dts / dds different length")
    
    print("Child taxa found:", len(dts))

    # return the zipped elements
    return zip(dts, dds)


class NBNElement:
    ''' Class that processes the informations inside the gathered taxa'''
    
    def __init__(self, html_rank, html_name, fileinfo):
        self.html_rank = html_rank
        self.html_name = html_name
        self.fileinfo = fileinfo
    
    def get_link(self):
        '''Method that gets the link from the name box'''
        link = self.html_name.find("a")
        if link:
            link = link.get("href")
            if link.startswith(NBN_HOME):
                return link
            else:
                return NBN_HOME + link
        else:
            return None  
    
    def get_name(self):
        '''Method that gets the name (e.g. '''
        return self.html_name.find("span", class_="name").text
    
    def get_rank(self):
        '''Method that gets the rank (specie, genus, ...) '''
        return self.html_rank.text
    
    # def generate_filename(self, base_folder, prefix):
    #     '''Method that generates the filename, same as generate_filename() 
    #     function, but uses the name found in the get_name() function'''
    #     return generate_filename(base_folder, prefix, self.get_name())

    def gather_child_elements(self):
        '''Method that gather the child elements from the page 
        pointed by the get_link() method'''
        if self.get_link():
            link = self.get_link()
            filename = self.fileinfo.pickle_filename(self.get_name())
            html_elements = gather_child_taxa(link, filename)
            
            return [NBNElement(dt, dd, self.fileinfo) for dt, dd in html_elements]
    
    def get_author(self):
        '''Method that gets the author name for the element'''
        author = self.html_name.find("span", class_="author")
        if author:
            return author.text
        else:
            return "author not found"


def generate_lists(family_name, fileinfo, save_lists = True):
    '''Function that arranges the genuses and species in a list, the function
    could be translated in a tree, but ... is difficult. The function returns
    a list of Taxa with name, author and reference link'''
    
    api_url = "https://species-ws.nbnatlas.org/search?"
    param = {}
    param["q"] = family_name
    param["fq"] = "idxtype:TAXON"
 
    req = request_handler.Request(api_url, fileinfo.pickle_filename("family_search"), param)
    req.load()
    
    # pick the first result
    search_json = req.get_json()
    
    family_guid = search_json["searchResults"]["results"][0]["guid"]
    
    family_url = "https://species.nbnatlas.org/species/" + family_guid
    
    
    filename = fileinfo.pickle_filename("family")
    
    taxa = gather_child_taxa(family_url, filename)
    
    genus_list = []
    species_list = []
    
    for dt, dd in taxa:
        
        element = NBNElement(dt, dd, fileinfo)
        
        if element.get_rank() == "subfamily":
            
            subfam = element.gather_child_elements()

            for subf in subfam:
                
                if subf.get_rank() == "tribe":
                    genuses = subf.gather_child_elements()
                    
                    for genus in genuses:
                        if genus.get_rank() == "genus":
                            name = genus.get_name()
                            author = genus.get_author()
                        
                            genus_list.append(Taxa.Taxa(name, author, genus.get_link(), "none"))
                
                if subf.get_rank() == "genus":
                    name = subf.get_name()
                    author = subf.get_author()
                    
                    genus_list.append(Taxa.Taxa(name, author, subf.get_link(), "none"))
        
        if element.get_rank() == "genus":
            name = element.get_name()
            author = element.get_author()
            
            genus_list.append(Taxa.Taxa(name, author, element.get_link(), "none"))
                              
    for genus in genus_list:
        
        filename = fileinfo.pickle_filename(f"{genus.name}_webpage")
        html_elements = gather_child_taxa(genus.link, filename)
        
        for dt, dd in html_elements:
            specie = NBNElement(dt, dd, fileinfo)            
            
            taxa = Taxa.Taxa(specie.get_name(), specie.get_author(), specie.get_link(), genus)
            species_list.append(taxa)

    if save_lists:

        list_filename = fileinfo.mptaxa_filename("genus_list")
        Taxa.save_taxa_list(genus_list, list_filename)
        
        list_filename = fileinfo.mptaxa_filename("species_list")
        Taxa.save_taxa_list(species_list, list_filename)
        
    return genus_list, species_list

def gather_taxonomy(url, filename):
    ''' Function that scraps the taxonomy of a specie,
    it searches in the classification section the various ranks, and groups
    them in a dictionary. The function gathers the data for the subspecies too.
    returns a list of dictionaries where the first element is the specie and is
    always present, the other elements are subspecies in case they exist'''
    
    # find ranks and the name associated
    soup = request_handler.get_soup(url, filename)
    children = soup.find("section", id="classification")
    
    dts = children.find_all("dt")
    dds = children.find_all("dd")

    html_parts = zip(dts, dds)
    
    # compiles the specie + subspecie list
    species = []
    
    species.append({})
    
    # find the subspecie and append the eventual subspecie name and author
    
    for dt, dd in html_parts:
        if dt.text == "subspecies":
            subspecie_name = dd.find("span", class_="name").text.split(" ")[3]
            subspecie_author = dd.find("span", class_="author").text
            species.append({"subspecies" : subspecie_name, "author" : subspecie_author})
    
    # fill in the dictionary the rest of the taxonomy
    for dt, dd in zip(dts, dds):
        if dt.text == "subspecies":
            continue
        
        for specie in species:
            name =  dd.find("span", class_="name").text
            
            if dt.text == "species":
                name = name.split(" ")[1]
            
            specie[dt.text] = name

    return species

def generate_species_dictionary(species_list, fileinfo):
    species_dicts = []
    
    for specie in species_list:
        # get the specie link, is the member .link of the Taxa class
        link = specie.link
        if not link.startswith(NBN_HOME):
            link = NBN_HOME + "/" + specie.link
              
        filename = fileinfo.pickle_filename(specie.name.replace(" ", "_"))
        species = gather_taxonomy(link, filename)
         
        # add the author of the specie which is still not in the dictionary
        species[0]["author"] = specie.author   
    
        species_dicts += species
    return species_dicts
    
            

if __name__ == "__main__":


#    # Test the csv file construction
#    
#    # to do
#    # - manage the authors for the subspecie
#    # - move the non NBN specific functions to this file
#    
#    # load a specie taxa file
#    
#    # base_path = "./Data/Libellulidae"
#    # family_url = "https://species.nbnatlas.org/species/NBNSYS0000160307" 
#    # prefix = "libellulidae"
#
#    # base_path = "./Data/Psychidae"
#    # family_url = "https://species.nbnatlas.org/species/NBNSYS0000160829" 
#    # prefix = "psychidae"
#
#    base_path = "./Data/Vespidae"
#    family_url = "https://species.nbnatlas.org/species/NBNSYS0000050803" 
#    prefix = "vespidae"
#
#    # base_path = "./Data/Mycetophilidae"
#    # family_url = "https://species.nbnatlas.org/species/NBNSYS0000160474" 
#    # prefix = "mycetophilidae"   
#    
#    # base_path = "./Data/Formicidae"
#    # family_url = "https://species.nbnatlas.org/species/NBNSYS0000037030" 
#    # prefix = "formicidae"     
#    
#    # load family home page
#    print("NBN_parser")
#    
#    base_folder = "./Data/Psychidae"
#    prefix = "psychidae"
#    url = "https://species.nbnatlas.org/species/NBNSYS0000160829"
#    
#    fileinfo = FileInfo.FileInfo(base_folder, prefix)
#    
#    genus_list, species_list = generate_lists(url, fileinfo)
#    spec_dict = generate_species_dictionary(species_list, fileinfo)
#    
#    
#    print(len(genus_list), len(spec_dict))
    
    
    base_folder = "./Data/NBN_test"
    prefix = "vespidae"
    
    fi = FileInfo.FileInfo(base_folder, prefix)
    
    
    family_name = "Vespidae"
    
    genus_list, specie_list = generate_lists(family_name, fi)
    

        
                                      
            
            
    
            
                       
                            