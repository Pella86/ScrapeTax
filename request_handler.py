# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 09:46:56 2020

@author: Media Markt
"""

import requests
import bs4
import os
import pickle

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
    
    def download(self, params = None):
        ''' Makes a connection to the website and downloads the webpage'''
        print("Downloading data from:", self.url)
        self.response = requests.get(self.url, params=params)
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
        
        
def get_soup(url, filename):
    req = Request(url, filename)
    req.load()
    return bs4.BeautifulSoup(req.response.text, "html.parser")