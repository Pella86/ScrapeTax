#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 09:44:19 2020

@author: maurop
"""



import xml.etree.ElementTree as ET

root = ET.Element("html")
head = ET.SubElement(root, "head")
style = ET.SubElement(head, "style")
style.text = '''td {
  width: 42mm;
  height: 12mm;
  border: 1px solid black;
  padding: 5px;
  font-family: Lucida Console;
  font-size: 12px;
}'''

body = ET.SubElement(root, "body")


table = ET.SubElement(body, "table")

for rows in range(10):
    tr = ET.SubElement(table, "tr")
    for cols in range(5):
        td = ET.SubElement(tr, "td")
        
        genus = ET.SubElement(td, "i")
        genus.text = "Genus"
        
        nl = ET.SubElement(td, "br")
        
        specie = ET.SubElement(td, "i")
        specie.text = "specie"
        
        nl = ET.SubElement(td, "br")
        
        author = ET.SubElement(td, "div")
        author.text = "Author Name, date"
        
        


tree = ET.ElementTree(root)
tree.write("example_page.html")


class SelectorProprieties:
    
    
    def __init__(self, selector):
        
        self.selector = selector
        self.propriety_list = []
    
    def add_propriety(self, propriety, value):
        self.propriety_list.append((propriety, value))
        
    def generate_selector(self):
        s = self.selector + "{\n"
        
        for p in self.propriety_list:
            s += f"    {p[0]}: {p[1]};\n"
            
        s += "}\n"
            
        return s
        
        


class LabelsTable:
    
    def __init__(self):
        
        # set up the HTML
        self.root = ET.Element("html")
        head = ET.SubElement(self.root, "head")
        style = ET.SubElement(head, "style")
        
        sel = SelectorProprieties("td")
        #sel.add_propriety("background", "lightgrey")
        sel.add_propriety("width", "42mm")
        sel.add_propriety("height", "12mm")
        sel.add_propriety("border", "1px solid black")  
        sel.add_propriety("padding", "5px")
        sel.add_propriety("font-family", "Lucida Console")
        sel.add_propriety("font-size", "12px")
        
        style.text = sel.generate_selector()
        
        body = ET.SubElement(self.root, "body")
        self.table = ET.SubElement(body, "table")
        
    
    
    def generate_table(self, taxa_list):
        n_cols = 5
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
                    specie_str = genspe[1]
                    
                    genus = ET.SubElement(td, "i")
                    genus.text = genus_str
                    
                    ET.SubElement(td, "br")
                    
                    specie = ET.SubElement(td, "i")
                    specie.text = specie_str
                    
                    ET.SubElement(td, "br")
                    
                    author = ET.SubElement(td, "div")
                    author.text = taxa.author
    
    
    def generate_html(self, filename):
         tree = ET.ElementTree(self.root)
         tree.write(filename)                       
                
        


# =============================================================================
# Previous shit
# =============================================================================


# --- working example ---
#import xml.etree.ElementTree as ET
#
#root = ET.Element("html")
#head = ET.SubElement(root, "head")
#style = ET.SubElement(head, "style")
#style.text = '''td {
#  width: 42mm;
#  height: 12mm;
#  border: 1px solid black;
#  padding: 5px;
#  font-family: Lucida Console;
#  font-size: 12px;
#}'''
#
#body = ET.SubElement(root, "body")
#
#
#table = ET.SubElement(body, "table")
#
#for rows in range(10):
#    tr = ET.SubElement(table, "tr")
#    for cols in range(5):
#        td = ET.SubElement(tr, "td")
#        
#        genus = ET.SubElement(td, "i")
#        genus.text = "Genus"
#        
#        nl = ET.SubElement(td, "br")
#        
#        specie = ET.SubElement(td, "i")
#        specie.text = "specie"
#        
#        nl = ET.SubElement(td, "br")
#        
#        author = ET.SubElement(td, "div")
#        author.text = "Author Name, date"
#        
#        
#
#
#tree = ET.ElementTree(root)
#tree.write("example_page.html")


# --- previous html/css tests ---
#filename = "label_formatted_html.html"
#
#example = '''<!DOCTYPE html>
#<html>
#<head>
#<style>
#div {
#  background-color: lightgrey;
#  width: 35mm;
#  height: 20mm;
#  border: 1px solid black;
#  padding: 5px;
#  font-family: Lucida Console;
#  font-size: 12px;
#}
#
#
#
#</style>
#</head>
#
#<body>
#
#<div><i>Allodia<br>crescens</i><br>(Staeger, 1940)</div>
#
#
#
#</body>
#</html>'''
#
## div as table
## https://snook.ca/archives/html_and_css/getting_your_di 
#
#
#
#
#
#
#
#with open(filename, 'w') as f:
#    f.write(example)
#    
#    
    
# How many cells are in the width of a piece of paper?
# margin: 4.23 mm --- size A4: 210 mm
# 210 - 4.2 * 2 = 200
# 210 mm / 42 mm = 5 colonne


#<tr> <td> </td> </tr>


#import xml.etree.ElementTree as ET
#
#root = ET.Element("html")
#head = ET.SubElement(root, "head")
#style = ET.SubElement(head, "style")
#style.text = '''div {
#  background-color: lightgrey;
#  width: 35mm;
#  height: 20mm;
#  border: 1px solid black;
#  padding: 5px;
#  font-family: Lucida Console;
#  font-size: 12px;
#}'''
#
#body = ET.SubElement(root, "body")
#
#div = ET.SubElement(body, "div")
#div.text = "<i>Allodia<br>crescens</i><br>(Staeger, 1940)"
#
#
#tree = ET.ElementTree(root)
#tree.write("example_page.html")




