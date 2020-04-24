# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 11:49:00 2020

@author: maurop
"""

import request_handler
import json

webservice = "http://www.catalogueoflife.org/annual-checklist/2019/webservice"


if __name__ == "__main__":
    
    req = request_handler.Request(webservice, "./Data/col_test.pickle")
    req.download({"name":"psychidae", "format":"json"})
    
    job = req.response.json()
    print(json.dumps(job, indent=2))
    
   "body > div.l-basic-main > div.l-content.__web-inspector-hide-shortcut__ > div > div.ui.segments > div:nth-child(1) > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div:nth-child(1) > b > a"

    