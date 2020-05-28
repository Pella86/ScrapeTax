# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 10:02:11 2020

@author: maurop
"""

import os
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


class FileInfo:
    ''' Class that manages files and folders'''
    
    def __init__(self, base_path, source_website, family_name):
        # Family first letter must be capitalized
        if family_name[0].islower():
            raise Exception("FileInfo: family_name is not capitalized")
            
        self.family_name = family_name
        self.prefix = source_website + "_" + self.family_name.lower()
        
        # create a folder with the family name (e.g. ./base_path/Familyname)
        self.base_path = os.path.join(base_path, self.family_name)
        if os.path.isdir(self.base_path):
            logger.debug("Folder already present")
        else:
            os.mkdir(self.base_path)
    
    def mptaxa_exists(self, name):
        return os.path.isfile(self.mptaxa_filename(name))

    def filename(self, name, extention):
        fname = f"{self.prefix}_{name}.{extention}"
        return os.path.join(self.base_path, fname)
    
    def html_filename(self, name):
        return self.filename(name, "html")
    
    def pickle_filename(self, name):
        return self.filename(name, "pickle")
    
    def mptaxa_filename(self, name):
        return self.filename(name, "mptaxa")
    
    def csv_filename(self, name):
        return self.filename(name, "csv")
    


if __name__ == "__main__":
    
    
    fi = FileInfo("./Data/", "fi", "FileInfoTest")
    
    print(fi.pickle_filename("webpage"))
    
        