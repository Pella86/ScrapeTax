#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 09:21:27 2020

@author: maurop
"""
# =============================================================================
# Imports
# =============================================================================

import os

import NBN_parser
import CreateHTMLFile
import CreateLabelTable
import EncyclopediaOfLife
import Chrysis_net
import Taxa

# =============================================================================
#  Function to create the authority list    
# =============================================================================

def generate_authority_list(genus_list, species_list, base_folder, prefix):
    
    fhtml = CreateHTMLFile.CreateHTMLFile()
    # add date of creation and how many taxas are in the file
    # maybe add the possibility to save the generate tree for later use?
    # could be useless since it will be not modifiable
    
    fhtml.add_element("--- Genuses ---")
    fhtml.add_line_break()
    
    for genus in genus_list:
        fhtml.add_italics_element(genus.name)
        fhtml.add_element(", ")
        fhtml.add_element(genus.author)
        fhtml.add_line_break()

    fhtml.add_element("--- Species ---")
    fhtml.add_line_break()
    
    for specie in species_list:
        fhtml.add_italics_element(specie.name)
        fhtml.add_element(", ")
        fhtml.add_element(specie.author)
        fhtml.add_line_break()
    
    
    fhtml.generate_html_file(os.path.join(base_folder, prefix + "_species_list.html"))

# =============================================================================
# Function to create the authority file
# =============================================================================

def create_authority_lines(species_dicts):
    ''' function that given a list of taxonomic dictionary of species creates
    a line of the authority file separated and formatted (utf-8). The file can
    be imported in excel'''
    
    # elements to be included in the file
    elements = ["family", "subfamily", "tribe", "genus", "species",
                "subspecies", "InfraspecificRank", "Infraspecific Epitheth",
                "author"]
    
    # Data will be comma separated
    separator = ","
    
    # create the lines based on the above defined elements
    lines = []
    
    
    for n, tax_dict in enumerate(species_dicts):
        
        # taxonomical names in order of how they are in the authority file
        elements_list = []
         
        # creates the string based on the rank if  the rank exists
        # else puts a space
        taxonomical_names = []
        for tax_rank in elements:
            tax_name = tax_dict.get(tax_rank)
            if tax_name:
                taxonomical_names.append(tax_name)
            else:
                taxonomical_names.append(" ")
                
        elements_list.append(taxonomical_names)
    
      
        # Compose the line from the elements
        line = ""
        for taxonomical_names in elements_list:
            
            # creates the line enumerating the species
            # it inserts a Excel formula so that is easier to remove rows
            if n == 0:
                line += "1" + separator     
            else:
                line += f"= A{n + 1} + 1" + separator
                
            
            # attach to the line the corresponding names
            for i, tax_name in enumerate(taxonomical_names):
                # if the name has spaces surround it with "
                if tax_name.find(" ") >= 0:
                    tax_name = f'"{tax_name}"'
                
                # if is the last element dont put the separator
                if i == len(taxonomical_names) - 1:
                    line += tax_name
                else:
                    line += tax_name + separator
            line += "\n"
        
        lines.append(line)
    
    return lines    
    
def save_authority_file(filename, species_dict):
    csv_file = " ,Family,Subfamily,Tribe,Genus,SpecificEpithet,SubspecificEpithet,InfraspecificRank,InfraspecificEpithet,Authorship\n".encode("utf8")
    lines = create_authority_lines(species_dict)
    for line in lines:
        csv_file += line.encode("utf8")
    
    with open(filename, "wb") as f:
        f.write(csv_file)

# def generate_authority_file(family_url, base_path, prefix, source):
      
#     if source == "NBN_Atlas":
#         _, species_list = NBN_parser.generate_lists(family_url, base_path, prefix)
#         spec_dict = NBN_parser.generate_species_dictionary(species_list, base_path, prefix)
        
#     elif source == "EOL":
#         _, species_list = EncyclopediaOfLife.generate_lists(family_url, base_path, prefix)
#         spec_dict = EncyclopediaOfLife.generate_specie_dictionary(species_list, family_url)
             
#     csv_filename = os.path.join(base_path, prefix + "_authority_file.csv")
        
#     save_authority_file(csv_filename, spec_dict)


def generate_authority_file(species_dict, base_path, prefix):
      
    csv_filename = os.path.join(base_path, prefix + "_authority_file.csv")
        
    save_authority_file(csv_filename, species_dict)

# =============================================================================
# Main 
# =============================================================================
 
PRODUCTION = False   

def get_input(title, input_sentence, default = None):
    print("-" * 79)
    print(title)
    choice = input(input_sentence + " >")
    if choice == "":
        choice = default
    return choice
 
    
def prod_main():    
    print("Scrape Tax")
    print("Program to gather informations from online databases about species and genuses")
    
        
    base_folder = get_input("The path to the folder where the file will be saved, the folder must already exist. Use dot (.) to access the current folder",
                            "path",
                            "./Data/Vespidae")
    
    
    prefix = get_input("Chose a prefix to name the files",
                       "prefix",
                       "vespidae")
    
    url = get_input("Paste the url of the family of the https://nbnatlas.org/ search result",
                    "website link",
                    "https://nbnatlas.org/species/NBNSYS0000050803")
        
    
    exit_command = False
    
    while not exit_command:
        print("What you would like to do?")
        print("  1. Generate authority list")
        print("  2. Generate label table")
        print("  3. Create csv authority file")
        print("  4. Exit (e, exit, quit)")
        
        
        choice = input("pick a number >")
        
        if choice == "e" or choice == "exit" or choice == "quit" or choice == "4":
            exit_command = True
        else:
            try:
                choice = int(choice)
            except ValueError:
                print("not a value from 1 to 3")
                choice = None 
            
            if choice == 1:
                print("Generating authority list")
    
                genus_list, species_list = NBN_parser.generate_lists(url, base_folder, prefix)
                generate_authority_list(genus_list, species_list, base_folder)  
                
                exit_command = True
            
            elif choice == 2:
                print("Generating label table")
                _, species_list = NBN_parser.generate_lists(url, base_folder, prefix)
                
                table = CreateLabelTable.LabelTable()
                
                table.create_table(species_list,
                                   os.path.join(base_folder,
                                                prefix + "_label_table.html"
                                                )
                                   )
                
                exit_command = True
                
            elif choice == 3:
                print("Generating authority file")
                generate_authority_file(url, base_folder, prefix, "NBN_Atlas")
                   
            else:
                print("Choice not available")
                exit_command = True
    

if __name__ == "__main__":
    if PRODUCTION:
        prod_main()
    else:

        base_folder = "./Data/Formicidae"
        url = "https://species.nbnatlas.org/species/NBNSYS0000037030" 
        prefix = "formicidae"          

        # genus_list, species_list = NBN_parser.generate_lists(url, base_folder, prefix)
        # generate_authority_list(genus_list, species_list, base_folder, prefix)  
        

        # _, species_list = NBN_parser.generate_lists(url, base_folder, prefix)
        
        # table = CreateLabelTable.LabelTable()
        
        # table.create_table(species_list,
        #                    os.path.join(base_folder,
        #                                 prefix + "_label_table.html"
        #                                 )
        #                    )

        #generate_authority_file(url, base_folder, prefix, "NBN_Atlas")
        
        family = "Chrysididae"
        prefix = family.lower()

        base_folder = "./Data/Chrysididae"
        
        # NBN_Atlas
        
        url = "https://species.nbnatlas.org/species/NBNSYS0000159685"

        # _, species_list_nbn = NBN_parser.generate_lists(url, base_folder, prefix)
        # spec_dict = NBN_parser.generate_species_dictionary(species_list_nbn, base_folder, prefix)
        
        # generate_authority_file(spec_dict, base_folder, "nbn_" + prefix)

        # # EOL
 
        # _, species_list_eol = EncyclopediaOfLife.generate_lists(family, base_folder, prefix)
        # spec_dict = EncyclopediaOfLife.generate_specie_dictionary(species_list_eol, family)
        
        # generate_authority_file(spec_dict, base_folder, "eol_" + prefix)
        
        # # Chrysis net
        # _, species_list_chr = Chrysis_net.generate_lists(base_folder, prefix)
        # spec_dict = Chrysis_net.generate_specie_dictionary(species_list_chr)
        
        # generate_authority_file(spec_dict, base_folder, "chr_" + prefix)
        
        _, species_list_nbn = NBN_parser.generate_lists(url, base_folder, prefix)
        _, species_list_eol = EncyclopediaOfLife.generate_lists(family, base_folder, prefix)
        _, species_list_chr = Chrysis_net.generate_lists(base_folder, prefix)
        print(len(species_list_nbn), len(species_list_eol), len(species_list_chr))
        
        
        csv = '"Present in","NBN Atlas","EOL Database","Chrysis.net"\n'
        
        complete_list = []
        
        for nbn_specie in species_list_nbn:
            complete_list.append(nbn_specie)
            
        for eol_specie in species_list_eol:
            if eol_specie.name in [sp.name for sp in complete_list]:
                continue
            else:
                complete_list.append(eol_specie)
            
        for chr_specie in species_list_chr:
            if chr_specie.name in [sp.name for sp in complete_list]:
                continue
            else:
                complete_list.append(chr_specie)
        complete_list.sort(key= lambda item : item.name)  
        
        lines = ""
        for sp in complete_list:
            line = f'"{sp.name}",'
            
            if sp.name in [s.name for s in species_list_nbn]:
                line += "x,"
            else:
                line += ","
                    
            if sp.name in [s.name for s in species_list_eol]:
                line += "x,"
            else:
                line += ","                    
                    
            if sp.name in [s.name for s in species_list_chr]:
                line += "x"
            else:
                line += ""
            
            lines += line + "\n"
                
        csv += lines
                
        filename = os.path.join(base_folder, "list_compare.csv")
        
        with open(filename, "wb") as f:
            f.write(csv.encode("utf8"))
        
        
        
# =============================================================================
# Old stuff
# =============================================================================
  

# =============================================================================
#  Generate the lists
# =============================================================================

# url = nbn_home +  '/species/NBNSYS0000050803#classification'
# base_folder = "./Data/Vespidae"
# prefix = "vespidae"

# # the url of a family on the NBN Atlas
# url = nbn_home + '/species/NBNSYS0000160474'
# # the folder on the pc were the data will be saved
# base_folder = "./Data/Mycetophilidae"
# # the prefix for the files to be saved
# prefix = "mycetophilidae"

# genus_list, species_list = NBN_parser.generate_lists(url, base_folder, prefix)
    
# generate_authority_list(genus_list, species_list, base_folder)


      
# base_folder = "./Data/Vespidae/"

# nbn_home = "https://species.nbnatlas.org"   
        
# #nbn_myceto = nbn_home + '/species/NBNSYS0000160474#names'
# nbn_myceto = nbn_home +  '/species/NBNSYS0000050803#classification'


# url = nbn_myceto
# filename = "./Data/Vespidae/nbn_vespidae.pickle"

# genus_names = NBN_parser.gather_child_taxa(url, filename)

# genus_list = NBN_parser.parse_html_taxa(genus_names, "genus", "Vespidae")

# print(genus_list)

# for genus in genus_list:
#     print(genus)
    
#     start = genus.link.rfind("/")
#     end = genus.link.find("#")
#     filename = os.path.join(base_folder, genus.link[start+1:end] + ".pickle")
    
#     species_names = NBN_parser.gather_child_taxa(nbn_home + genus.link, filename)
    
#     species_list = NBN_parser.parse_html_taxa(species_names, "species", genus)       

# for genus in genus_list:
#     print(genus.name, end=', ')

#     start = genus.link.rfind("/")
#     end = genus.link.find("#")
#     filename = genus.link[start+1:end] + ".pickle"   
    
#     species_names = gather_child_taxa(nbn_home + genus.link, filename)
    
#     species_list = parse_html_taxa(species_names, "species")    
    
    


# genus = genus_list[0]

# print(genus)
# print(genus.link)

# start = genus.link.rfind("/")
# end = genus.link.find("#")
# filename = genus.link[start+1:end] + ".pickle"     

# print(filename)


# species_names = gather_child_taxa(nbn_home + genus.link, filename)

# species_list = parse_html_taxa(species_names, "species")


# for specie in species_list:
#     print(specie)



# cl = name_formatting.LabelsTable()

# cl.generate_table(species_list)
# cl.generate_html("myceto_lables_test.html")
            


#print("Compose genus list")        
#
#genus_list = []
#
#for hierarchy_name, dd in genus_names:
#    name = dd.find("span", class_="name")
#    author = dd.find("span", class_="author")
#    link = dd.find("a")
#    
#    if hierarchy_name.get_text() == "genus":
#        genus = GenusNBN(name.get_text(), author.get_text(), link.get("href"))
#        genus_list.append(genus)
#
#with open("myceto species.txt", "w") as f:
#    for genus in genus_list:
#        print(genus)
#        print(genus.link)
#        
#        # visit the pages corresponding to the genus and extract the species
#        start = genus.link.find("NBN")
#        end = genus.link.find("#")
#        filename = genus.link[start:end] + ".pickle"
#        
#        species_names = gather_child_taxa(nbn_home + genus.link, filename)
#        
#        print(species_names)
#        
#        
#        for hierarchy_name, info in species_names:
#            print("------------")
#            
#            name = info.find("span", class_="name")
#            author = info.find("span", class_="author")
#            
#            if hierarchy_name.get_text() == "species":
#                if name is not None and author is not None:
#                    print(name.get_text(), author.get_text())
#                    f.write( name.get_text() + " " + author.get_text() + "\n")



# =============================================================================
# Previous shit
# =============================================================================

        
#class Genus:
#    
#    def __init__(self, name, author):
#        self.name = str(name)
#        self.author = str(author)
#        
#    def __str__(self):
#        return self.name + " | " + self.author
#        
#class GenusNBN(Genus):
#    
#    def __init__(self, name, author, link):
#        super().__init__(name, author)
#        
#        self.link = link



        
## Query the site for the micetophilidae family        
#
#eol_address = 'https://eol.org/api/search/1.0.json?'
#q = 'q=Mycetophilidae'
#page = 'page=1'
#key = 'key='
#et = '&' 
#
#url = eol_address + q + et + page + et + key
#
#req = Request(url, "myceto_home_page.pickle")
#req.load()
#
#main_query_json = req.response.json()
#
## find the mycetophilidae classification tree
#
#myceto_main_page_url = main_query_json['results'][0]['link']
#
#
#myceto_names_url = myceto_main_page_url + "/names"
#
#
#req = Request(myceto_names_url, "myceto_names.pickle")
#req.show_url()
#req.load()
#
#
## parse the page
#
#soup = bs4.BeautifulSoup(req.response.text, "html.parser")
#
## try to find the div containing the hierarchy
#
#divs = soup.find_all("div")
#
#print(len(divs))
#
#for i, div in enumerate(divs):
#    #print(div)
#    text = div.get_text()
#    if "EOL Dynamic Hierarchy 1.1" in text and "Mycetophilidae" in text:
#        print("FOUND", i)
#        print(text.replace('\n', ' ')[: 70])
#        
#        
#tree = str(divs[16])
#
#tree_bs = bs4.BeautifulSoup(tree, 'html.parser')
#tree_divs = tree_bs.find_all('div')
#
#for div in tree_divs:
#    if "Mycetophilidae" not in div:
#        print("-----")
#        print(div.get_text().replace('\n', ' ')[:50])