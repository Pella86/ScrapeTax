#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  5 09:39:36 2020

@author: maurop
"""

import request_handler



home = "http://sciaroidea.info/"


sciaroidea_webpage = home + "/taxonomy/40255"


soup = request_handler.get_soup(sciaroidea_webpage)


soup.select()