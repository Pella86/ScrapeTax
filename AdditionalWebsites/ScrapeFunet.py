#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 11 09:57:03 2020

@author: maurop
"""

# =============================================================================
# import hacks
# =============================================================================

import sys
prev_dir = "../"
if prev_dir not in sys.path:
    sys.path.append(prev_dir)

# =============================================================================
# imports    
# =============================================================================

import RequestsHandler
import FileInfo
import Taxa

# =============================================================================
# 
# =============================================================================

lepi_url = "http://ftp.funet.fi/index/Tree_of_life/insecta/lepidoptera/"

fi = FileInfo.FileInfo("./funet", "funet", "Lepidoptera")


def parse_LIST(ul_element):
    names = ul_element.find_all("span", {"class": "TN"})        
    
    taxon_list = []
    
    for name_tag in names:
        
        # find the taxon name
        name_parts = name_tag.text.split(" ", 1)
        
        
        # some names dont have an author
        if len(name_parts) == 2:
            name = name_parts[0]
            author = name_parts[1]
        else:
            name = name_parts[0]
            author = None
            
        
        link_tag = name_tag.find("a")
        
        if link_tag is None:
            link = None
        else:
            link = url + link_tag.get("href")

        
        taxon_list.append(Taxon(name, author, link))    
    return taxon_list


class Taxon:
    
    def __init__(self, name, author, link):
        self.name = name
        self.author = author
        self.link = link
    
    def __str__(self):
        return self.name
        
    
class TaxonPage:
    
    def __init__(self, url, page_name):
        
        fi = FileInfo.FileInfo("./funet", "funet", "Lepidoptera")
        
        
        req = RequestsHandler.Request(url, fi.cache_filename(page_name))
        req.load()
        
        soup = req.get_soup()
        
        clist = soup.find("ul", {"class":"LIST"})
        
        self.taxon_list = parse_LIST(clist)
        self.page_name = page_name
        self.link = url
        

class Node:
    
    def __init__(self, taxon_page):
        
        self.page = taxon_page
        self.subpages = []
        
        if self.page.page_name.endswith("idae"):
            pass
        else:
            for taxon in self.page.taxon_list:
                
                if taxon.link == None:
                    continue
                
                tp = TaxonPage(taxon.link, taxon.name)
                
    
    
                
                self.subpages.append(Node(tp))
       

class Tree:
    
    
    def __init__(self):
        
        tp = TaxonPage(lepi_url, "main_page")
        self.root = Node(tp)
        
    def print_node(self, node, level):
        print("  "*level + node.page.page_name, len(node.subpages))
        
    def print_sub(self, current_node, level):
        
        for node in current_node.subpages:
            self.print_node(node, level)
            
            if len(node.subpages) != 0:
                self.print_sub(node, level + 1)
                
            
    def print_tree(self):
        
        self.print_sub(self.root, 0)
            
    
    def get_family_node(self, current_node, family_name, result):
        
        for node in current_node.subpages:
            
            if node.page.page_name == family_name:
                result.append(node.page.link)
            else:
                self.get_family_node(node, family_name, result)
    
    def get_family_link(self, family_name):
        result = []
        self.get_family_node(self.root, family_name, result)
        if len(result) == 1:
            return result[0]
        else:
            raise Exception("Name not found:", family_name)

#t = Tree()     
#t.print_tree()       
#
#
#print(t.get_family_link("ax"))
#
#tp = TaxonPage(t.get_family_link("Papilionidae"))
#
#


url = "http://ftp.funet.fi/index/Tree_of_life/insecta/lepidoptera/ditrysia/papilionoidea/riodinidae/"

req = RequestsHandler.Request(url, fi.cache_filename("test_riodinidae")) 
req.load()


soup = req.get_soup()

body = soup.find("body")


chirren = body.findChildren(recursive=False)


taxon_list = []
group = None
children = []

for ele in chirren:

    if ele.name == "div" and ele.has_attr('class') and ele['class'][0] == 'GROUP':
        if group is not None:
            taxon_list.append((group, children))
            children = []
        
        # parse the group
        
        tag = ele.find("span", {"class":"TN"})
        
        if tag is not None:
        
            print(tag.text)
            
            text_parts = tag.text.split(" ")
            
            rank = text_parts[0]
            name = text_parts[1]
            author = " ".join(text_parts[2:])
            
            group = (rank, name, author)
            print(group)
        

    if ele.name == "ul" and ele.has_attr("class") and ele["class"][0] == "LIST":
        
        children = parse_LIST(ele)
            
        print(children)

print()


class AssociatedTaxa:
    ''' class that couples a taxa with a list of subtaxa, like a subfamily
        coupled with a genus
    '''
        
    def __init__(self, main_taxa, rank):
        
        self.rank = rank
        self.main_taxa = main_taxa
        self.associates = []
    
    def add_associate(self, associate):
        self.associates.append(associate)
    
    def __eq__(self, other):
        return self.main_taxa == other
    
    def __str__(self):
        
        associates_str = "".join(associate + ", " for associate in self.associates)
        associates_str = associates_str[:-2]
        return "- " + self.main_taxa + ": " + associates_str

for group, children in taxon_list:
    print(group)
    for child in children:
        print("   ", child)
        

# take the parsed page and assign the corresponding tribes and subfamilies
        
# list containing all associations
subfamilies = []
tribes = []

# Since it is a drop down the first name encompasses the subsequent names
current_tribe = None
current_subfamily = None       

for group, children in taxon_list:
    
    if group[0] == "Tribe":
        if current_tribe:
            tribes.append(current_tribe)
        current_tribe = AssociatedTaxa(group[1], "tribe")

    if group[0] == "Subfamily":
        if current_subfamily:
            subfamilies.append(current_subfamily)
        current_subfamily = AssociatedTaxa(group[1], "subfamily")

    for child in children:
        if current_tribe:
            current_tribe.add_associate(child.name)
        
        if current_subfamily:
            current_subfamily.add_associate(child.name)

if current_subfamily:
    subfamilies.append(current_subfamily)

if current_tribe:
    tribes.append(current_tribe)            
    
    
for ass in subfamilies:
    print(ass)
    
for ass in tribes:
    print(ass)


            
#tp = TaxonPage(lepi_url, fi, "main_page")
#
#for taxon in tp.taxon_list:
#    print("---", taxon.name, "---")
#    print(taxon.link)  
#    
#    
#    if taxon.name == "Ditrysia":
#        
#        print("Ditrysia page analysis")
#        
#        tpl = TaxonPage(taxon.link, fi, taxon.name)
#        
#        for t in tpl.taxon_list:
#            print("  ", t.name)
#            print("  ", t.link)
#            
#            if t.name == "Papilionoidea":
#                
#                ptpl = TaxonPage(t.link, fi, t.name)
#                
#                for pt in ptpl.taxon_list:
#                    
#                    print(pt.name)
#                    
#                    if pt.name == "Papilionidae":
#                        
#                        pptpl = TaxonPage(pt.link, fi, pt.name)
#                        
#                        for ppt in pptpl.taxon_list:
#                            
#                            print("  ", ppt.name)
#                            print("  ", ppt.link)
                    
            


#req = RequestsHandler.Request(lepi_url, fi.cache_filename("main_page"))
#req.load()
#
#
#soup = req.get_soup()
#
#clist = soup.find("ul", {"class":"LIST"})
#
#print(len(clist))
#
#print(clist.text)
#
#names = clist.find_all("span", {"class": "TN"})
#
#family_links = []
#
#
## find the orders (?)
#
## find the links
#links = []
#for name_tag in names:
#    print(name_tag.text)
#    link_tag = name_tag.find("a")
#    link = lepi_url + link_tag.get("href")
#    links.append(link)
#    print(link)
#    
#
## find the families
#
#for link in links:
#    
#    pos = link[:-1].rfind("/")
#    
#    name = link[pos + 1:-1]
#    
#    #req = Request()
#    
#    if name == "ditrysia":
#        print(link)
#        
#        req = RequestsHandler.Request(link, fi.cache_filename(name))
#        req.load()
#        
#        soup = req.get_soup()
#        
#        # find the LIST
#        clist = soup.find("ul", {"class":"LIST"})
#        
#        # find the names
#        names = clist.find_all("span", {"class": "TN"})
#        
#        for name_tag in names:
#            print(name_tag.text)

        
        
    
    
    
