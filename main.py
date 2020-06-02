#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 09:21:27 2020

@author: maurop
"""
# =============================================================================
# Imports
# =============================================================================

import CreateLabelTable
import AuthorityFileCreation
import FileInfo
import TaxaList

# =============================================================================
# Main 
# =============================================================================


def scrape_taxonomy(family_name, base_folder, sources, genera_filter, actions):
    fileinfo = FileInfo.FileInfo(base_folder, "_".join(sources), family_name)

    taxa_list = TaxaList.generate_taxa_list(base_folder, sources, family_name, genera_filter)

        
    for action in actions:
        
        if action == "authority list":
            AuthorityFileCreation.generate_authority_list(taxa_list.taxa, fileinfo)
        
        elif action == "authority file":
            AuthorityFileCreation.generate_authority_file(taxa_list.taxa, fileinfo)
        
        elif action == "label table":
            table = CreateLabelTable.LabelTable("safari")                
            table.create_table(taxa_list.taxa, fileinfo.html_filename("label_table"))
        else:
            print("Action not supported")
            
class UserInput:

    def __init__(self):
        self.title = None
        self.input_sentence = None
        self.default = None
        self.comma_values = False
        
        self.user_input = None
    
    def get_user_input(self):
        print("-" * 79)
        print(self.title)
        
        if self.default:
            print("Default:", self.default)
        
        choice = input(self.input_sentence + " >")
        
        if choice == "":
            choice = self.default
        
        self.user_input = choice  
        
    def parse_comma_separated(self):
        if self.user_input:
            parts = self.user_input.split(",")
            val = [v.strip() for v in parts]
            
            self.user_input = val
    
    def get_input(self):
        
        self.get_user_input()
        
        if self.comma_values:
            self.parse_comma_separated()
        
        print("Input:", self.user_input)
        
        return self.user_input
        

def prod_main():
    
    
    # title
    print("Scrape Tax")
    print("Program to gather informations from online databases about species and genuses")
    
    # get the base folder
    base_folder_input = UserInput()
    base_folder_input.title = "The path to the folder where the file will be saved, the folder must already exist. Use dot (.) to access the current folder"
    base_folder_input.input_sentence = "path"
    base_folder_input.default = "./Data"
    
    base_folder = base_folder_input.get_input()
    
    # gather the source website
    sources_input = UserInput()
    sources_input.title = "Chose a website (nbn, eol, gbif, bold)"
    sources_input.input_sentence = "website(s)"
    sources_input.default = "eol, nbn, gbif, bold"
    sources_input.comma_values = True
    
    sources = sources_input.get_input()

    # Get the family
    family_name_input = UserInput()
    family_name_input.title = "Input the family name"
    family_name_input.input_sentence = "family"
    family_name_input.default = "Mantidae"
    
    family_name = family_name_input.get_input()
    
    # Add the option to filter by genus
    genera_input = UserInput()
    genera_input.title = "Give genera names to be filtered comma separated, if the input is an empty list, all the genera will be considered"
    genera_input.input_sentence = "genera"
    genera_input.default = []
    genera_input.comma_values = True
    
    genera_filter = genera_input.get_input()
    
    print("Generating lists...")
    
    actions = ["authority list", "authority file", "label table"]
    
    scrape_taxonomy(family_name, base_folder, sources, genera_filter, actions)
    
    
#    fileinfo = FileInfo.FileInfo(base_folder, "_".join(sources), family_name)
#
#    taxa_list = TaxaList.generate_taxa_list(base_folder, sources, family_name, genera_filter)
#
#
#    exit_command = False
#    
#    while not exit_command:
#        print("{:-^79}".format("What you would like to do?"))
#        print("  1. Generate authority list")
#        print("  2. Generate label table")
#        print("  3. Create csv authority file")
#        print("  4. Exit (e, exit, quit)")
#        
#        
#        choice = input("pick a number >")    
#        if choice == "e" or choice == "exit" or choice == "quit" or choice == "4":
#            exit_command = True
#        else:
#            try:
#                choice = int(choice)
#            except ValueError:
#                print("not a value from 1 to 3")
#                choice = None 
#
#            if choice == 1:
#                print("Generating authority list...")
#                
#                AuthorityFileCreation.generate_authority_list(taxa_list.taxa, fileinfo)  
#                
#                print("Authority list created")
#            
#            elif choice == 2:
#                print("Generating label table...")
#                
#                table = CreateLabelTable.LabelTable("safari")
#                
#                table.create_table(taxa_list.taxa, fileinfo.html_filename("label_table"))
#
#                print("Table created.")
#                
#            elif choice == 3:
#                print("Generating authority file...")
#                    
#                AuthorityFileCreation.generate_authority_file(taxa_list.taxa, fileinfo)
#                
#                print("Authority file created.")
#            
#            else:
#                print("Choice not available")
#                exit_command = True            
#        


PRODUCTION = True   

if __name__ == "__main__":
    if PRODUCTION:
        prod_main()
    else:
        pass
        
        
# =============================================================================
# Chrysidide specific stuff
# =============================================================================
        # family = "Chrysididae"
        # prefix = family.lower()

        # base_folder = "./Data/Chrysididae"
        
        # url = "https://species.nbnatlas.org/species/NBNSYS0000159685"
        
        
        # _, species_list_chr = Chrysis_net.generate_lists(base_folder, prefix)
        # spec_dict = Chrysis_net.generate_specie_dictionary(species_list_chr)
        
        # AuthorityFileCreation.generate_authority_file(spec_dict, base_folder, "chr_" + prefix)
        
        # _, species_list_nbn = NBN_parser.generate_lists(url, base_folder, prefix)
        # _, species_list_eol = EncyclopediaOfLife.generate_lists(family, base_folder, prefix)
        # _, species_list_chr = Chrysis_net.generate_lists(base_folder, prefix)
        # print(len(species_list_nbn), len(species_list_eol), len(species_list_chr))
        
        
        # csv = '"Present in","NBN Atlas","EOL Database","Chrysis.net"\n'
        
        # complete_list = []
        
        # for nbn_specie in species_list_nbn:
        #     complete_list.append(nbn_specie)
            
        # for eol_specie in species_list_eol:
        #     if eol_specie.name in [sp.name for sp in complete_list]:
        #         continue
        #     else:
        #         complete_list.append(eol_specie)
            
        # for chr_specie in species_list_chr:
        #     if chr_specie.name in [sp.name for sp in complete_list]:
        #         continue
        #     else:
        #         complete_list.append(chr_specie)
        # complete_list.sort(key= lambda item : item.name)  
        
        # lines = ""
        # for sp in complete_list:
        #     line = f'"{sp.name}",'
            
        #     if sp.name in [s.name for s in species_list_nbn]:
        #         line += "x,"
        #     else:
        #         line += ","
                    
        #     if sp.name in [s.name for s in species_list_eol]:
        #         line += "x,"
        #     else:
        #         line += ","                    
                    
        #     if sp.name in [s.name for s in species_list_chr]:
        #         line += "x"
        #     else:
        #         line += ""
            
        #     lines += line + "\n"
                
        # csv += lines
                
        # filename = os.path.join(base_folder, "list_compare.csv")
        
        # with open(filename, "wb") as f:
        #     f.write(csv.encode("utf8"))
        
        
