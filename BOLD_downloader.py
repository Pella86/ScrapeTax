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


param = {"taxid":168441}

req = request_handler.Request(taxon_search_url, fileinfo.pickle_filename("taxon_id_search"), param)

soup = req.get_soup()

print(soup.select("body > div.page-container > div.bloc.l-bloc.bgc-white > div "))




