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
import CSVFile

# =============================================================================
# Constants
# =============================================================================

lepi_url = "http://ftp.funet.fi/index/Tree_of_life/insecta/lepidoptera/"

#fi = FileInfo.FileInfo("./funet", "funet", "Lepidoptera")

# =============================================================================
# Generic taxon class when the rank is unkown
# =============================================================================

class Taxon:
    
    def __init__(self, name, author, link):
        self.name = name
        self.author = author
        self.link = link
    
    def __str__(self):
        return self.name

# =============================================================================
# Associated taxa
# =============================================================================

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
        associates_str = ", ".join(self.associates if self.associates else "No genera associated")
        if associates_str.endswith(", "):
            associates_str = associates_str[:-2]
        return "- " + self.main_taxa + ": " + associates_str


# =============================================================================
# Main taxon page     
# =============================================================================

class TaxonPage:
    ''' Funet taxon page: the pages can have different structures'''

    fi = FileInfo.FileInfo("./funet", "funet", "Lepidoptera")
    
    def __init__(self, url):
        
        # the page url
        self.url = url
        
        # generate page name from url (use the last name in the url)
        pos = self.url[:-1].rfind("/")
        name = self.url[pos + 1 : -1]        
        self.page_name = name
        
        # pull the request
        req = RequestsHandler.Request(self.url, self.fi.cache_filename(self.page_name))
        req.load()
        
        self.soup = req.get_soup()     
    
    def is_structured(self):
        ''' if in the page there is a GROUP class it means that the page
            is layered'''
        if self.soup.find("div", {"class":"GROUP"}):
            return True
        else:
            return False
    
    
    def parse_LIST(self, ul_element):
        ''' This function parses the list in the page, the list in general
        contains the name and authors information, returns a list of Taxon'''
        
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
                
            # link to the taxon page
            link_tag = name_tag.find("a")
            
            if link_tag is None:
                link = None
            else:
                # this goes one level deeper
                link = self.url + link_tag.get("href")
    
            taxon_list.append(Taxon(name, author, link))    
        return taxon_list
        


class TaxonPageNormal(TaxonPage):
    ''' If the page is not structured extract the information'''
    
    def __init__(self, url):
        super().__init__(url)
        
        clist = self.soup.find("ul", {"class":"LIST"})
            
        self.taxon_list = self.parse_LIST(clist)        
        

class TaxonPageStructured(TaxonPage):
    
    ''' For structured pages the information needs to be parsed differently
    this will have groups'''
    
    
    def __init__(self, url):
        super().__init__(url)

        body = self.soup.find("body")
        
        # finds all the first level elements
        chirren = body.findChildren(recursive=False)
        
        # this will have all the groups in the page
        group_list = []
        current_group = None
        children = []
        
        for ele in chirren:
            
            # if it is a current_group, it means that this is a higher taxonomy
            if ele.name == "div" and ele.has_attr('class') and ele['class'][0] == 'GROUP':
                if current_group is not None:
                    group_list.append((current_group, children))
                    children = []
                
                # parse the group
                current_group = self.parse_GROUP(ele)
             
            # else is a normal list of taxons
            if ele.name == "ul" and ele.has_attr("class") and ele["class"][0] == "LIST":
                
                children = self.parse_LIST(ele)
                
       
        group_list.append((current_group, children))

    
        current_tribe = None
        current_subfamily = None  

        tribes = []
        subfamilies = []        
    
        for group, children in group_list:
            
            if group is None:
                print("group is none")
                print(group)
                print(children)
                continue
            
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

        if current_tribe:
            tribes.append(current_tribe)
        
        if current_subfamily:
            subfamilies.append(current_subfamily)


        self.subfamilies = subfamilies
        self.tribes = tribes

    def parse_GROUP(self, div_element):
        
        tag = div_element.find("span", {"class":"TN"})
        
        if tag is not None:
            text_parts = tag.text.split(" ")
            
            rank = text_parts[0]
            name = text_parts[1]
            author = " ".join(text_parts[2:])
            
            group = (rank, name, author)
            return group


# =============================================================================
# Tree class        
# =============================================================================

