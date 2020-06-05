#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 09:21:27 2020

@author: maurop
"""
# =============================================================================
# Imports
# =============================================================================

import copy

import CreateLabelTable
import AuthorityFileCreation
import FileInfo
import TaxaList
import Levenshtein_distance

# =============================================================================
# Main 
# =============================================================================


def scrape_taxonomy(family_name, base_folder, sources, genera_filter, actions):
    fileinfo = FileInfo.FileInfo(base_folder, "_".join(sources), family_name)

    taxa_list = TaxaList.generate_taxa_list(base_folder, sources, family_name, genera_filter)
    
    
    taxa_list.clean_noauthor()

    for action in actions:
        
        if action == "authority list":
            AuthorityFileCreation.generate_authority_list(copy.copy(taxa_list.taxa), fileinfo)
        
        elif action == "authority file":
            AuthorityFileCreation.generate_authority_file(copy.copy(taxa_list.taxa), fileinfo)
        
        elif action == "label table":
            table = CreateLabelTable.LabelTable("safari")                
            table.create_table(taxa_list.taxa, fileinfo.html_filename("label_table"))
        else:
            print("Action not supported")
            

def get_author_name(author):
    pos = author.rfind(",")
    
    
    author_name = author[:pos]
    if author_name.startswith("("):
        author_name = author_name[1:]    
    
    return author_name


            


def scrape_gbif(family_name, base_folder, genera_filter, actions):
    
    
    gbif_taxa_list = TaxaList.generate_taxa_list_single(base_folder, "gbif", family_name)
    
    # filter the non accepted name
    gbif_taxa_list.filter_status()
    
    # filter the list for the relevant genuses
    gbif_taxa_list.filter_taxa(genera_filter)

    # remove taxa without authors
    gbif_taxa_list.clean_noauthor()

    
    # scrape the bold website to get the subfamilies and tribes
    bold_taxa_list = TaxaList.generate_taxa_list_single(base_folder, "bold", family_name)
    
    # find subfamilies and tribes
    associations = bold_taxa_list.find_associations()
    
    gbif_taxa_list.fill_associations(associations)

    
    
    # use the NBN_Atlas for the authors
    nbn_taxa_list = TaxaList.generate_taxa_list_single(base_folder, "nbn", family_name)
    
    for gbif_taxon in gbif_taxa_list.taxa:
        
        for nbn_taxon in nbn_taxa_list.taxa:
            
            if (gbif_taxon.genus == nbn_taxon.genus and
                gbif_taxon.specie == nbn_taxon.specie and
                gbif_taxon.subspecie == nbn_taxon.subspecie):
                
                
                if gbif_taxon.author != nbn_taxon.author:

                    gbif_author_name = get_author_name(gbif_taxon.author)
                    nbn_author_name = get_author_name(nbn_taxon.author)
                    
                    # if the name is the same, it means that is a parenthesis
                    # issue or a year issue, thus the name of the author is
                    # spelled correctly, we take the year from the nbn as a 
                    # reference
                    if gbif_author_name == nbn_author_name:
                        gbif_taxon.author = nbn_taxon.author
                        gbif_taxon.links += nbn_taxon.links
                        
                    else:
                        # if is a name issue check if the name is similar
                        # with the Levenshtein distance
                        distance = Levenshtein_distance.levenshtein(gbif_author_name, nbn_author_name)

                        # if the distance is less then 2 letters his means that
                        # is a probable spelling mistake so all the authors name
                        # should be substituted accordingly
                        if distance <= 2:
                            # substitute all the name in the list
                            for sub_author_taxon in gbif_taxa_list.taxa:
                                if get_author_name(sub_author_taxon.author) == gbif_author_name:
                                    sub_author_taxon.author = sub_author_taxon.author.replace(gbif_author_name, nbn_author_name)
                                    sub_author_taxon.author.links += ["Author spelling from NBN Atlas"]
                                    
                        # else there is a true author conflict so we take teh 
                        # nbn one?
                        else:
                            if nbn_taxon.author.find("misident.") != -1:
                                continue
                            else:
                                print("Name conflict")
                                print("GBIF:", gbif_taxon)
                                print("NBN:", nbn_taxon)
                                gbif_taxon.author = nbn_taxon.author
                                gbif_taxon.links += nbn_taxon.links
 
    taxa_list = gbif_taxa_list
    taxa_list.sort()
    
    fileinfo = FileInfo.FileInfo(base_folder, "gbif", family_name)
    for action in actions:
        
        if action == "authority list":
            AuthorityFileCreation.generate_authority_list(copy.copy(taxa_list.taxa), fileinfo)
        
        elif action == "authority file":
            AuthorityFileCreation.generate_authority_file(copy.copy(taxa_list.taxa), fileinfo)
        
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
    sources_input.default = "gbif, bold"
    sources_input.comma_values = True
    
    sources = sources_input.get_input()

    # Get the family
    family_name_input = UserInput()
    family_name_input.title = "Input the family name"
    family_name_input.input_sentence = "family"
    family_name_input.default = "Mycetophilidae"
    
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
    


PRODUCTION = False   

if __name__ == "__main__":
    if PRODUCTION:
        prod_main()
    else:
        
        family_name = "Chrysididae"
        base_folder = "./Data"
        genera_filter = []
        actions = ["authority list", "authority file", "label table"]
        
        scrape_gbif(family_name, base_folder, genera_filter, actions)
        
        
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
        
        
