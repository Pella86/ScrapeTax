# -*- coding: utf-8 -*-
"""
Created on Thu Mar 19 09:16:57 2020

@author: maurop
"""

import xml.etree.ElementTree as ET

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


class CreateHTMLFile:
    
    def __init__(self):
        self.root = ET.Element("html")
        
        head = ET.SubElement(self.root, "head")
        
        self.style = ET.SubElement(head, "style")
        
        sel = SelectorProprieties("body")
        sel.add_propriety("font-family", "Lucida Console")
        
        
        psel = SelectorProprieties("p")
        psel.add_propriety("display", "inline")
        
        self.style.text = sel.generate_selector()
        self.style.text += psel.generate_selector()
        
        
        self.body = ET.SubElement(self.root, "body")
    
    
    def add_selector(self, selector):
        self.style.text += selector.generate_selector()
        
    
    def add_body_element(self, element):
        self.body.append(element)


    def add_italics_element(self, text):
        it = ET.Element("i")
        it.text = text
        self.add_body_element(it)
    
    def add_element(self, text):
        di = ET.Element("p")
        di.text = text
        self.add_body_element(di)
    
    def add_line_break(self):
        br = ET.Element("br")
        self.add_body_element(br)
    
    def add_empty_element(self, text):
        el = ET.Element("")
        el.text = (text)
        self.add_body_element(el)
    
    def add_heading(self, level, text):
        el = ET.Element(f"h{level}")
        el.text = text
        self.add_body_element(el)
        
    
    def generate_html_file(self, filename):
         tree = ET.ElementTree(self.root)
         tree.write(filename)     
    
    
        