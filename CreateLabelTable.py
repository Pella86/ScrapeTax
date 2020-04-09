# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 09:52:02 2020

@author: Media Markt
"""

import xml.etree.ElementTree as ET

import CreateHTMLFile



class LabelTable:   
    
    def __init__(self):
        self.fhtml = CreateHTMLFile.CreateHTMLFile()
        
        tsel = CreateHTMLFile.SelectorProprieties("table")
        tsel.add_propriety("border-collapse", "collapse")
        
        self.fhtml.add_selector(tsel)
        
        
        table_selector = CreateHTMLFile.SelectorProprieties("td")
        table_selector.add_propriety("width", "42mm")
        table_selector.add_propriety("height", "12mm")
        table_selector.add_propriety("border", "1px solid black")  
        table_selector.add_propriety("padding", "5px")
        #table_selector.add_propriety("font-family", "Lucida Console")
        table_selector.add_propriety("font-size", "8px")  
        #table_selector.add_propriety("border-collapse", "collapse")
        
        self.fhtml.add_selector(table_selector)
        
        self.table = ET.SubElement(self.fhtml.body, "table")
        
 
    def create_table(self, taxa_list, filename):
        n_cols = 4
        n_rows = int(len(taxa_list) / n_cols) + 1
        
        print(f"Table will be {n_rows}x{n_cols}")
        
        for i in range(n_rows):
            
            tr = ET.SubElement(self.table, "tr")
            
            for j in range(n_cols):
                
                cur_index = i * n_cols + j
                
                if  cur_index < len(taxa_list):
                    
                    taxa = taxa_list[cur_index]
                    
                    td = ET.SubElement(tr, "td")
                    
                    print(taxa)
                    
                    genspe = taxa.name.split(" ")
                    
                    
                    genus_str = genspe[0]
                    
                    specie_str = ""
                    if len(genspe) >= 2:
                        specie_str = genspe[1]
                    
                    genus = ET.SubElement(td, "i")
                    genus.text = genus_str
                    
                    ET.SubElement(td, "br")
                    
                    specie = ET.SubElement(td, "i")
                    specie.text = specie_str
                    
                    ET.SubElement(td, "br")
                    
                    author = ET.SubElement(td, "div")
                    author.text = taxa.author 
    
        self.fhtml.generate_html_file(filename)
    


if __name__ == "__main__":
    table = LabelTable()
    
    import os
    import NBN_parser
    
    base_folder = ".\Data\Vespidae"
    
    filename = os.path.join(base_folder, "vespidae_specie_list.mptaxa")
    species_list = NBN_parser.laod_taxa_list(filename)
    
    table.create_table(species_list,
                       os.path.join(base_folder,
                                    "vespidae_label_table_test.html"
                                    )
                       )