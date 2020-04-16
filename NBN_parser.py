# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 09:55:42 2020

@author: Media Markt
"""


import os
import request_handler
import Taxa


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


def generate_filename(base_folder, prefix, name):
    ''' Function that generates a filename given a prefix and a base folder'''
    name = name.replace(" ", "_")
    filename = f"{prefix}_{name}_webpage.pickle" 
    return os.path.join(base_folder, filename)

class NBNElement:
    ''' Class that processes the informations inside the gathered taxa'''
    
    def __init__(self, html_rank, html_name):
        self.html_rank = html_rank
        self.html_name = html_name
    
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
    
    def generate_filename(self, base_folder, prefix):
        '''Method that generates the filename, same as generate_filename() 
        function, but uses the name found in the get_name() function'''
        return generate_filename(base_folder, prefix, self.get_name())

    def gather_child_elements(self, base_folder, prefix):
        '''Method that gather the child elements from the page 
        pointed by the get_link() method'''
        if self.get_link():
            link = self.get_link()
            filename = self.generate_filename(base_folder, prefix )
            html_elements = gather_child_taxa(link, filename)
            return [NBNElement(dt, dd) for dt, dd in html_elements]
    
    def get_author(self):
        '''Method that gets the author name for the element'''
        author = self.html_name.find("span", class_="author")
        if author:
            return author.text
        else:
            return "author not found"





def generate_lists(family_url, base_folder, prefix, save_lists = True):
    '''Function that arranges the genuses and species in a list, the function
    could be translated in a tree, but ... is difficult. The function returns
    a list of Taxa with name, author and reference link'''
    
    filename = generate_filename(base_folder, prefix, "family")
    
    taxa = gather_child_taxa(family_url, filename)
    
    genus_list = []
    species_list = []
    
    for dt, dd in taxa:
        
        element = NBNElement(dt, dd)
        
        if element.get_rank() == "subfamily":
            
            subfam = element.gather_child_elements(base_folder, prefix)

            for subf in subfam:
                
                if subf.get_rank() == "tribe":
                    genuses = subf.gather_child_elements(base_folder, prefix)
                    
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
        
        filename = os.path.join(base_folder, f"{prefix}_{genus.name}_webpage.pickle")
        
        html_elements = gather_child_taxa(genus.link, filename)
        
        for dt, dd in html_elements:
            specie = NBNElement(dt, dd)            
            
            taxa = Taxa.Taxa(specie.get_name(), specie.get_author(), specie.get_link(), genus)
            species_list.append(taxa)

    if save_lists:
        list_filename = os.path.join(base_folder, f"{prefix}_genus_list.mptaxa")
        Taxa.save_taxa_list(genus_list, list_filename)
        
        list_filename = os.path.join(base_folder,f"{prefix}_species_list.mptaxa")
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

def generate_species_dictionary(species_list, base_path, prefix):
    species_dicts = []
    
    for specie in species_list:
        # get the specie link, is the member .link of the Taxa class
        link = specie.link
        if not link.startswith(NBN_HOME):
            link = NBN_HOME + "/" + specie.link
              
        filename = generate_filename(base_path, "tax_", specie.name)
        species = gather_taxonomy(link, filename)
         
        # add the author of the specie which is still not in the dictionary
        species[0]["author"] = specie.author   
    
        species_dicts += species
    return species_dicts


# def create_authority_lines(species_dicts):
#     elements = ["family", "subfamily", "tribe", "genus", "species",
#                 "subspecies", "InfraspecificRank", "Infraspecific Epitheth",
#                 "author"]
    
#     # create the lines based on the above defined elements
#     lines = []
#     sep = ","
    
#     for n, tax_dict in enumerate(species_dicts):
    
#         elements_list = []
         
#         # creates the string based on the element if it exist, else put a space
#         elestr = []
#         for el in elements:
#             sp = tax_dict.get(el)
#             if sp:
#                 elestr.append(sp)
#             else:
#                 elestr.append(" ")
                
#         elements_list.append(elestr)
    
      
#         # get the author from the taxa
#         line = ""
#         for elestr in elements_list:
            
#             line += str(n + 1) + sep
            
#             for i, el in enumerate(elestr):
#                 if el.find(" ") >= 0:
#                     el = f'"{el}"'
                
#                 if i == len(elestr) - 1:
#                     line += el
#                 else:
#                     line += el + sep
#             line += "\n"
        
#         lines.append(line)
    
#     return lines    
    

# def create_authority_line(n_base, specie, base_path):
#     '''Function that creates the line for the authority file, this function
#     returns a list of string corresponding to a row of the excel file'''
    
#     print(f"Creating csv line for {specie}...")
    
#     # get the specie link, is the member .link of the Taxa class
#     link = specie.link
#     if not link.startswith(NBN_HOME):
#         link = NBN_HOME + "/" + specie.link
          
#     filename = generate_filename(base_path, "tax_", specie.name)
#     species = gather_taxonomy(link, filename)
     
#     # add the author of the specie which is still not in the dictionary
#     species[0]["author"] = specie.author
    
#     elements = ["family", "subfamily", "tribe", "genus", "species",
#                 "subspecies", "InfraspecificRank", "Infraspecific Epitheth",
#                 "author"]
    
#     # create the lines based on the above defined elements
#     lines = []
#     sep = ","
    
#     for tax_dict in species:
    
#         elements_list = []
         
#         # creates the string based on the element if it exist, else put a space
#         elestr = []
#         for el in elements:
#             sp = tax_dict.get(el)
#             if sp:
#                 elestr.append(sp)
#             else:
#                 elestr.append(" ")
                
#         elements_list.append(elestr)
    
      
#         # get the author from the taxa
#         line = ""
#         for elestr in elements_list:
            
#             line += str(n_base) + sep
            
#             for i, el in enumerate(elestr):
#                 if el.find(" ") >= 0:
#                     el = f'"{el}"'
                
#                 if i == len(elestr) - 1:
#                     line += el
#                 else:
#                     line += el + sep
#             line += "\n"
            
#             n_base += 1
        
#         lines.append(line)
    
#     return n_base, lines

    
            

if __name__ == "__main__":


    # Test the csv file construction
    
    # to do
    # - manage the authors for the subspecie
    # - move the non NBN specific functions to this file
    
    # load a specie taxa file
    
    # base_path = "./Data/Libellulidae"
    # family_url = "https://species.nbnatlas.org/species/NBNSYS0000160307" 
    # prefix = "libellulidae"

    # base_path = "./Data/Psychidae"
    # family_url = "https://species.nbnatlas.org/species/NBNSYS0000160829" 
    # prefix = "psychidae"

    base_path = "./Data/Vespidae"
    family_url = "https://species.nbnatlas.org/species/NBNSYS0000050803" 
    prefix = "vespidae"

    # base_path = "./Data/Mycetophilidae"
    # family_url = "https://species.nbnatlas.org/species/NBNSYS0000160474" 
    # prefix = "mycetophilidae"   
    
    # base_path = "./Data/Formicidae"
    # family_url = "https://species.nbnatlas.org/species/NBNSYS0000037030" 
    # prefix = "formicidae"     
    
    # load family home page
    print("NBN_parser")
    
    base_folder = "./Data/Psychidae"
    prefix = "psychidae"
    url = "https://species.nbnatlas.org/species/NBNSYS0000160829"
    
    genus_list, species_list = generate_lists(url, base_folder, prefix)
    spec_dict = generate_species_dictionary(species_list, base_path, prefix)
    lines = create_authority_lines(spec_dict)
    
    for line in lines:
        print(lines)

        
                                      
            
            
            
    
    
    
    # tags = gather_child_taxa(url, filename)

    # species_list = []

    # for dt, dd in tags:
        
    #     if get_rank(dt) == "subfamily":
    #         link = get_link(dd)
    #         if link:
    #             name = get_name(dd)
    #             filename = generate_filename(base_folder, prefix, name)
                
    #             sub_tags = gather_child_taxa(link, filename)
                
    #             for sdt, sdd in sub_tags:
                    
    #                 if get_rank(sdt) == "tribe":
    #                     link = get_link(sdd)
    #                     if link:
    #                         name = get_name(sdd)
    #                         filename = generate_filename(base_folder, prefix, name)
                            
    #                         tribe_tags = gather_child_taxa(link, filename)
                            
    #                         for tdt, tdd in tribe_tags:
                                
    #                             if get_rank(tdt) == "genus":
    #                                 link = get_link(tdd)
    #                                 if link:
    #                                     name = get_name(tdd)
    #                                     filename = generate_filename(base_folder, prefix, name)
                            
    #                                     genus_tags = gather_child_taxa(link, filename)
                                        
    #                                     for gdt, gdd in genus_tags:
                                            
    #                                         link = get_link(gdd)
                                            
    #                                         if link:
    #                                             name = get_name(gdd)
    #                                             species = gather_taxonomy(link, generate_filename(base_folder, prefix, name))
                                                
    #                                             print(species)
                                            
                                                           
                                    
                                    
                    
                
                
            
    
    
    # soup = get_soup(url, filename)
    
    # # search for the child taxa section that contains all the names
    # children = soup.find("dl", class_="child-taxa")
    
    # # names with hierarchy tags (subfamily, genus, ...)
    # dts = children.find_all("dt")
    
    # # the real names
    # dds = children.find_all("dd")

    
    # ranks = ["unranked", "kingdom", "phylum", "subphylum", "class", "order", "family", "subfamily", "tribe", "genus", "species"]
    
    # subfamily_count = 0
    # tribe_count = 0
    
    
    # species_list = ""
    
    
    # genus_list = []
    
    # for dt, dd in zip(dts, dds):

    #     if dt.text == "subfamily":
    #         slink = dd.find("a")
            
    #         if slink:
    #             slink = slink.get("href")
    #             name = dd.find("span", class_="name").text
                
    #             subfamily_count += 1

    #             tags = gather_child_taxa(NBN_HOME + slink, os.path.join(base_folder, prefix + "_" + name + "_" + str(subfamily_count) + ".pickle" ))
                
                
                
    #             for sdt, sdd in tags:
    #                 print("-"*79)
                    
    #                 if sdt.text == "tribe":
    #                     tlink = sdd.find("a")
    #                     if tlink:
    #                         tlink = tlink.get("href")
                            
    #                         name = sdd.find("span", class_="name").text
    #                         print(name)
                            
    #                         tribe_tags = gather_child_taxa(NBN_HOME + tlink, os.path.join(base_folder, prefix + "_" + name + "_" + str(tribe_count) + ".pickle" ))
                            
    #                         for tdt, tdd in tribe_tags:
    #                             print(tdt.text + ": " + tdd.find("span", class_="name").text)
        
    #     if dt.text == "genus":
    #         link = dd.find("a").get("href")
    #         pass
            
                       
                            