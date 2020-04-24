# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 11:38:44 2020

@author: maurop
"""


class ProgressBar:
    
    
    def __init__(self, tot_elements):
        self.tot_elements = tot_elements - 1
        self.len_bar = 70
        self.indicator_chr = "-"
        self.empty_chr = " "
    
    
    def draw_bar(self, actual_element):
        perc = actual_element / self.tot_elements
        fraction = int(perc * self.len_bar)
        ind = self.indicator_chr * fraction
        emp = self.empty_chr * (self.len_bar - fraction)

        bar = f"[{ind}>{emp}]  {int(perc * 100)}%"
        
        
        print("\r", bar, end="")
        
        if actual_element == self.tot_elements:
            print()


if __name__ == "__main__":
    
    
    pb = ProgressBar(100)
    
    import time
    for i in range(100):
        pb.draw_bar(i)
        time.sleep(0.1)