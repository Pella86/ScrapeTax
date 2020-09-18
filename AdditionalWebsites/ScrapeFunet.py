#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 11 09:57:03 2020

@author: maurop
"""

import sys

prev_dir = "../"

if prev_dir not in sys.path:
    sys.path.append(prev_dir)
    
    
import RequestsHandler
import FileInfo

lepi_url = "http://ftp.funet.fi/index/Tree_of_life/insecta/lepidoptera/"

fi = FileInfo.FileInfo("./funet", "funet", "Lepidoptera")


class Taxon:
    
    def __init__(self, name, author, link):
        self.name = name
        self.author = author
        self.link = link
        
    
class TaxonPage:
    
    def __init__(self, url, fi, page_name):
        req = RequestsHandler.Request(url, fi.cache_filename(page_name))
        req.load()
        
        soup = req.get_soup()
        
        clist = soup.find("ul", {"class":"LIST"})
        names = clist.find_all("span", {"class": "TN"})        
        
        self.taxon_list = []
        
        for name_tag in names:
            
            # find the taxon name
            name_parts = name_tag.text.split(" ", 1)
            
            
            # some names dont have an author
            if len(name_parts) == 2:
                name = name_parts[0]
                author = name_parts[1]
            else:
                name = name_parts[0]
                
            
            link_tag = name_tag.find("a")
            
            if link_tag is None:
                link = None
            else:
                link = url + link_tag.get("href")

            
            self.taxon_list.append(Taxon(name, author, link))
            
tp = TaxonPage(lepi_url, fi, "main_page")

for taxon in tp.taxon_list:
    print("---", taxon.name, "---")
    print(taxon.link)  
    
    
    if taxon.name == "Ditrysia":
        
        print("Ditrysia page analysis")
        
        tpl = TaxonPage(taxon.link, fi, taxon.name)
        
        for t in tpl.taxon_list:
            print("  ", t.name)
            print("  ", t.link)
            
            if t.name == "Papilionoidea":
                
                ptpl = TaxonPage(t.link, fi, t.name)
                
                for pt in ptpl.taxon_list:
                    
                    print(pt.name)
                    
                    if pt.name == "Papilionidae":
                        
                        pptpl = TaxonPage(pt.link, fi, pt.name)
                        
                        for ppt in pptpl.taxon_list:
                            
                            print("  ", ppt.name)
                    
            


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

        
        
    
    
    
