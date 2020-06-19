# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 09:55:42 2020

@author: maurop
"""

# =============================================================================
# Imports
# =============================================================================

import re

import RequestsHandler
import Taxa
import FileInfo
import ProgressBar
import LogFiles

# =============================================================================
# Logging
# =============================================================================

logger = LogFiles.Logger(__name__)

# =============================================================================
# Scrape NBN Atlas
# =============================================================================

NBN_HOME = "https://species.nbnatlas.org"   


def process_author(html_element):
    author = html_element.text

    # remove the nomen nudum here
    author = author.replace("nomen nudum", "")
    
    if author != html_element.text:
        logger.report_log(html_element.text + " Removed nomen nudum")
    
    author = author.strip()
    
    regex = re.compile(r"[^,] [(\[]?\d\d\d\d[)\]]?")
    
    # add the comma before the year
    rematch = regex.findall(author)
    
    if rematch:
        
        pos = author.find(rematch[0])
        
        author = author[:pos + 1] + "," + author[pos + 1:]   
        
        logger.report_log(author + " Added comma")
    
    return author


def gather_child_taxa(url, filename):
    '''Function that scans the web page and gathers the child taxa of the url'''
    
    soup = RequestsHandler.get_soup(url, filename)
    
    # search for the child taxa section that contains all the names
    children = soup.find("dl", class_="child-taxa")
    
    # names with hierarchy tags (subfamily, genus, ...)
    dts = children.find_all("dt")
    
    # the real names
    dds = children.find_all("dd")
    
    if len(dts) != len(dds):
        raise Exception("Gather child taxa: dts / dds different length")
    

    # return the zipped elements
    return zip(dts, dds)


class NBNElement:
    ''' Class that processes the informations inside the gathered taxa'''
    
    def __init__(self, html_rank, html_name, fileinfo):
        self.html_rank = html_rank
        self.html_name = html_name
        self.fileinfo = fileinfo
    
    def get_link(self):
        '''Method that gets the link from the name box'''
        link = self.html_name.find("a")
        if link:
            link = link.get("href")
            if link.startswith(NBN_HOME):
                return link
            else:
                return NBN_HOME + link
        else:
            return None  
    
    def get_name(self):
        '''Method that gets the name (e.g. Boletina plana)'''
        return self.html_name.find("span", class_="name").text
    
    def get_rank(self):
        '''Method that gets the rank (specie, genus, ...) '''
        return self.html_rank.text

    def gather_child_elements(self):
        '''Method that gather the child elements from the page 
        pointed by the get_link() method'''
        if self.get_link():
            link = self.get_link()
            filename = self.fileinfo.cache_filename(self.get_name())
            html_elements = gather_child_taxa(link, filename)
            
            return [NBNElement(dt, dd, self.fileinfo) for dt, dd in html_elements]
    
    def get_author(self):
        '''Method that gets the author name for the element'''
        author = self.html_name.find("span", class_="author")
        if author:
            return process_author(author)
        else:
            return None


def gather_taxonomy(url, filename):
    ''' Function that scraps the taxonomy of a specie,
    it searches in the classification section the various ranks, and groups
    them in a dictionary. The function gathers the data for the subspecies too.
    returns a list of dictionaries where the first element is the specie and is
    always present, the other elements are subspecies in case they exist'''
    
    # find ranks and the name associated
    soup = RequestsHandler.get_soup(url, filename)
    children = soup.find("section", id="classification")
    
    dts = children.find_all("dt")
    dds = children.find_all("dd")

    html_parts = zip(dts, dds)
    
    # compiles the specie + subspecie list
    species = []
    
    species.append({})
    
    # find the subspecie and append the eventual subspecie name and author
    
    for dt, dd in html_parts:
        if dt.text == "subspecies":
            subspecie_name = dd.find("span", class_="name").text.split(" ")[3]
            subspecie_author = process_author(dd.find("span", class_="author"))
            species.append({"subspecies" : subspecie_name, "author" : subspecie_author})
    
    # fill in the dictionary the rest of the taxonomy
    for dt, dd in zip(dts, dds):
        if dt.text == "subspecies":
            continue
        
        for specie in species:
            name =  dd.find("span", class_="name").text
            
            if dt.text == "species":
                name = name.split(" ")[1]
            
            specie[dt.text] = name

    return species


def generate_lists(family_name, fileinfo, load_lists = True):
    '''Function that arranges the genuses and species in a list, the function
    could be translated in a tree, but ... is difficult. The function returns
    a list of Taxa with name, author and reference link'''
    
    logger.main_log("Generating taxa list from NBN Atlas...")
    logger.log_short_report("Input name: " + family_name)
    
    api_url = "https://species-ws.nbnatlas.org/search?"
    
    param = {"q" : family_name,
             "fq": "idxtype:TAXON"}
 
    req = RequestsHandler.Request(api_url, fileinfo.cache_filename("family_search"), param)
    req.load()
    
    search_json = req.get_json()
    search_results = search_json["searchResults"]["results"]
    
    # display the possible matches
    logger.log_short_report(f"Possible matches: {len(search_results)}")
    for result in search_results:
        logger.log_short_report(f"    -{result['name']} ({result['guid']})")
    
    # pick the first result
    family_guid = search_results[0]["guid"]
    
    # parameters for the webpage corresponding to the family
    family_url = "https://species.nbnatlas.org/species/" + family_guid
    
    filename = fileinfo.cache_filename("family")
    
    taxa = gather_child_taxa(family_url, filename)
    
    
    # start getting the speceis
    genus_list = []
    species_list = []
    
    pwheel = ProgressBar.ProgressWheel()
    
    # search for the child taxa
    for dt, dd in taxa:
        
        fam_taxa = Taxa.Taxa()
        fam_taxa.family = family_name
        
        fam_taxa.rank = Taxa.Taxa.rank_genus
        fam_taxa.source = "n"
        
        pwheel.draw_symbol()
        
        element = NBNElement(dt, dd, fileinfo)
        
        # if is a subfamily
        if element.get_rank() == "subfamily":
            
            subfam = element.gather_child_elements()

            for subf in subfam:
                
                subfam_taxa = Taxa.Taxa()
                subfam_taxa.copy_taxa(fam_taxa)
                subfam_taxa.subfamily = element.get_name()
                
                if subf.get_rank() == "tribe":
                    genuses = subf.gather_child_elements()
                    
                    # if is a genus with a tribe and subfamily
                    for genus in genuses:
                        if genus.get_rank() == "genus":
                            
                            taxa = Taxa.Taxa()
                            taxa.copy_taxa(subfam_taxa)
                            
                            taxa.author = genus.get_author()
                            taxa.genus = genus.get_name()
                            taxa.links.append(genus.get_link())
                            taxa.tribe = subf.get_name()
                            
                            genus_list.append(taxa)
                
                # if is a genus with subfamily without a tribe
                if subf.get_rank() == "genus":
                    
                    taxa = Taxa.Taxa()
                    taxa.copy_taxa(subfam_taxa)

                    taxa.author = genus.get_author()
                    taxa.genus = genus.get_name()
                    taxa.links.append(genus.get_link())
                    
                    genus_list.append(taxa)
        
        # if is a genus without subfamily
        if element.get_rank() == "genus":
            taxa = Taxa.Taxa()
            taxa.copy_taxa(fam_taxa)

            taxa.author = element.get_author()
            taxa.genus = element.get_name()
            taxa.links.append(element.get_link())
            
            genus_list.append(taxa)        
                      
    for genus in genus_list:
        pwheel.draw_symbol()
        
        filename = fileinfo.cache_filename(f"{genus.genus}_webpage")

        html_elements = gather_child_taxa(genus.links[0], filename)
        
        for dt, dd in html_elements:
            specie = NBNElement(dt, dd, fileinfo)            

            taxa = Taxa.Taxa()
            taxa.copy_taxa(genus)
           
            taxa.author = specie.get_author()
            taxa.specie = specie.get_name().replace(genus.genus, "").strip()
            taxa.rank = Taxa.Taxa.rank_specie
            taxa.links.append(specie.get_link())
            
            species_list.append(taxa)
            
            # find subspecies somehow
            # is possible that the name of the specie wuld be separated by / 
            # like tritici/obelisca and will break the file name
            filename = fileinfo.cache_filename(taxa.specie.replace("/", "_"))
            soup = RequestsHandler.get_soup(taxa.links[0], filename)
            children = soup.find("section", id="classification")
            
            if children:
            
                dts = children.find_all("dt")
                dds = children.find_all("dd")
            
                html_parts = zip(dts, dds)
                
                # find the subspecie and append the eventual subspecie name and author
                
                for dth, ddh in html_parts:
                    if dth.text == "subspecies":
                        staxa = Taxa.Taxa()
                        staxa.copy_taxonomy(taxa)
                        
                        staxa.author = process_author(ddh.find("span", class_="author"))
                        staxa.subspecie = ddh.find("span", class_="name").text.split(" ")[3]
                        
                        
                        staxa.rank = Taxa.Taxa.rank_subspecie
                        staxa.links.append(specie.get_link())
                        staxa.source = "n"
                        
                        species_list.append(staxa)
                    
    
    pwheel.end()
    
    logger.log_short_report(f"Genus retrived: {len(genus_list)} Species retrived: {len(species_list)}")
        
    return genus_list, species_list


if __name__ == "__main__":
    
    base_folder = "./Tests/test_NBN"
    family_name = "Mycetophilidae"
    
    fi = FileInfo.FileInfo(base_folder, "nbn", family_name)
    
    logger.set_run_log_filename(fi.name_only("test_log_myceto"))
    
    genus_list, specie_list = generate_lists(family_name, fi)
    
    print("{:-^79}".format(" GENERA "))
    print("rank family subfamily tribe genus specie subspecie author")
    for genus in genus_list:
        genus.print_extended()

    print("{:-^79}".format(" SPECIES (first 50) "))    
    for specie in specie_list[:50]:
        print(specie)
    
    

        
                                      
            
            
    
            
                       
                            