# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 09:55:42 2020

@author: maurop
"""

import request_handler
import Taxa
import FileInfo
import ProgressBar


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
        '''Method that gets the name (e.g. Boletina plana)'''
        return self.html_name.find("span", class_="name").text
    
    def get_rank(self):
        '''Method that gets the rank (specie, genus, ...) '''
        return self.html_rank.text

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
            return author.text.strip()
        else:
            return "author not found"


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
    
    # parameters for the webpage corresponding to the family
    family_url = "https://species.nbnatlas.org/species/" + family_guid
    
    filename = fileinfo.pickle_filename("family")
    
    taxa = gather_child_taxa(family_url, filename)
    
    
    # start getting the speceis
    genus_list = []
    species_list = []
    
    pwheel = ProgressBar.ProgressWheel()
    
    
    for dt, dd in taxa:
        
        fam_taxa = Taxa.Taxa()
        fam_taxa.family = family_name
        
        fam_taxa.rank = Taxa.Taxa.rank_genus
        fam_taxa.source = "n"
        
        pwheel.draw_symbol()
        
        element = NBNElement(dt, dd, fileinfo)
        
        if element.get_rank() == "subfamily":
            
            subfam = element.gather_child_elements()

            for subf in subfam:
                
                subfam_taxa = Taxa.Taxa()
                subfam_taxa.copy_taxa(fam_taxa)
                subfam_taxa.subfamily = element.get_name()
                
                if subf.get_rank() == "tribe":
                    genuses = subf.gather_child_elements()
                    
                    for genus in genuses:
                        if genus.get_rank() == "genus":
                            
                            taxa = Taxa.Taxa()
                            taxa.copy_taxa(subfam_taxa)
                            
                            taxa.author = genus.get_author()
                            taxa.genus = genus.get_name()
                            taxa.links.append(genus.get_link())
                            taxa.tribe = subf.get_name()
                            
                            genus_list.append(taxa)
                
                if subf.get_rank() == "genus":
                    
                    taxa = Taxa.Taxa()
                    taxa.copy_taxa(subfam_taxa)

                    taxa.author = genus.get_author()
                    taxa.genus = genus.get_name()
                    taxa.links.append(genus.get_link())
                    
                    genus_list.append(taxa)
        
        if element.get_rank() == "genus":
            taxa = Taxa.Taxa()
            taxa.copy_taxa(fam_taxa)

            taxa.author = element.get_author()
            taxa.genus = element.get_name()
            taxa.links.append(element.get_link())
            
            genus_list.append(taxa)        
                      
    for genus in genus_list:
        pwheel.draw_symbol()
        
        filename = fileinfo.pickle_filename(f"{genus.genus}_webpage")

        html_elements = gather_child_taxa(genus.links[0], filename)
        
        for dt, dd in html_elements:
            specie = NBNElement(dt, dd, fileinfo)            

            taxa = Taxa.Taxa()
            taxa.copy_taxa(genus)
           
            taxa.author = specie.get_author()
            taxa.specie = specie.get_name().replace(genus.genus, "").strip()
            taxa.rank = Taxa.Taxa.rank_specie
            taxa.links.append(specie.get_link())
            
            species_list.append(taxa)
            
            # find subspecies somehow
            soup = request_handler.get_soup(taxa.links[0], fileinfo.pickle_filename(taxa.specie))
            children = soup.find("section", id="classification")
            
            if children:
            
                dts = children.find_all("dt")
                dds = children.find_all("dd")
            
                html_parts = zip(dts, dds)
                
                # compiles the specie + subspecie list
                species = []
                
                species.append({})
                
                # find the subspecie and append the eventual subspecie name and author
                
                for dth, ddh in html_parts:
                    if dth.text == "subspecies":
                        subspecie_name = ddh.find("span", class_="name").text.split(" ")[3]
                        subspecie_author = ddh.find("span", class_="author").text
                        species.append({"subspecies" : subspecie_name, "author" : subspecie_author})  
                        
                        staxa = Taxa.Taxa()
                        staxa.copy_taxonomy(taxa)
                        
                        staxa.author = ddh.find("span", class_="author").text
                        staxa.subspecie = ddh.find("span", class_="name").text.split(" ")[3]
                        
                        staxa.rank = Taxa.Taxa.rank_subspecie
                        staxa.links.append(specie.get_link())
                        staxa.source = "n"
                        
                        species_list.append(staxa)
                    
    
    pwheel.end()
    
    if save_lists:

        list_filename = fileinfo.mptaxa_filename("genus_list")
        Taxa.save_taxa_list(genus_list, list_filename)
        
        list_filename = fileinfo.mptaxa_filename("species_list")
        Taxa.save_taxa_list(species_list, list_filename)
        
    return genus_list, species_list

    
            

if __name__ == "__main__":
    
    base_folder = "./Data/NBN_test"
    family_name = "Vespidae"
    
    fi = FileInfo.FileInfo(base_folder, "nbn", family_name)
    
    genus_list, specie_list = generate_lists(family_name, fi)
    
    
    for genus in genus_list:
        print(genus)
    
    for specie in specie_list:
        specie.print_extended()
    
    

        
                                      
            
            
    
            
                       
                            