#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 09:21:27 2020

@author: maurop
"""
# =============================================================================
# Imports
# =============================================================================

import NBN_parser
import CreateLabelTable
import EncyclopediaOfLife
import Chrysis_net
import AuthorityFileCreation
import FileInfo
import GBIF_downloader
import BOLD_downloader
import Taxa

# =============================================================================
# Fusion functions
# =============================================================================


def fuse_taxa(taxa_lists):
    ''' The function fuses multiple taxa list together'''
    
    if len(taxa_lists) < 1: 
        raise Exception("Fuse data: taxa_lists is empty")
    
    fusion_list = []
    
    # Fill the fusion list with the first element of taxa lists which is a list
    # of taxa coming from one of the different sources
    fusion_list += taxa_lists[0]
    taxa_lists.pop(0)
    
    # Now scan the other lists for duplicates and fill in missing informations
    for taxa_list in taxa_lists:
        
        # for each taxa in the list
        for taxa in taxa_list:
            
            # compare it with the taxa, if is already there add the links 
            # sources and eventual taxonomy differences
            for ftaxa in fusion_list:
    
                if ftaxa.is_equal(taxa):
                    ftaxa.copy_taxonomy(taxa)
                    
                    if ftaxa.author == None and taxa.author != None:
                        ftaxa.author = taxa.author
                    
                    ftaxa.source += taxa.source
                    ftaxa.links += taxa.links
                    break
            else:
                fusion_list.append(taxa)
                
    return fusion_list


def filter_taxa(taxa_list, genera_filter):
    ''' The function filters the taxa list according to genera'''
    
    if genera_filter:
    
        genus_filtered = []
    
        # little debug counter to check how many are selected    
        
        genus_count = {}
            
        for g in genera_filter:
            genus_count[g] = 0
        
        for taxa in taxa_list:
            
            for filt in genera_filter:
                if taxa.genus.find(filt) != -1:
                    genus_filtered.append(taxa)
                    genus_count[filt] += 1
        
        print("--- Items found in genus filtering ---")
        for key, value in genus_count.items():
            print(key, value)
        print("--------------------------------------")
    
    else:
        genus_filtered = taxa_list
    
    return genus_filtered


def filter_status(taxa_list):
    ''' Tests wether the status of the taxonomic name is accepted, the
        taxonomic status information are retrived from the GBIF database
    '''
    
    def check_status(item):
        if item.taxonomic_status != None:
            return item.taxonomic_status == "ACCEPTED"
        else:
            return True
    
    return filter(lambda item : check_status(item), taxa_list)
    

    
        

# =============================================================================
# Main 
# =============================================================================
 


def get_input(title, input_sentence, default = None):
    print("-" * 79)
    print(title)
    choice = input(input_sentence + " >")
    if choice == "":
        choice = default
    return choice


def parse_sources():
    
    correct_answer = False
    
    while not correct_answer:
        
        sources = get_input("Chose a website (nbn, eol, gbif, bold)", "website", "eol, nbn, gbif, bold")
        
        sources_parts = sources.split(",")
        sources_parts = [source.strip() for source in sources_parts]
        
        print("Sources: ", sources_parts)
        
        return sources_parts
        

def prod_main():
    
    
    # title
    print("Scrape Tax")
    print("Program to gather informations from online databases about species and genuses")
    
    # Gather the path information
    base_folder = get_input("The path to the folder where the file will be saved, the folder must already exist. Use dot (.) to access the current folder",
                            "path",
                            "./Data")
    
    print("Base folder:", base_folder)

    
    # gather the source website
    sources = parse_sources()

    # Get the family
    family_name = get_input("Input the family name",
                                "family",
                                "Noctuidae")
    
    print("Family:", family_name)
    
    # Add the option to filter by genus
    genera_filter = get_input("Give genera names comma separated", "genera", [])
    if genera_filter:
        genera_filter = [genus.strip() for genus in genera_filter.split(",")]

    print("Generating lists...")

    taxa_lists = []
    
    source_module = {"nbn"  : NBN_parser,
                     "eol"  : EncyclopediaOfLife,
                     "gbif" : GBIF_downloader,
                     "bold" : BOLD_downloader
                     }
    
    def generate_lists(source):
        fileinfo = FileInfo.FileInfo(base_folder, source, family_name)
        genus_list, species_list = source_module[source].generate_lists(family_name, fileinfo)
        return genus_list + species_list
    
    for s in sources:
        taxa_lists.append(generate_lists(s))
              
    
    # create the informations
    fileinfo = FileInfo.FileInfo(base_folder, "".join(sources), family_name)    
    
    taxa_list = fuse_taxa(taxa_lists)
    
    taxa_list = filter_taxa(taxa_list, genera_filter)
    
    # gather the tribes / subfamilies information
    
    subfamilies, tribes = Taxa.construct_associations(taxa_list)
    
    # use the associations assign the families to the extant genera
    
    for taxa in taxa_list:
        if taxa.subfamily == None:
            for subfamily in subfamilies:
                if taxa.genus in subfamily.associates:
                    taxa.subfamily = subfamily.main_taxa
                    break

        if taxa.tribe == None:
            for tribe in tribes:
                if taxa.genus in tribe.associates:
                    taxa.tribe = tribe.main_taxa
                    break
    
    # sort the list
    taxa_list.sort(key=lambda t : t.sort_key())
                


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
                print("Generating authority list...")
                
                AuthorityFileCreation.generate_authority_list(taxa_list, fileinfo)  
                
                print("Authority list created")
            
            elif choice == 2:
                print("Generating label table...")
                
                table = CreateLabelTable.LabelTable("safari")
                
                table.create_table(taxa_list, fileinfo.html_filename("label_table"))

                print("Table created.")
                
            elif choice == 3:
                print("Generating authority file...")
                    
                AuthorityFileCreation.generate_authority_file(taxa_list, fileinfo)
                
                print("Authority file created.")
            
            else:
                print("Choice not available")
                exit_command = True            
        


PRODUCTION = True   

if __name__ == "__main__":
    if PRODUCTION:
        prod_main()
    else:
        
        base_folder = "./Data/Fusion"
        family_name = "Mycetophilidae"
        
        print("EOL Analyisis")
        fileinfo = FileInfo.FileInfo(base_folder, "eol", family_name)
        
        eol_glist, eol_slist = EncyclopediaOfLife.generate_lists(family_name, fileinfo)
        
        eol_list = eol_glist + eol_slist

        print("NBN Analyisis")        
        fileinfo = FileInfo.FileInfo(base_folder, "nbn", family_name)
        
        nbn_glist, nbn_slist = NBN_parser.generate_lists(family_name, fileinfo)
        
        nbn_list = nbn_glist + nbn_slist        

        print("GBIF Analyisis")        
        fileinfo = FileInfo.FileInfo(base_folder, "gbif", family_name)
        
        gbf_glist, gbf_slist = GBIF_downloader.generate_lists(family_name, fileinfo)
        
        gbf_list = gbf_glist + gbf_slist      
        
        print("Fusing the sources...")
        
        
        fusion = fuse_taxa([gbf_list, nbn_list, eol_list])
        
        #gfilter = ["Neoempheria", "Acnemia", "Azana", "Leptomorphus", "Neuratelia", "Neoplatyura", "Megalopelma", "Polylepta", "Sciophila", "Pyratula"]
        #gfilter = ["Palaeodocosia", "Synplasta", "Syntemna", "Boletina", "Bolitophila", "Coelosia", "Gnoriste", "Grzegorzekia", "Docosia"]
        #gfilter = ["Leia", "Rondaniella", "Dynatosoma", "Mycetophila"]
        #gfilter = ["Phronia", "Trichonta", "Zygomyia", "Tarnania"]
        #gfilter = ["Allodia", "Allodiopsis", "Anatella", "Brevicornu", "Brevicornis", "Cordyla"]
        #gfilter = ["Exechia", "Exechiopsis", "Rymosia", "Epicypta"]
        #gfilter = ["Phthinia"]
        gfilter = []
        
        genus_filtered = filter_taxa(fusion, gfilter)
        
        tlist = filter_status(genus_filtered)

        for taxa in tlist:
            if taxa.genus == "Docosia" and taxa.specie == "setosa":
                print(taxa)
                print(taxa.taxonomic_status)

        
#        fileinfo = FileInfo.FileInfo(base_folder, "all", family_name)
#        table = CreateLabelTable.LabelTable("safari")
#        table.create_table(genus_filtered, fileinfo.html_filename("taxa_table"))
#        
#        print("Table generated")
                    
                    
        
        
#        base_folder = "./Data/Vespidae"
#        family_name = "Vespidae"
#        prefix = family_name.lower()
#        
#        fileinfo = FileInfo.FileInfo(base_folder, prefix)
#        
#        glist, slist = EncyclopediaOfLife.generate_lists(family_name, fileinfo)
        
        # lt = CreateLabelTable.LabelTable()  
        # lt.create_table(slist, fileinfo.html_filename("table"))
        
        # base_folder = "./Data/Formicidae"
        # url = "https://species.nbnatlas.org/species/NBNSYS0000037030" 
        # prefix = "formicidae"          

        
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