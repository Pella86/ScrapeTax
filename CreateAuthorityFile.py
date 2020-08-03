# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 10:59:46 2020

@author: maurop
"""

# =============================================================================
# Imports
# =============================================================================

import ProgressBar
import CreateHTMLFile
import Taxa
import LogFiles

# =============================================================================
# Logging
# =============================================================================

logger = LogFiles.Logger(__name__)

# =============================================================================
# Function to create the authority file
# =============================================================================

def create_authority_lines(taxa_list):
    ''' function that given a list of taxonomic dictionary of species creates
    a line of the authority file separated and formatted (utf-8). The file can
    be imported in excel'''
    
    logger.log_short_report("--- Generating authority file ---")
    
    
    # Data will be comma separated
    separator = ","
    
    # create the lines based on the above defined elements
    lines = []
    
    
    for i, taxa in enumerate(taxa_list):

        line = ""
        
        if i == 0:
            line += "1" + separator     
        else:
            line += f"= A{i + 1} + 1" + separator     
        
        line += taxa.family + separator
        
        line += (f'"{taxa.subfamily}"' if taxa.subfamily else "") + separator
        
        line += (f'"{taxa.tribe}"' if taxa.tribe else "") + separator
        
        line += (f'"{taxa.genus}"' if taxa.genus else "") + separator
        
        if taxa.rank == Taxa.Taxa.rank_genus:
            line += "sp." + separator
        else:
            line += (f'"{taxa.specie}"' if taxa.specie else "") + separator

        line += (f'"{taxa.subspecie}"' if taxa.subspecie else "") + separator

        line += "" + separator # infraspecific rank

        line += "" + separator # infraspecific epithet

        line +=  (f'"{taxa.author}"' if taxa.author else "") + separator 

        line +=  '"' + "".join(f'{link}, ' for link in taxa.links )[:-2] +'"'  
        
        line += "\n"
        
        lines.append(line)
    
    
    logger.log_report(f"Created {len(lines)} lines")
        
    
    return lines    
    
def save_authority_file(filename, taxa_list):
    ''' saves the authority file on disk and adds the headers'''
    
    csv_file = " ,Family,Subfamily,Tribe,Genus,SpecificEpithet,SubspecificEpithet,InfraspecificRank,InfraspecificEpithet,Authorship\n".encode("utf8")
    lines = create_authority_lines(taxa_list)
    for line in lines:
        csv_file += line.encode("utf8")
    
    with open(filename, "wb") as f:
        f.write(csv_file)
    
    logger.log_short_report("Authority file saved file in:" + filename)


def generate_authority_file(taxa_list, fileinfo):
    ''' generates the filename and passes it to the save functio'''
      
    csv_filename = fileinfo.csv_filename("authority_file")
        
    save_authority_file(csv_filename, taxa_list)
    
    
    
# =============================================================================
#  Function to create the authority list    
# =============================================================================

def generate_authority_list(taxa_list, fileinfo):
    
    logger.log_short_report("-- Generating Authority List ---")
    
    fhtml = CreateHTMLFile.CreateHTMLFile()
    # add date of creation and how many taxas are in the file
    # maybe add the possibility to save the generate tree for later use?
    # could be useless since it will be not modifiable
    
    fhtml.add_heading(1, "Species list for " + fileinfo.family_name)
    
    fhtml.add_heading(2, "Genuses")
    fhtml.add_line_break()
    
    taxa_list.sort(key=lambda t : t.sort_key_genus())
    
    for genus in filter(lambda taxa : taxa.rank == Taxa.Taxa.rank_genus, taxa_list):
        fhtml.add_italics_element(genus.genus)
        fhtml.add_element(", ")
        if genus.author:
            fhtml.add_element(genus.author)
        else:
            fhtml.add_element("author not found")
        fhtml.add_line_break()

    fhtml.add_heading(2, "Species")
    fhtml.add_line_break()
    
    for specie in filter(lambda taxa : taxa.rank == Taxa.Taxa.rank_specie, taxa_list):
        fhtml.add_italics_element(specie.genus + " " + specie.specie)
        fhtml.add_element(", ")
        fhtml.add_element(specie.author)
        fhtml.add_line_break()
    
    
    filename = fileinfo.html_filename("species_list")
    
    fhtml.generate_html_file(filename)
    
    logger.log_short_report("Authority list saved in: " + filename)
    

# =============================================================================
#  Function to create the synonym list    
# =============================================================================
    
def generate_synonym_list(synonym_list, fileinfo):
    
    logger.log_short_report("--- Generating Synonyms list ---")
    
    fhtml = CreateHTMLFile.CreateHTMLFile()
    fhtml.add_heading(1, "Synonyms list for " + fileinfo.family_name)   
 
    fhtml.add_heading(2, "Synonym (...) Accepted name")
    fhtml.add_line_break()
    

    for synonym in synonym_list:
        
        syn_taxa = synonym.synonym_taxa
        
        fhtml.add_italics_element(syn_taxa.get_name())
        
        fhtml.add_element(", ")
        
        if syn_taxa.author:
            fhtml.add_element(syn_taxa.author)
        else:
            fhtml.add_element("author not found")
            
        fhtml.add_element("  =  ")
        
        acc_taxa = synonym.accepted_taxa
        
        fhtml.add_italics_element(acc_taxa.get_name())
        fhtml.add_element(", ")
        if acc_taxa.author:
            fhtml.add_element(acc_taxa.author)
        else:
            fhtml.add_element("author not found")
        
        fhtml.add_line_break()
    
    filename = fileinfo.html_filename("synonym_list")
    fhtml.generate_html_file(filename)
    
    logger.log_short_report("Synonyms file saved in: " + filename)