#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  8 10:34:04 2020

@author: maurop
"""

import os

class CSVFile:
    '''Class that manages a CSV file'''
    
    line_break = "\n"
    separator = ","
    bom = "\ufeff" # byte order mark
    
    def __init__(self, filename):
        self.filename = filename
        self.data = ""
    
    def prepare_line(self, data_list):
        quoted_data = map(lambda t :  f'"{t}"', data_list)
        s = self.separator.join(quoted_data) + self.line_break
        return s
    
    def add_line(self, data_list):
        ''' Given an array of values the program writes them separated by comma
        enclosed in quotes, the function writes the file as soon as this
        operation is called'''

        self.data += self.prepare_line(data_list)      
        
        self.write()

    def write(self):
        with open(self.filename, "wb") as f:
            
            # add the byte order mark if is not present
            if not self.data.startswith(self.bom):
                self.data = self.bom + self.data
            # write the file
            f.write(self.data.encode("utf8"))
        
    def write_table(self, table):
        ''' Given a matrix of rows and columns, the program will save each
        row as a line and each column as a comma separated value'''
        lines = []
        for row in table:
            line = self.prepare_line(row)
            lines.append(line)
            
        self.data = "".join(lines)

        self.write()
            
    
    def read(self):
        if os.path.isfile(self.filename):
            with open(self.filename, "r") as f:
                self.data = f.read()
                
                self.data = str(self.data).replace("\ufeff", "")
                
    def get_table(self):
        self.read()
        if self.data:
            lines = self.data.split(self.line_break)
            
            return list(map(lambda line : self.get_columns(line), lines))


    def get_columns(self, line):     
        ''' Given a comma separated strings the function returns the separated data
        in a list '''
        
        # resulting columns
        col = []
        
        # column content
        dstr = ""
        
        # the data can be surrounded by " quotes and the commas inside the quotes
        # are ignored
        
        # if is inside the double "..." quotes
        state_inside = False
        
        for c in line:
            
            if state_inside:
                # keep the state True until an other quote is found
                if c == '"':
                    state_inside = False
                    continue
                
            else:
                
                # if a quote is found trigger the inside state
                if c == '"':
                    state_inside = True
                    continue
                
                # reset the string and append the data string to the resulting columns
                if c == ",":
                    col.append(dstr)    
                    dstr = ""
                    continue
            
            dstr += c
        col.append(dstr)
        return col
    

    def exists(self):
        return True if os.path.isfile(self.filename) else False