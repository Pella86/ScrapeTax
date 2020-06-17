# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 09:46:56 2020

@author: maurop
"""

# =============================================================================
# Imports
# =============================================================================

import requests
import bs4
import os
import pickle
import LogFiles

# =============================================================================
# Logging
# =============================================================================

logger = LogFiles.Logger(__name__)

# =============================================================================
# Request class:
#   handles the requests to the website, saves a copy of the files under
#   effectively caching the files fromt the website
# =============================================================================

class Request:
    
    def __init__(self, url, filename, params = None):
        self.url = url
        self.response = None
        self.filename = filename
        self.params = params
    
    def download(self):
        ''' Makes a connection to the website and downloads the webpage'''
        logger.main_log("sending request...")
        self.response = requests.get(self.url, params=self.params)
        logger.main_log("Downloaded data from: " + self.response.request.url)
        logger.main_log("Response status: " + str(self.response))
    
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
            logger.main_log("Loading data from file: " + self.filename)
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
        
    def get_json(self):
        if self.response == None:
            self.load()
        return self.response.json()
    
    def get_soup(self):
        if self.response == None:
            self.load()
        return bs4.BeautifulSoup(self.response.text, "html.parser")
    
    def get_html(self):
        return self.response.text


def load_request(url, filename):
    req = Request(url, filename)
    req.load()
    return req.response
        
        
def get_soup(url, filename):
    response = load_request(url, filename)
    return bs4.BeautifulSoup(response.text, "html.parser")


def get_json(url, filename):
    response = load_request(url, filename)
    return response.json()