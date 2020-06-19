# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 10:02:11 2020

@author: maurop
"""

#import os
#import logging
#
#logger = logging.getLogger(__name__)
#
#logger.setLevel(logging.INFO)
#
## add ch to logger
#if not logger.hasHandlers():
#    ch = logging.StreamHandler()
#    ch.setLevel(logging.DEBUG)
#    
#    # create formatter
#    formatter = logging.Formatter('%(levelname)s - %(message)s')
#    
#    # add formatter to ch
#    ch.setFormatter(formatter)
#    logger.addHandler(ch)


import os
import LogFiles

log = LogFiles.Logger(__name__)


class FileInfo:
    ''' Class that manages files and folders'''
    
    def __init__(self, base_path, source_website, family_name):
        # Family first letter must be capitalized
        if family_name[0].islower():
            log.log("family_name is not capitalized")
            raise Exception("FileInfo: family_name is not capitalized")
            
        self.family_name = family_name
        self.prefix = source_website + "_" + self.family_name.lower()
        
        # create a folder with the family name (e.g. ./base_path/Familyname)
        self.base_path = os.path.join(base_path, self.family_name)
        
        if os.path.isdir(self.base_path):
            log.main_log("Folder already present: " + self.base_path)
        else:
            log.main_log("created folders: " + self.base_path)
            os.makedirs(self.base_path)
    
    def mptaxa_exists(self, name):
        return os.path.isfile(self.mptaxa_filename(name))
    
    def format_name(self, name, extention):
        return f"{self.prefix}_{name}.{extention}"

    def filename(self, name, extention):
        fname = self.format_name(name, extention)
        return os.path.join(self.base_path, fname)
    
    def html_filename(self, name):
        return self.filename(name, "html")
    
    def pickle_filename(self, name):
        return self.filename(name, "pickle")
    
    def mptaxa_filename(self, name):
        return self.filename(name, "mptaxa")
    
    def csv_filename(self, name):
        return self.filename(name, "csv")
    
    def txt_filename(self, name):
        return self.filename(name, "txt")
    
    def cache_filename(self, name):
        # generate a subfolder named cache
        cache_subfolder = os.path.join(self.base_path, "cache/")
        if not os.path.isdir(cache_subfolder):
            log.main_log("Created chache folder")
            os.mkdir(cache_subfolder)
        
        return os.path.join(cache_subfolder, self.format_name(name, "pickle"))
    
    def name_only(self, name):
        return os.path.join(self.base_path, name)
        
    


if __name__ == "__main__":
    
    
    fi = FileInfo("./Tests/test_Fileinfo", "fi", "FileInfoTest")
    
    print(fi.pickle_filename("webpage"))
    
        