#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 20 12:55:37 2020

@author: maurop
"""

# small program that interacts with the bold API
#https://www.boldsystems.org/index.php/resources/api?type=taxonomy

import request_handler
import FileInfo
import json

api_url = "http://www.boldsystems.org/index.php/API_Tax/TaxonSearch"
taxonid_api_url = "http://www.boldsystems.org/index.php/API_Tax/TaxonData"


base_folder = "./Data/BOLD_test"

fileinfo = FileInfo.FileInfo(base_folder, "bold", "Mycetophilidae")


# =============================================================================
# retrive taxonomy
# =============================================================================
#
#param = {"taxName":fileinfo.family_name}
#
#req = request_handler.Request(api_url, fileinfo.pickle_filename("test"), param)
#
#res_json = req.get_json()
#
#print(json.dumps(res_json, indent=2))
#
#print("Matches:", res_json["total_matched_names"])
#
#for match in res_json["top_matched_names"]:
#    
#    print(match["taxon"])
#    
#    
## Pick the first match
#    
#family = res_json["top_matched_names"][0]
#
## use the id to get the stats
#
#param = {"taxId" : family["taxid"],
#         "dataTypes" : "all"
#         }
#
#req = request_handler.Request(taxonid_api_url, fileinfo.pickle_filename("taxid_info"), param)
#
#res_json = req.get_json()
#
#
##print(json.dumps(res_json, indent=2))
#

# =============================================================================
# retrive all the specimens they have
# =============================================================================

#import urllib
#
#api_specimen = "http://www.boldsystems.org/index.php/API_Public/specimen"
#
#param = {"taxon":"Mycetophilidae",
#         "format":"json"}
#
#param = urllib.parse.urlencode(param, quote_via=urllib.parse.quote)
#
#req = request_handler.Request(api_specimen, fileinfo.pickle_filename("api_specimen"), param)
#
#j = req.get_json()
#
#print(j["bold_records"]["records"].keys())
#
#records = j["bold_records"]["records"]
#
#first_key = list(records.keys())[0]
#
#first_record = records[first_key]
#
#print(json.dumps(first_record, indent=2))
#
#
#print(first_record["taxonomy"]["family"]["taxon"]["name"])
#print(first_record["taxonomy"]["subfamily"]["taxon"]["name"])
##print(first_record["taxonomy"]["tribe"]["taxon"]["name"])
#print(first_record["taxonomy"]["genus"]["taxon"]["name"])
#print(first_record["taxonomy"]["species"]["taxon"]["name"])
#
#
#
#def get_taxon_name(taxon, record):
#    
#    taxon = record["taxonomy"].get(taxon)
#    
#    if taxon:
#        return taxon["taxon"]["name"]
#    else:
#        return None
#    
#def get_author(record):
#    return record["taxonomy"]["species"]["taxon"].get("reference")
#
#
#class Record:
#    
#    def __init__(self, record):
#        self.record = record
#        
#        self.specie = None
#        self.genus = None
#        self.author = None
#        self.rank = None
#        
#        
#        specie_taxon = self.get_taxon("species")
#        
#        if specie_taxon:
#            self.specie = self.get_name("species").split(" ")[1]
#            self.author = self.get_author("species")
#            self.rank = Taxa.Taxa.rank_specie
#        
#        
#        genus_taxon = self.get_taxon("genus")
#        
#        if genus_taxon:
#            if specie_taxon == None:
#                self.rank = Taxa.Taxa.rank_genus
#                self.author = self.get_author("genus")
#            
#            self.genus = self.get_name("genus")
#            
#        
#        self.tribe = self.assign_name("tribe")
#        self.subfamily = self.assign_name("subfamily")
#        self.family = self.assign_name("family")
#            
#                 
#            
#    
#    def get_taxon(self, taxon_name):
#        return self.record["taxonomy"].get(taxon_name)
#
#    def get_name(self, taxon_name):
#        return self.record["taxonomy"][taxon_name]["taxon"]["name"]
#
#    def get_author(self, taxon_name):
#        return self.record["taxonomy"][taxon_name].get("reference")    
#    
#    def assign_name(self, taxon_name):
#        
#        taxon = self.get_taxon(taxon_name)
#        if taxon:
#            return self.get_name(taxon_name)
#        else:
#            return None
#        
#
#import Taxa
#
#
#print(list(records.values())[0]["taxonomy"].keys())
#
#tax_keys = ['identification_provided_by', 'identification_method', 'phylum', 'class', 'order', 'family', 'subfamily', 'genus', 'species']
#
#for record in records.values():
#    print("-"*79)
#    #print(record["taxonomy"])
#    
#    tax_list = list(record["taxonomy"].keys())
#    
#    for word in tax_list:
#        if word in tax_keys:
#            print(".", end="")
#        else:
#            print(word)
#    print()
#            
    
#    rec = Record(record)
#    
#    if rec.genus == None and rec.specie == None:
#        continue
#    
#    taxa = Taxa.Taxa()
#    
#    taxa.family = rec.family
#    taxa.subfamily = rec.subfamily
#    taxa.tribe = rec.tribe
#    taxa.genus = rec.genus
#    taxa.specie = rec.specie
#    taxa.author = rec.author
#    taxa.rank = rec.rank
#    
#    taxa.print_extended()


# =============================================================================
# scrape the taxon pages
# =============================================================================


main_page = "https://www.boldsystems.org"

taxon_search_url = "https://www.boldsystems.org/index.php/Taxbrowser_Taxonpage"

# taxon=mycetophilidae&searchTax=Search+Taxonomy
#param = {"taxon":fileinfo.family_name.lower(),
#         "searchTax":"Search Taxonomy"}
#
#req = request_handler.Request(taxon_search_url, fileinfo.pickle_filename("taxon_search"), param)
#
#req.load()
#
#soup = req.get_soup()
#
#print(soup.find("Sub"))

import Taxa

def get_children(taxid, parent_taxa = None):
    ''' The function scans the webpage with the taxid and finds the subtaxa 
        asssociated with it'''
    
    # construct the request
    param = {"taxid" : taxid}
    filename = fileinfo.pickle_filename(f"taxid_search_{taxid}")
    req = request_handler.Request(taxon_search_url, filename, param)
    
    # get the soup
    soup = req.get_soup()
    
    # Find the sections containing the sub taxa, if there are less than 6
    # sections it means that the page doesn't have sub taxa
    sections = soup.find_all("div", {"class":"col-md-6"})
    if len(sections) <= 6:
        #print("There are no subtaxa")
        return None
    else:
        subtaxa = sections[6]
    
    # Find the taxons in the sections, it can be that the subtaxa have multiple
    # ranks like a family can have genera and subfamily associated wiht it
    taxon_ranks = subtaxa.find_all("lh")
    taxons = subtaxa.find_all("ol")    
    
    # Analyze the taxons
    taxa_list = []
    
    for rank, tax in zip(taxon_ranks, taxons):
        
        # dummy taxa to insert the information that will be equal in all the
        # child taxa like source and previous taxonomy
        retrived_taxa = Taxa.Taxa()
        retrived_taxa.source = Taxa.Taxa.source_bold
        
        if parent_taxa:
            retrived_taxa.copy_taxonomy(parent_taxa)
        
        # format the rank Subfamilies (7) -> subfamilies
        frank = rank.text.split(" ")[0].lower()
        
        taxa_ranks = {"subfamilies" : Taxa.Taxa.rank_subfamily,
                      "tribes"      : Taxa.Taxa.rank_tribe,
                      "genera"      : Taxa.Taxa.rank_genus,
                      "species"     : Taxa.Taxa.rank_specie,
                      "subspecies"  : Taxa.Taxa.rank_subspecie
                      }
        
        try:
            retrived_taxa.rank = taxa_ranks[frank]
        except KeyError:
            raise Exception("Taxon rank not present")
        
            
        # once defined which rank is the taxon, then add the name to the 
        # corresponding field in the class
        # get the names associated with the rank
        
        taxon_names = tax.find_all("a")
        
        for name in taxon_names:
            
            taxa = Taxa.Taxa()
            taxa.copy_taxa(retrived_taxa)
            
            # parse the name
            
            if taxa.rank == Taxa.Taxa.rank_specie:
                text = name.text.split(" ")[1].strip()
                
            elif taxa.rank == Taxa.Taxa.rank_subspecie:
                text = name.text.split(" ")[2].strip()
            
            else:
                text = name.text.split(" ")[0].strip()

            # the "sp." is marked under species but has no designated name
            # has only a code like CB-12. There are some species taht probably
            # are provisory names that contain codes and symbols
            if text == "sp." or text == "cf." or "-" in text or "_" in text:
                continue

            # assign the name
            
            if taxa.rank == Taxa.Taxa.rank_subfamily:
                taxa.subfamily = text

            elif taxa.rank == Taxa.Taxa.rank_tribe:
                taxa.tribe = text
            
            elif taxa.rank == Taxa.Taxa.rank_genus:
                taxa.genus = text
            
            elif taxa.rank == Taxa.Taxa.rank_specie:
                taxa.specie = text
            
            elif taxa.rank == Taxa.Taxa.rank_subspecie:
                taxa.subspecie = text

            else:
                raise Exception("Taxon rank not present")
            
            link = main_page + name.get("href")
            taxa.links.append(link)
            
            taxa_list.append(taxa)
    
    return taxa_list
                


def get_id_from_taxa(taxa):
    ''' small function to retrive the id from the source link
        source link: https://www.boldsystems.org/index.php/Taxbrowser_Taxonpage?taxid=596013
    '''
    
    # select the link
    link = taxa.links[0]
    # find where taxid is 
    pos_taxid = link.find("taxid")    
    # cut the string sto that only the id remains
    taxid = int(link[pos_taxid + len("taxid") + 1 :])
    
    return taxid


taxa_list = []

# generate a taxa for the family

# get taxa related to family
family_id = 168441
family_taxa_list = get_children(family_id)

taxa_list += family_taxa_list

for ftaxa in family_taxa_list:
    
    subfamily_taxa = get_children(get_id_from_taxa(ftaxa), ftaxa)
    
    if subfamily_taxa:
        
        taxa_list += subfamily_taxa
    
        for staxa in subfamily_taxa:
            
            tribes_taxa = get_children(get_id_from_taxa(staxa), staxa)
            
            if tribes_taxa:
                
                taxa_list += tribes_taxa
            
                for gtaxa in tribes_taxa:
                    
                    genus_taxa = get_children(get_id_from_taxa(gtaxa), gtaxa)
                    
                    if genus_taxa:
                        
                        taxa_list += genus_taxa
                        
                        for sptaxa in genus_taxa:
                            
                            subspecie_taxa = get_children(get_id_from_taxa(sptaxa), sptaxa)
                            
                            if subspecie_taxa:
                                
                                taxa_list += subspecie_taxa
    
    
        
print(len(taxa_list))        


for taxa in taxa_list:
    if taxa.rank == Taxa.Taxa.rank_specie:
        taxa.print_extended()      
            

#def get_children_recursive(taxid, taxa_list):
#    
#    tlist = get_children(taxid)
#    
#    if tlist:
#        taxa_list += tlist
#        for t in taxa_list:    
#            return get_children_recursive(get_id_from_taxa(t), taxa_list)
#    
#    else:
#        return taxa_list
#    
#
#l = get_children_recursive(family_id, [])
        

