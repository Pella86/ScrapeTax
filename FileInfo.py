# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 10:02:11 2020

@author: maurop
"""

import os


class FileInfo:
    
    def __init__(self, base_path, prefix):
        self.base_path = base_path
        self.prefix = prefix
    
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