# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 09:52:02 2020

@author: maurop
"""

import xml.etree.ElementTree as ET

import CreateHTMLFile


# =============================================================================
# Labels table creation
# =============================================================================

class LabelTable:   
    
    def __init__(self, browser):
        
        # creates a generic html file
        self.fhtml = CreateHTMLFile.CreateHTMLFile()
        
        # manages the proprieties of the table
        tsel = CreateHTMLFile.SelectorProprieties("table")
        tsel.add_propriety("border-collapse", "collapse")
        tsel.add_propriety("page-break-after", "always") #forces the spaces between tables to print a table per page
        
        self.fhtml.add_selector(tsel)
        
        left_sel = CreateHTMLFile.SelectorProprieties(".left")
        left_sel.add_propriety("float", "left")
        self.fhtml.add_selector(left_sel)
        
        right_sel = CreateHTMLFile.SelectorProprieties(".right")
        right_sel.add_propriety("float", "right")
        self.fhtml.add_selector(right_sel)
        
        
        
        # formatting the text and size of the cell
        table_selector = CreateHTMLFile.SelectorProprieties("td")
        table_selector.add_propriety("width", "42mm")
        table_selector.add_propriety("height", "12mm")        
        table_selector.add_propriety("border", "1px solid black")  
        table_selector.add_propriety("padding", "5px")
        table_selector.add_propriety("font-family", "Lucida Console")
        #table_selector.add_propriety("border-collapse", "collapse")  
 
        # Browser specific proprieties
        if browser == "chrome":
            table_selector.add_propriety("font-size", "8px")  
            self.n_rows_per_table = 22
        
        elif  browser == "safari":
            table_selector.add_propriety("font-size", "10px") 
            self.n_rows_per_table = 15
        else:
            raise Exception("LabelTable: No browser specified")
        
        self.fhtml.add_selector(table_selector)
        
        # The xml element table
        self.table = ET.SubElement(self.fhtml.body, "table")
        
 
    def create_table(self, taxa_list, filename):
        
        # fixed number of columns (fits an A4)
        n_cols = 4
        
        # total number of rows is figured out from how many taxas are there
        n_rows = int(len(taxa_list) / n_cols) + 1
        
        print(f"Table will be {n_rows}x{n_cols}")
        
        # Start generating a coloumn
        for irow in range(n_rows):
            
            # Insert a page break for every page
            if irow % self.n_rows_per_table == 0:
                self.table = ET.SubElement(self.fhtml.body, "table")
                self.fhtml.add_line_break()
            
            tr = ET.SubElement(self.table, "tr")
            
            for icol in range(n_cols):
                
                # calculates the index row major for the table
                cur_index = irow * n_cols + icol
                
                # index can overflow the real length (if the length of the 
                # taxa_list isn't divisbile by n_cols)
                if  cur_index < len(taxa_list):
                    
                    taxa = taxa_list[cur_index]

                    # divide genus and specie
                    genspe = taxa.name.split(" ")

                    # if the name is binomial (e.g. Metisa plana)
                    if len(genspe) >= 2:                        
                        genus_str = genspe[0]
                        specie_str = "".join([n + " " for n in genspe[1:]])
                    
                    # if the name is only the genus (e.g Metisa)
                    elif len(genspe) == 1:
                        genus_str = genspe[0]
                        specie_str = "sp."
 
                    # Line corresponding to the genus
                    td = ET.SubElement(tr, "td")
                    
                    genus = ET.SubElement(td, "i")
                    genus.text = genus_str
                    
                    ET.SubElement(td, "br")
                                        
                    # Line corresponding to the specie
                    if specie_str == "sp.":
                        specie = ET.SubElement(td, "div")
                        specie.text = specie_str
                    else:
                        specie = ET.SubElement(td, "i")
                        specie.text = specie_str
                        ET.SubElement(td, "br")

                    # Line corresponding to author
#                    author = ET.SubElement(td, "div")
#                    if taxa.author:
#                        author.text = taxa.author
#                    else:
#                        author.text = "Author not available"
                    
                    # add the source to the last line
                    last_line_div = ET.SubElement(td, "div")
                    
                    left = ET.SubElement(last_line_div, "span")
                    left.set("class", "left")
                    if taxa.author:
                        left.text = taxa.author
                    else:
                        left.text = "Author not available"
                    
                    if taxa.source:
                        right = ET.SubElement(last_line_div, "span")
                        right.set("class", "right")
                        right.text = "(" + taxa.source + ")"
    
        self.fhtml.generate_html_file(filename)
    


if __name__ == "__main__":
     table = LabelTable("safari")
    
     import os
     import NBN_parser
     import FileInfo
    
     base_folder = "./Data/Vespidae"
     prefix = "vespidae"
     
     fi = FileInfo.FileInfo(base_folder, prefix)
     family_url = "https://species.nbnatlas.org/species/NBNSYS0000050803"
     
     
     genus_list, species_list = NBN_parser.generate_lists(family_url, fi)
    
     table.create_table(genus_list + species_list,
                        os.path.join(base_folder,
                                     "vespidae_label_table_test.html"
                                     )
                        )
    