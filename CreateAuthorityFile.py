# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 10:59:46 2020

@author: maurop
"""

# =============================================================================
# Imports
# =============================================================================

import CreateHTMLFile
import Taxa
import LogFiles
import CSVFile

# =============================================================================
# Logging
# =============================================================================

logger = LogFiles.Logger(__name__)

# =============================================================================
# Function to create the authority file
# =============================================================================

def prep_field(field):
    ''' If a field is None will be converted to an empty string'''
    return field if field else ""

def generate_authority_file(taxa_list, fileinfo):
    ''' generates the csv file of the authority file'''
      
    csv_filename = fileinfo.csv_filename("authority_file")
    
    # Create a csv file
    f = CSVFile.CSVFile(csv_filename)
    
    # add the header
    header = ["" ,"Family", "Subfamily", "Tribe" , "Genus", "SpecificEpithet", "SubspecificEpithet", "InfraspecificRank", "InfraspecificEpithet", "Authorship"]
    
    f.add_line(header)
    
    # creates the records for each taxon in the list
    for i, taxa in enumerate(taxa_list):
        if i == 0:
            line = ["1"]
        else:
            line = [f"=A{i + 1} + 1"]
        
        line += [taxa.family]
        line += [prep_field(taxa.subfamily)]
        line += [prep_field(taxa.tribe)]        
        line += [prep_field(taxa.genus)]      
        
        # if is a genus the specie will be marked as "sp."
        if taxa.rank == Taxa.Taxa.rank_genus:
            line += ["sp."]
        else:
            line += [prep_field(taxa.specie)]

        line += [prep_field(taxa.subspecie)]
        line += [""]
        line += [""]
        line += [prep_field(taxa.author)]  
        line += ["".join(f'{link}, ' for link in taxa.links )[:-2]]
        
        f.add_line(line)
    
    f.write()
    logger.log_short_report("Authority file saved file in:" + csv_filename)

    
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