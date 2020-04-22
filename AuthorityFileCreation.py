# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 10:59:46 2020

@author: Media Markt
"""

import ProgressBar
import CreateHTMLFile

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
    
    
    pb = ProgressBar.ProgressBar(len(species_dicts))

    
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
        
        pb.draw_bar(n)
        
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
    ''' saves the authority file on disk and adds the headers'''
    
    print("Generating authority file...")
    
    csv_file = " ,Family,Subfamily,Tribe,Genus,SpecificEpithet,SubspecificEpithet,InfraspecificRank,InfraspecificEpithet,Authorship\n".encode("utf8")
    lines = create_authority_lines(species_dict)
    for line in lines:
        csv_file += line.encode("utf8")
    
    with open(filename, "wb") as f:
        f.write(csv_file)
    
    print("saved file in:", filename)


def generate_authority_file(species_dict, fileinfo):
    ''' generates the filename and passes it to the save functio'''
      
    csv_filename = fileinfo.csv_filename("authority_file")
        
    save_authority_file(csv_filename, species_dict)
    
    
    
# =============================================================================
#  Function to create the authority list    
# =============================================================================

def generate_authority_list(genus_list, species_list, fileinfo):
    
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
    
    
    fhtml.generate_html_file(fileinfo.html_filename("species_list"))