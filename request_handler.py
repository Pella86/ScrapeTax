# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 09:46:56 2020

@author: maurop
"""

import requests
import bs4
import os
import pickle
import logging


logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)



# add ch to logger
if not logger.hasHandlers():
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    
    # create formatter
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    
    # add formatter to ch
    ch.setFormatter(formatter)
    logger.addHandler(ch)

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
        logger.debug("Downloading data from:" + self.url)
        self.response = requests.get(self.url, params=self.params)
        logger.debug("Response status: " + str(self.response))
    
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
            logger.debug("Loading data from file: " + self.filename)
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