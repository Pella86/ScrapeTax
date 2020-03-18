# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 10:07:07 2020

@author: Media Markt
"""


class Taxa:
    
    def __init__(self, name, author, link, supertaxa):
        self.name = str(name)
        self.author = str(author)
        self.link = link
        self.super_taxa = supertaxa
        
    def __str__(self):
        return self.name + " | " + self.author    