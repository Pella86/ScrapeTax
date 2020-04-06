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

    # return the zipped
    return zip(dts, dds)


def generate_filename(base_folder, prefix, name):
    filename = f"{prefix}_{name}_webpage.pickle" 
    return os.path.join(base_folder, filename)

class NBNElement:
    
    
    def __init__(self, dt, dd):
        self.html_rank = dt
        self.html_name = dd
    
    def get_link(self):
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
        return self.html_name.find("span", class_="name").text
    
    def get_rank(self):
        return self.html_rank.text
    
    def generate_filename(self, base_folder, prefix):
        return generate_filename(base_folder, prefix, self.get_name())

    def gather_child_elements(self, base_folder, prefix):
        if self.get_link():
            link = self.get_link()
            filename = self.generate_filename(base_folder, prefix )
            html_elements = gather_child_taxa(link, filename)
            return [NBNElement(dt, dd) for dt, dd in html_elements]
    
    def get_author(self):
        author = self.html_name.find("span", class_="author")
        if author:
            return author.text
        else:
            return "author not found"





def generate_lists(family_url, base_folder, prefix, save_lists = True):
    
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
    soup = request_handler.get_soup(url, filename)
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


             
    return species


def create_authority_line(n_base, specie, base_path):
    print(f"Creating csv line for {specie}...")
    
    link = specie.link
    if not link.startswith(NBN_HOME):
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


# def get_rank(dt):
#     return dt.text

# def get_link(dd):
#     link = dd.find("a")
#     if link:
#         return NBN_HOME + link.get("href")
#     else:
#         return None
    
# def get_name(dd):
#     return dd.find("span", class_="name").text


# def get_species_tags(tdt, tdd, base_folder, prefix):
#     if get_rank(tdt) == "genus":
#         link = get_link(tdd)
#         if link:
#             name = get_name(tdd)
#             filename = generate_filename(base_folder, prefix, name)    
#             return gather_child_taxa(link, filename)
        
        

    
    
            

if __name__ == "__main__":
    # load family home page
    print("NBN_parser")
    
    base_folder = "./Data/Psychidae"
    prefix = "psychidae"
    
    url = "https://species.nbnatlas.org/species/NBNSYS0000160829"
    
    genus_list, species_list = generate_lists(url, base_folder, prefix)
    
    n = 1
    for specie in species_list:
        n, line = create_authority_line(n, specie, base_folder)
        
        print(line)
        
                                      
            
            
            
    
    
    
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
            
                       
                            