class Node:
    ''' Each page is a node, the page can be normal or structured, the page
    contains sub pages as leafs of the graph'''
    
    def __init__(self, taxon_page):
        
        self.page = taxon_page
        self.subpages = []
        
        # the subpages collection stops at the families
        if self.page.page_name.endswith("idae"):
            pass
        else:
            for taxon in self.page.taxon_list:
                
                if taxon.link == None:
                    continue
                
                tp = TaxonPageNormal(taxon.link)

                self.subpages.append(Node(tp))
       

class Tree:
    
    ''' The tree is used to navigate under the lepidoptera page, and find 
    the corresponding family page'''
    
    
    def __init__(self):
        tp = TaxonPageNormal(lepi_url)
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
            
            if node.page.page_name == family_name.lower():
                result.append(node.page.url)
            else:
                self.get_family_node(node, family_name, result)
    
    def get_family_link(self, family_name):
        result = []
        self.get_family_node(self.root, family_name, result)
        if len(result) == 1:
            return result[0]
        else:
            raise Exception("Name not found:", family_name)


class Associations:
    
    def __init__(self):
        self.tree = Tree()
  

    def find_associations(self, family_name):
        
        tp_url = self.tree.get_family_link(family_name)
        
        print(tp_url)
        
        tp = TaxonPage(tp_url)
        
        if tp.is_structured():
            print("Page is structured")
            ts = TaxonPageStructured(tp_url)
            return ts.subfamilies, ts.tribes
        
        else:
            print("Page is normal")
            tn = TaxonPageNormal(tp_url)
            
            subfamilies = []
            tribes = []
            
            for taxon in tn.taxon_list:
                print(taxon.link)
                
                taxon_page = TaxonPage(taxon.link)
                
                if taxon_page.is_structured():
                
                    children_page = TaxonPageStructured(taxon.link)
                    print(children_page.tribes)
                    
        
                    tribes += children_page.tribes
        
                    atax = AssociatedTaxa(taxon, "subfamily")
                    for tribe in children_page.tribes:
                        for tax in tribe.associates:
                            atax.add_associate(tax)
                    
                    subfamilies.append(atax)   
                else:
                    children_page = TaxonPageNormal(taxon.link)
                    
                    atax = AssociatedTaxa(taxon, "subfamily")
                    for tx in children_page.taxon_list:
                        atax.add_associate(tx)
                    
                    subfamilies.append(atax)   
                    tribes = None                    
                
            
            return subfamilies, tribes
    
    


        






if __name__ == "__main__":
    
#    normal_url = "http://ftp.funet.fi/index/Tree_of_life/insecta/lepidoptera/ditrysia/"
#    
#    tpage = TaxonPageNormal(normal_url)
#    
#    for t in tpage.taxon_list:
#        print(t)
#    
#    stuctured_url = "http://ftp.funet.fi/index/Tree_of_life/insecta/lepidoptera/ditrysia/papilionoidea/riodinidae/"
#    
#    tpage = TaxonPageStructured(stuctured_url)
    
    family_name = "Nepticulidae"
    
    ass = Associations()
    
    subfamilies, tribes = ass.find_associations(family_name)
        
    print("--- subfamilies ---")
    for sub in subfamilies:
        print(sub)
    
    print("--- tribes ---")
    for tribe in tribes:
        print(tribe)
        
    csv = CSVFile.CSVFile("./funet/" + family_name + "_subfamiles_tribes.csv")
    
    csv.add_line(["Subfamily", "Tribe", "Genus"])
    
    
    tot_genus = []
    
    for sub in subfamilies:
        for genus in sub.associates:
            tot_genus.append(genus)
    
    for tribe in tribes:
        for genus in tribe.associates:
            if genus not in tot_genus:
                tot_genus.append(genus)
            
    for genus in tot_genus:
        line = ["", "", ""]
        line[2] = genus
        
        for sub in subfamilies:
            if genus in sub.associates:
                line[0] = sub.main_taxa.name
                break
        
        for tribe in tribes:
            if genus in tribe.associates:
                line[1] = tribe.main_taxa
                break
        print(line)
        
        csv.add_line(line)

            
    
    
    
    
    
    
    
    
    
    
    
    
