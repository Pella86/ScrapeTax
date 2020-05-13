# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 11:38:44 2020

@author: maurop
"""


class ProgressBar:
    ''' Class that shows a little updating progress bar on the screen
        [---->     ] x%
    '''
    
    def __init__(self, tot_elements):
        # the elements inside the for loop
        self.tot_elements = tot_elements - 1
        
        # the length of the bar
        self.len_bar = 70
        
        # indicators
        self.indicator_chr = "-"
        self.empty_chr = " "
    
    
    def draw_bar(self, actual_element):
        # calculate the percentage complete
        perc = actual_element / self.tot_elements
        
        # calculate the fraction of the bar to be displayed as complete
        fraction = int(perc * self.len_bar)
        
        # construct the strings corresponding to the completed/uncompleted bar
        ind = self.indicator_chr * fraction
        emp = self.empty_chr * (self.len_bar - fraction)

        bar = f"[{ind}>{emp}]  {int(perc * 100)}%"
        
        # print with carriage return
        print("\r", bar, end="")
        
        # end with a new line that will stop the end=""
        if actual_element == self.tot_elements:
            print()
            

class ProgressWheel:
    ''' Class that show a little rotating wheel'''
    
    def __init__(self):
        self.symbols = "|/-.-\\"
        self.counter = 0
        
    def draw_symbol(self):
        print("\r", self.symbols[self.counter], end="")
        
        self.counter += 1
        # limit the counter between 0 and len - 1 characters in symbols
        self.counter %= len(self.symbols)

    def end(self):
        print("100%")
        


if __name__ == "__main__":
    
    import time
    
    pb = ProgressBar(100)

    for i in range(100):
        pb.draw_bar(i)
        time.sleep(0.1)
        
    
    pw = ProgressWheel()
    
    for i in range(100):
        pw.draw_symbol()
        time.sleep(0.1)
    pw.end()
