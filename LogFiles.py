#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 10:20:34 2020

@author: maurop
"""

import logging
import time


run_log_filename = None
short_report_log_filename = None


# Files
#  main log file
#  console
#  report

class Logger:
    
    application_log_file = "./log_file.log"

    
    # flags
    level_DEBUG = 0
    level_INFO = 1
    
    
    # handler type
    handler_main = 0
    handler_console = 1
    handler_report = 2
    handler_short_report = 3
    
    handler_main_report = [handler_main, handler_report]
    handler_mcr = [handler_main, handler_report, handler_short_report]
    
    
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        
        
        
        if not self.logger.hasHandlers():
            
            # console handler
#            ch = logging.StreamHandler()
#            
#            console_formatter = logging.Formatter("%(message)s")
#            ch.setFormatter(console_formatter)
#            
#            self.logger.addHandler(ch)
            
            # reset the log
            with open(self.application_log_file, "w") as f:
                f.write("")
                
            
            # file handler
            fh = logging.FileHandler(self.application_log_file)
            
            file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            fh.setFormatter(file_formatter)
            
            self.logger.addHandler(fh)
            
    def set_run_log_filename(self, filename):
        global run_log_filename
        global short_report_log_filename
#        run_log_filename = filename + "_" + time.strftime("%Y%m%d-%H%M%S") + ".log"
        run_log_filename = filename + ".log"
        short_report_log_filename = filename + "_summary.log"
        
        # reset the files
        with open(run_log_filename, "w") as f:
            f.write("")  
    
        with open(short_report_log_filename, "w") as f:
            f.write("")        
        
            
    def main_log(self, message, level = 0):
        if level == self.level_DEBUG:
            self.logger.debug(message)
        
        elif level == self.level_INFO:
            self.logger.info(message)
        
        else:
            raise ValueError("Logger: log level not supported")  

    def console_log(self, message):
        print(message)
    
    
    def report_log(self, message):
        with open(run_log_filename, "a") as f:
            f.write(message + "\n")  
    
    def short_report_log(self, message):
        with open(short_report_log_filename, "a") as f:
            f.write(message + "\n")
    
    def _log(self, message, handlers = [0, 1, 2, 3], level = 0):
        
        for handler in handlers:
            
            if handler == self.handler_main:
                self.main_log(message, level)
            
            if handler == self.handler_console:
                self.console_log(message)
            
            if handler == self.handler_report:
                self.report_log(message)
                
            if handler == self.handler_short_report:
                self.short_report_log(message)
    
    def log_report(self, message):
        handlers = [self.handler_main, self.handler_report]
        self._log(message, handlers)
    
    def log_report_console(self, message):
        handlers = [self.handler_main, self.handler_report, self.handler_console]
        self._log(message, handlers)
    
    
    def log_short_report(self, message):
        handlers = [self.handler_main, self.handler_report, self.handler_console, self.handler_short_report]
        self._log(message, handlers)        
        
        
    
#    def log(self, message, level = 0):
#        
#        if level == self.level_DEBUG:
#            self.logger.debug(message)
#        
#        elif level == self.level_INFO:
#            self.logger.info(message)
#        
#        else:
#            raise ValueError("Logger: log level not supported")
#    
#    
#    def set_run_log_filename(self, filename):
#        global run_log_filename
#        run_log_filename = filename + "_" + time.strftime("%Y%m%d-%H%M%S") + ".log"
#    
#    
#    def log_action(self, message):
#        global run_log_filename
#        
#        with open(run_log_filename, "a") as f:
#            f.write(message + "\n")
#            
#        self.log(message)
        
    
    
            
            
    