#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  5 10:17:57 2020

@author: maurop
"""

import requests
import os
import tarfile

import ProgressBar

database_url = "https://editors.eol.org/other_files/DWH/TRAM-809/DH_v1_1.tar.gz"

database_storage_folder = "./Data/EOL_database"

tarball_filename = "eol_database.tar.gz"

tarball_filepath = os.path.join(database_storage_folder, tarball_filename)

database_filepath = os.path.join(database_storage_folder, "taxon.tab")



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


with open(database_filepath, "rb") as f:
    
    #headers
    headers = f.read(206).decode("utf8").strip().split("\t")

    
    bcontent = f.read(2000)
    print("read the file")
    
    scontent = bcontent.decode("utf8")
    
    lines = scontent.split("\n")
    
    print("split the data")
    taxons = []
    
    pbar = ProgressBar.ProgressBar(len(lines))
    
    for i, line in enumerate(lines):
        fields = line.split("\t")
        
        database_data = {}
        for header, field in zip(headers, fields):
            database_data[header] = field
        taxons.append(database_data)
        pbar.draw_bar(i)
    
    # clean the database for insects
    # search parentNameUasgeID until find Insects
    print("Insecta entry")
    for taxa in taxons:
        if taxa["scientificName"] == "Insecta":
            print(taxa)
            
    
    