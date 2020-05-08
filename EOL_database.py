#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  5 10:17:57 2020

@author: maurop
"""

import requests
import os
import tarfile
import pickle

import ProgressBar

database_url = "https://editors.eol.org/other_files/DWH/TRAM-809/DH_v1_1.tar.gz"

database_storage_folder = "./Data/EOL_database"

tarball_filename = "eol_database.tar.gz"


insect_db_pathname = "./Data/EOL_database/insecta_db.pickle"


tarball_filepath = os.path.join(database_storage_folder, tarball_filename)

database_filepath = os.path.join(database_storage_folder, "taxon.tab")



''' Data example
   {'taxonID': 'EOL-000000000001',
    'source': 'trunk:1bfce974-c660-4cf1-874a-bdffbf358c19,NCBI:1',
    'furtherInformationURL': '',
    'acceptedNameUsageID': '',
    'parentNameUsageID': '',
    'scientificName': 'Life',
    'higherClassification': '',
    'taxonRank': 'clade',
    'taxonomicStatus': 'valid',
    'taxonRemarks': '',
    'datasetID': 'trunk',
    'canonicalName': 'Life',
    'EOLid': '2913056',
    'EOLidAnnotations': ''}'''



# Request the database (will be in tarball format)
if os.path.isfile(tarball_filepath):
    print("database already downloaded")
else:
    print("downloading database...")
    database_request = requests.get(database_url)
    print(database_request)
    
    with open(tarball_filepath, "wb") as f:
        f.write(database_request.content)
    print("download complete")

# extract the tarball format
if os.path.isfile(database_filepath):
    print("database already extracted")
else:
    print("extracting database...")
    tar = tarfile.open(tarball_filepath)
    tar.extractall(path=database_storage_folder)
    tar.close()
    print("database extracted")
    

insect_taxons = []
if os.path.isfile(insect_db_pathname):
    print("Opening insects database...", end="")
    with open(insect_db_pathname, "rb") as f:
        insect_taxons = pickle.load(f)
    print("OK")
else:

    with open(database_filepath, "rb") as f:
        
        #headers
        headers = f.read(206).decode("utf8").strip().split("\t")
    
        print("reading file...", end=" ")
        bcontent = f.read()
        print("OK")
        
        print("decoding...", end=" ")
        scontent = bcontent.decode("utf8")
        print("OK")
        
        
        field = ""
        db_data = {}
        field_n = 0
        taxon = []
        
        pbar = ProgressBar.ProgressBar(len(scontent))
        
        pbar.draw_bar(0)
        
        for i, c in enumerate(scontent):
    
            if c == "\t":
                db_data[headers[field_n]] = field
                field_n += 1
                
                field = ""
                
                continue
            
            if c == "\n":
                field_n = 0
                
                if i % 1e5 == 0:
                    pbar.draw_bar(i)
                    
                
                if "Insecta" in db_data["higherClassification"]:
                    taxon.append(db_data)
                    
                
                db_data = {}
                continue
            
            field += c
        
        pbar.draw_bar(len(scontent))
        print()
    
        print("writing pickle database... ", end="")
        with open(insect_db_pathname, "wb") as f:
            pickle.dump(taxon, f)
        print("OK")
        
        insect_taxons = taxon

print("Total number of insects taxons:", len(insect_taxons))
for taxa in insect_taxons:
    if "Vespidae" in taxa["higherClassification"]:
        if taxa["taxonRank"] == "genus":
            print(taxa)
            break
        
    
#    lines = scontent.split("\n")
#    
#    print("split the data")
#        
#    taxons = []
#    
#    pbar = ProgressBar.ProgressBar(len(lines))
#    
#    for i, line in enumerate(lines):
#        fields = line.split("\t")
#        
#        database_data = {}
#        for header, field in zip(headers, fields):
#            database_data[header] = field
#        taxons.append(database_data)
#        pbar.draw_bar(i)
#    
#    # clean the database for insects
#    # search parentNameUasgeID until find Insects
#    print("Insecta entry")
#    for taxa in taxons:
#        if taxa["scientificName"] == "Insecta":
#            print(taxa)
            
    
    