#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 10:20:34 2020

@author: maurop
"""

import logging
import time


run_log_filename = None

class Logger:
    
    application_log_file = "./log_file.log"
    
    
    
    
    # flags
    level_DEBUG = 0
    level_INFO = 1
    
    
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        if not self.logger.hasHandlers():
            
            # console handler
            ch = logging.StreamHandler()
            
            console_formatter = logging.Formatter("%(message)s")
            ch.setFormatter(console_formatter)
            
            self.logger.addHandler(ch)
            
            # file handler
            fh = logging.FileHandler(self.application_log_file)
            
            file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            fh.setFormatter(file_formatter)
            
            self.logger.addHandler(fh)
        
        
    
    def log(self, message, level = 0):
        
        if level == self.level_DEBUG:
            self.logger.debug(message)
        
        elif level == self.level_INFO:
            self.logger.info(message)
        
        else:
            raise ValueError("Logger: log level not supported")
    
    
    def set_run_log_filename(self, filename):
        global run_log_filename
        run_log_filename = filename + "_" + time.strftime("%Y%m%d-%H%M%S") + ".log"
    
    
    def log_action(self, message):
        global run_log_filename
        
        with open(run_log_filename, "a") as f:
            f.write(message + "\n")
            
        self.log(message)
            
            
    