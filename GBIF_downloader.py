#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  8 10:28:00 2020

@author: maurop
"""

import request_handler
import json
import os

import Taxa
import AuthorityFileCreation
import FileInfo

api_url = "https://api.gbif.org/v1"


species = "/species/"

match = "/species/match/"

def children_url(key):
    return f"{api_url}/species/{key}/children"

param = {}
param["name"] = "Mycetophilidae"



req = request_handler.Request(api_url + match, "./Data/GBIF_test/test_myceto.pickle", param)

req.load()

'''{'usageKey': 5565, 'scientificName': 'Mycetophilidae', 'canonicalName': 'Mycetophilidae', 'rank': 'FAMILY', 'status': 'ACCEPTED', 'confidence': 94, 'matchType': 'EXACT', 'kingdom': 'Animalia', 'phylum': 'Arthropoda', 'order': 'Diptera', 'family': 'Mycetophilidae', 'kingdomKey': 1, 'phylumKey': 54, 'classKey': 216, 'orderKey': 811, 'familyKey': 5565, 'synonym': False, 'class': 'Insecta'}'''

myceto_json = req.response.json()



req = request_handler.Request(api_url + species + str(myceto_json["familyKey"]) + "/", "./Data/GBIF_test/test_family_new.pickle")

req.load()

myceto_family = req.response.json()


#print(json.dumps(req.response.json(), indent = 2, sort_keys = True))

limit_param = {}
limit_param["limit"] = myceto_family["numDescendants"]

req = request_handler.Request(children_url(myceto_json["familyKey"]), "./Data/GBIF_test/test_children_limit.pickle", limit_param)

req.load()

'''   "authorship": "Hutton, 1904",
      "canonicalName": "Anomalomyia",
      "class": "Insecta",
      "classKey": 216,
      "constituentKey": "7ddf754f-d193-4cc9-b351-99906754a03b",
      "datasetKey": "d7dddbf4-2cf0-4f39-9b2a-bb099caae36c",
      "family": "Mycetophilidae",
      "familyKey": 5565,
      "genus": "Anomalomyia",
      "genusKey": 1615502,
      "issues": [],
      "key": 1615502,
      "kingdom": "Animalia",
      "kingdomKey": 1,
      "lastCrawled": "2019-09-06T05:41:48.812+0000",
      "lastInterpreted": "2019-09-06T04:35:55.714+0000",
      "nameKey": 709396,
      "nameType": "SCIENTIFIC",
      "nomenclaturalStatus": [],
      "nubKey": 1615502,
      "numDescendants": 13,
      "order": "Diptera",
      "orderKey": 811,
      "origin": "SOURCE",
      "parent": "Mycetophilidae",
      "parentKey": 5565,
      "phylum": "Arthropoda",
      "phylumKey": 54,
      "publishedIn": "Index Faunae N. Zealand",
      "rank": "GENUS",
      "remarks": "",
      "scientificName": "Anomalomyia Hutton, 1904",
      "sourceTaxonKey": 156980061,
      "synonym": false,
      "taxonID": "gbif:1615502",
      "taxonomicStatus": "ACCEPTED"
'''

#print(json.dumps(req.response.json(), indent = 1, sort_keys = True))


myceto_genus = req.response.json()

print(myceto_family["numDescendants"], len(myceto_genus["results"]))


genus_list = []
species_list = []

def generate_specie_mp_taxa(specie, mp_taxa_parent_genus):
    name = specie["scientificName"].replace(specie["authorship"], "")
    author = specie["authorship"]
    specie_id = specie["speciesKey"]
    link = f"{api_url}/species/{specie_id}"
    
    return Taxa.Taxa(name, author, link, mp_taxa_parent_genus)
    
    

for taxon in myceto_genus["results"]:
    
    if taxon["rank"] == "GENUS":
        print(taxon["rank"], taxon["scientificName"]) 
        
        name = taxon["scientificName"].replace(taxon["authorship"], "")
        author = taxon["authorship"]
        genus_id = taxon["genusKey"]
        link = f"{api_url}/species/{genus_id}"
        tax = Taxa.Taxa(name, author, link, None)
        
        genus_list.append(tax)
        
        
        limit_param["limit"] = taxon["numDescendants"]
        
        req = request_handler.Request(children_url(genus_id), os.path.join("./Data/GBIF_test", name + ".pickle"), param)
        
        req.load()
        
        species_response = req.response.json()
        
        for specie in species_response["results"]:
            #print(json.dumps(specie, indent=2))
            if specie["rank"] == "SPECIES":
                stax = generate_specie_mp_taxa(specie, tax)
            
                species_list.append(stax)
    
    if taxon["rank"] == "SPECIES":
        stax = generate_specie_mp_taxa(taxon, None)
        species_list.append(stax)
        

for taxa in species_list:
    print(taxa)
        
        
fileinfo = FileInfo.FileInfo("./Data/GBIF_test", "mycetophilidae")       
AuthorityFileCreation.generate_authority_list(genus_list, species_list, fileinfo)    
    
    
    
    