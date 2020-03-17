#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 09:21:27 2020

@author: maurop
"""
# =============================================================================
# Imports
# =============================================================================

import requests
import bs4
import pickle
import os

import name_formatting

# =============================================================================
# Request class:
#   handles the requests to the website, saves a copy of the files under
#   effectively caching the files fromt the website
# =============================================================================

class Request:
    
    def __init__(self, url, filename):
        self.url = url
        self.response = None
        self.filename = filename
    
    def download(self):
        ''' Makes a connection to the website and downloads the webpage'''
        print("Downloading data from:", self.url)
        self.response = requests.get(self.url)
        print("Response status: ", self.response)
    
    def save(self):
        ''' saves the requested webpage to the disk under filename '''
        
        if self.response == None:
            raise Exception("Response is empty")

        with open(self.filename, "wb") as f:
            pickle.dump(self.response, f)
    
    def load(self):
        ''' Checks if there is a file on the hard disk and loads it, if the
            file is not there downloads the webpage and saves it on the disk''' 
        if os.path.isfile(self.filename):
            print("Loading data from file:", self.filename)
            with open(self.filename, "rb") as f:
                self.response = pickle.load(f)
        else:
            self.download()
            self.save()
    
    def reload(self):
        ''' Forces the download and save again '''
        self.download()
        self.save()       
            
    def show_url(self):
        print(self.url)
        
        
# =============================================================================
# Taxa class:
#   The class is a container for the taxas, is still under construction
# =============================================================================

class Taxa:
    
    def __init__(self, name, author, link):
        self.name = str(name)
        self.author = str(author)
        self.link = link
        
    def __str__(self):
        return self.name + " | " + self.author    


# =============================================================================
# Parse the NBN pages
# =============================================================================
    
# returns the html names

def gather_child_taxa(url, filename):
    # download the website
    req = Request(url, filename)
    req.load()
    
    soup = bs4.BeautifulSoup(req.response.text, "html.parser")
    
    # search for the child taxa section that contains all the names
    children = soup.find("dl", class_="child-taxa")
    
    # names with hierarchy tags (subfamily, genus, ...)
    dts = children.find_all("dt")
    
    # the real names
    dds = children.find_all("dd")
    
    if len(dts) != len(dds):
        raise Exception("Gather child taxa: dts / dds different length")
    
    print("Child taxa found:", len(dts))

    # return the zipped
    return zip(dts, dds)



# hierarchy tag should be "known" so it could be defined in an external file

def parse_html_taxa(taxa, hierarchy_tag):
    
    taxa_names = []
    
    for html_tag, html_name in taxa:
        
        current_hirerarchy_tag = html_tag.get_text()
        
        if current_hirerarchy_tag == hierarchy_tag:
            name = html_name.find("span", class_="name").get_text()
            author = html_name.find("span", class_="author").get_text()
            link = html_name.find("a").get("href")
            
            taxa_names.append(Taxa(name, author, link))
    
    return taxa_names


nbn_home = "https://species.nbnatlas.org"   
        
#nbn_myceto = nbn_home + '/species/NBNSYS0000160474#names'
nbn_myceto = nbn_home +  '/species/NBNSYS0000050803#classification'


url = nbn_myceto
filename = "nbn_vespidae.pickle"

genus_names = gather_child_taxa(url, filename)

genus_list = parse_html_taxa(genus_names, "genus")

for genus in genus_list:
    print(genus.name, end=', ')

    start = genus.link.rfind("/")
    end = genus.link.find("#")
    filename = genus.link[start+1:end] + ".pickle"   
    
    species_names = gather_child_taxa(nbn_home + genus.link, filename)
    
    species_list = parse_html_taxa(species_names, "species")    
    
    


genus = genus_list[0]

print(genus)
print(genus.link)

start = genus.link.rfind("/")
end = genus.link.find("#")
filename = genus.link[start+1:end] + ".pickle"     

print(filename)


species_names = gather_child_taxa(nbn_home + genus.link, filename)

species_list = parse_html_taxa(species_names, "species")


for specie in species_list:
    print(specie)



cl = name_formatting.LabelsTable()

cl.generate_table(species_list)
cl.generate_html("myceto_lables_test.html")
            


#print("Compose genus list")        
#
#genus_list = []
#
#for hierarchy_name, dd in genus_names:
#    name = dd.find("span", class_="name")
#    author = dd.find("span", class_="author")
#    link = dd.find("a")
#    
#    if hierarchy_name.get_text() == "genus":
#        genus = GenusNBN(name.get_text(), author.get_text(), link.get("href"))
#        genus_list.append(genus)
#
#with open("myceto species.txt", "w") as f:
#    for genus in genus_list:
#        print(genus)
#        print(genus.link)
#        
#        # visit the pages corresponding to the genus and extract the species
#        start = genus.link.find("NBN")
#        end = genus.link.find("#")
#        filename = genus.link[start:end] + ".pickle"
#        
#        species_names = gather_child_taxa(nbn_home + genus.link, filename)
#        
#        print(species_names)
#        
#        
#        for hierarchy_name, info in species_names:
#            print("------------")
#            
#            name = info.find("span", class_="name")
#            author = info.find("span", class_="author")
#            
#            if hierarchy_name.get_text() == "species":
#                if name is not None and author is not None:
#                    print(name.get_text(), author.get_text())
#                    f.write( name.get_text() + " " + author.get_text() + "\n")



# =============================================================================
# Previous shit
# =============================================================================

        
#class Genus:
#    
#    def __init__(self, name, author):
#        self.name = str(name)
#        self.author = str(author)
#        
#    def __str__(self):
#        return self.name + " | " + self.author
#        
#class GenusNBN(Genus):
#    
#    def __init__(self, name, author, link):
#        super().__init__(name, author)
#        
#        self.link = link



        
## Query the site for the micetophilidae family        
#
#eol_address = 'https://eol.org/api/search/1.0.json?'
#q = 'q=Mycetophilidae'
#page = 'page=1'
#key = 'key='
#et = '&' 
#
#url = eol_address + q + et + page + et + key
#
#req = Request(url, "myceto_home_page.pickle")
#req.load()
#
#main_query_json = req.response.json()
#
## find the mycetophilidae classification tree
#
#myceto_main_page_url = main_query_json['results'][0]['link']
#
#
#myceto_names_url = myceto_main_page_url + "/names"
#
#
#req = Request(myceto_names_url, "myceto_names.pickle")
#req.show_url()
#req.load()
#
#
## parse the page
#
#soup = bs4.BeautifulSoup(req.response.text, "html.parser")
#
## try to find the div containing the hierarchy
#
#divs = soup.find_all("div")
#
#print(len(divs))
#
#for i, div in enumerate(divs):
#    #print(div)
#    text = div.get_text()
#    if "EOL Dynamic Hierarchy 1.1" in text and "Mycetophilidae" in text:
#        print("FOUND", i)
#        print(text.replace('\n', ' ')[: 70])
#        
#        
#tree = str(divs[16])
#
#tree_bs = bs4.BeautifulSoup(tree, 'html.parser')
#tree_divs = tree_bs.find_all('div')
#
#for div in tree_divs:
#    if "Mycetophilidae" not in div:
#        print("-----")
#        print(div.get_text().replace('\n', ' ')[:50])