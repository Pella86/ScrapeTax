#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 20 12:55:37 2020

@author: maurop
"""

# small program that interacts with the bold API
#https://www.boldsystems.org/

# =============================================================================
# Imports
# =============================================================================

import urllib

import RequestsHandler
import Taxa
import ProgressBar


# =============================================================================
# API URL
# =============================================================================

main_url = "http://www.boldsystems.org"

taxon_search_api_url = main_url + "/index.php/API_Tax/TaxonSearch"
taxonid_api_url = main_url + "/index.php/API_Tax/TaxonData"
specimen_api_url = main_url + "/index.php/API_Public/specimen"
taxon_search_url = main_url + "/index.php/Taxbrowser_Taxonpage"

# =============================================================================
# retrive all the specimens they have
# =============================================================================

class Record:
    ''' Class that manages the specimen records returned by the BOLD system'''
    
    def __init__(self, record):
        self.record = record
        
        self.specie = None
        self.genus = None
        self.author = None
        self.rank = None
        
        # get the taxons
        
        # check if is a specie
        
        specie_taxon = self.get_taxon("species")
        
        if specie_taxon:
            self.specie = self.get_name("species").split(" ")[1]
            self.author = self.get_author("species")
            self.rank = Taxa.Taxa.rank_specie
        
        # if is not a specie then the taxa might be a genus
        # if that is the case set rank and author accordingly
        # if the specie is present then the author refers to the specie
        # and the genus is part of the binomial name
        
        genus_taxon = self.get_taxon("genus")
        
        if genus_taxon:
            if specie_taxon == None:
                self.rank = Taxa.Taxa.rank_genus
                self.author = self.get_author("genus")
            
            self.genus = self.get_name("genus")
        
        # add the higher taxonomy
        
        self.tribe = self.assign_name("tribe")
        self.subfamily = self.assign_name("subfamily")
        self.family = self.assign_name("family")

    def get_taxon(self, taxon_rank):
        return self.record["taxonomy"].get(taxon_rank)

    def get_name(self, taxon_rank):
        return self.record["taxonomy"][taxon_rank]["taxon"]["name"]

    def get_author(self, taxon_rank):
        return self.record["taxonomy"][taxon_rank]["taxon"].get("reference")
    
    def assign_name(self, taxon_rank):
        taxon = self.get_taxon(taxon_rank)
        if taxon:
            return self.get_name(taxon_rank)
        else:
            return None


def specimen_list(family_name, fileinfo):
    ''' This function produces the list of specimen that they have in the
        database, the function filters out all the specimen that have the 
        same taxonomic designation
    '''
    
    # request all the specimens that have family_name in their stuff
    param = {"taxon": family_name,
             "format":"json"}    
    
    # in case the parameters have a space it encodes it as "name%20name"
    # instead of "name+name". There shouldnt be spaces in a family_name yet
    # this is here for legacy purposes?
    param = urllib.parse.urlencode(param, quote_via=urllib.parse.quote)
    filename = fileinfo.cache_filename("specimen_api")
    
    # performs the request
    req = RequestsHandler.Request(specimen_api_url, filename, param)
    res_json = req.get_json()
    
    # selects the respective records from the response
    records = res_json["bold_records"]["records"]
    
    # This are the possible dict keys of the record, if there is a response
    # with more keys the program will give a error
    tax_keys = ['identification_provided_by', 'identification_method',
                'phylum', 'class', 'order', 'family', 'subfamily', 'genus',
                'species', 'subspecies']
    
    
    # converts the records in taxas
    taxa_list = list()
    for record in records.values():
         
        # check if the taxon program selects all possible taxon ranks
        tax_list = list(record["taxonomy"].keys())
        
        for word in tax_list:
            if word in tax_keys:
                #print(".", end="")
                continue
            else:
                raise Exception("BOLD_downloader: the key is not present:" + word)
        
        # create the record class which will parse the JSON
        rec = Record(record)
        
        # We are only intereseted in genus + specie not family, subfamily, 
        # which anyway dont have author and information to the associated genus
        if rec.genus == None and rec.specie == None:
            continue
        
        # there are species that arent determined yet?
        if rec.specie == "n. sp.":
            continue
        
        
        
        # transform the recod to the taxa
        taxa = Taxa.Taxa()
        
        taxa.family = rec.family
        taxa.subfamily = rec.subfamily
        taxa.tribe = rec.tribe
        taxa.genus = rec.genus
        taxa.specie = rec.specie
        taxa.author = rec.author
        taxa.rank = rec.rank
        
        # if the taxa is already present dont add it
        # if is not present add it to the list
        for existing_taxa in taxa_list:
            if existing_taxa.is_equal(taxa):
                break
        else:
            taxa_list.append(taxa)

    return taxa_list

# =============================================================================
# Get taxon information from the taxon pages
# =============================================================================

def get_children(taxid, fileinfo, parent_taxa = None):
    ''' The function scans the webpage with the taxid and finds the subtaxa 
        asssociated with it'''
    
    # construct the request
    param = {"taxid" : taxid}
    filename = fileinfo.cache_filename(f"taxid_search_{taxid}")
    req = RequestsHandler.Request(taxon_search_url, filename, param)
    
    # get the soup
    soup = req.get_soup()
    
    # Find the sections containing the sub taxa, if there are less than 6
    # sections it means that the page doesn't have sub taxa
    sections = soup.find_all("div", {"class":"col-md-6"})
    if len(sections) <= 6:
        return None
    else:
        subtaxa = sections[6]
    
    # Find the taxons in the sections, it can be that the subtaxa have multiple
    # ranks like a family can have genera and subfamily associated wiht it
    taxon_ranks = subtaxa.find_all("lh")
    taxons = subtaxa.find_all("ol")    
    
    # Analyze the taxons
    taxa_list = []
    
    for rank, tax in zip(taxon_ranks, taxons):
        
        # dummy taxa to insert the information that will be equal in all the
        # child taxa like source and previous taxonomy
        retrived_taxa = Taxa.Taxa()
        retrived_taxa.source = Taxa.Taxa.source_bold
        
        if parent_taxa:
            retrived_taxa.copy_taxonomy(parent_taxa)
        
        # format the rank Subfamilies (7) -> subfamilies
        frank = rank.text.split(" ")[0].lower()
        
        # comvert into Taxa rank type
        taxa_ranks = {"subfamilies" : Taxa.Taxa.rank_subfamily,
                      "tribes"      : Taxa.Taxa.rank_tribe,
                      "genera"      : Taxa.Taxa.rank_genus,
                      "species"     : Taxa.Taxa.rank_specie,
                      "subspecies"  : Taxa.Taxa.rank_subspecie
                      }
        
        try:
            retrived_taxa.rank = taxa_ranks[frank]
        except KeyError:
            raise Exception("BOLD_downloader: Taxon rank not present")
        
        # get the names associated with the rank
        
        taxon_names = tax.find_all("a")
        
        for name in taxon_names:
            
            taxa = Taxa.Taxa()
            taxa.copy_taxa(retrived_taxa)
            
            # parse the name
            if taxa.rank == Taxa.Taxa.rank_specie:
                text = name.text.split(" ")[1].strip()
                
            elif taxa.rank == Taxa.Taxa.rank_subspecie:
                text = name.text.split(" ")[2].strip()
            
            else:
                text = name.text.split(" ")[0].strip()

            # the "sp." is marked under species but has no designated name
            # has only a code like CB-12. There are some species that probably
            # are provisory names that contain codes and symbols
            if text == "sp." or text == "cf." or "-" in text or "_" in text:
                continue
            
            if text.find("sp.") != -1:
                print("sp. in text, text:", text)
                continue
            
            if text.find("nr.") != -1:
                print("nr. in text, text:", text)
                continue
                        
            
            
            # skip names containing digits
            if any(c.isdigit() for c in text):
                continue

            # assign the name
            if taxa.rank == Taxa.Taxa.rank_subfamily:
                taxa.subfamily = text

            elif taxa.rank == Taxa.Taxa.rank_tribe:
                taxa.tribe = text
            
            elif taxa.rank == Taxa.Taxa.rank_genus:
                taxa.genus = text
            
            elif taxa.rank == Taxa.Taxa.rank_specie:
                taxa.specie = text
            
            elif taxa.rank == Taxa.Taxa.rank_subspecie:
                taxa.subspecie = text

            else:
                raise Exception("Taxon rank not present")
            
            # assign the relative link, used then to find the relative subtaxa
            link = main_url + name.get("href")
            taxa.links.append(link)
            
            taxa_list.append(taxa)
    
    return taxa_list
                


def get_id_from_taxa(taxa):
    ''' small function to retrive the id from the source link
        source link: https://www.boldsystems.org/index.php/Taxbrowser_Taxonpage?taxid=596013
    '''
    
    # select the link
    link = taxa.links[0]
    
    # find where taxid is 
    pos_taxid = link.find("taxid")  
    
    # cut the string sto that only the id remains
    taxid = int(link[pos_taxid + len("taxid") + 1 :])
    
    return taxid



def generate_children_list(family_id, fileinfo, parent_taxa):
    
    pwheel = ProgressBar.ProgressWheel()
    
    taxa_list = []
    
    # get taxa related to family
    family_taxa_list = get_children(family_id, fileinfo, parent_taxa)
    
    taxa_list += family_taxa_list
    
    for ftaxa in family_taxa_list:
        
        pwheel.draw_symbol()
        
        subfamily_taxa = get_children(get_id_from_taxa(ftaxa), fileinfo, ftaxa)
        
        if subfamily_taxa:
            
            taxa_list += subfamily_taxa
        
            for staxa in subfamily_taxa:

                pwheel.draw_symbol()                
        
                tribes_taxa = get_children(get_id_from_taxa(staxa), fileinfo, staxa)
                
                if tribes_taxa:
                    
                    taxa_list += tribes_taxa
                
                    for gtaxa in tribes_taxa:
        
                        pwheel.draw_symbol()
                        
                        genus_taxa = get_children(get_id_from_taxa(gtaxa), fileinfo, gtaxa)
                        
                        if genus_taxa:
                            
                            taxa_list += genus_taxa
                            
                            for sptaxa in genus_taxa:
                                
                                pwheel.draw_symbol()
                                
                                subspecie_taxa = get_children(get_id_from_taxa(sptaxa), fileinfo, sptaxa)
                                
                                if subspecie_taxa:
                                    
                                    taxa_list += subspecie_taxa
    pwheel.end()
    # filter out all the taxon that don't have specie or genus
    return list(filter(lambda taxa : taxa.specie != None or taxa.genus != None, taxa_list))

# =============================================================================
# Generate the complete taxa list
# =============================================================================

def generate_lists(family_name, fileinfo, load_lists = True):
    print("Gathering data from BOLD Databases...")
    print("Input name:", family_name)
    
    
    # Use the search API to search for the name
    
    param = {"taxName" : family_name}
    
    req = RequestsHandler.Request(taxon_search_api_url, fileinfo.cache_filename("test"), param)
    
    res_json = req.get_json()
    
    print("Possible matches:", res_json["total_matched_names"])
    
    for match in res_json["top_matched_names"]:
        print("    - " + match["taxon"], f"(id: {match['taxid']})" )
    
    # get the tax id from the search    
        
    # Pick the first match
    family = res_json["top_matched_names"][0]

    # use the id to get the information about the taxon
    param = {"taxId" : family["taxid"],
             "dataTypes" : "basic"}
    
    req = RequestsHandler.Request(taxonid_api_url, fileinfo.cache_filename("taxid_info"), param)
    res_json = req.get_json()
    
    # keys: dict_keys(['taxid', 'taxon', 'tax_rank', 'tax_division',
    #         'parentid', 'parentname', 'taxonrep', 'stats', 'country',
    #         'sitemap', 'images', 'sequencinglabs', 'depositry',
    #         'wikipedia_summary', 'wikipedia_link'])
    
    if res_json["tax_rank"] != "family":
        raise Exception("BOLD_downloader: the selected result is not a family")
    
    
    family_taxa = Taxa.Taxa()
    
    family_taxa.rank = Taxa.Taxa.rank_family
    family_taxa.family = res_json["taxon"]
    
    family_id = res_json["taxid"]
    
    print("Retriving subtaxas...")
    
    # use the retrived information to scavenge the sub taxa
    taxa_list = generate_children_list(family_id, fileinfo, family_taxa)
    
    print("Gathering specimens...")
    
    # use the specimen database to find the authors
    specimens = specimen_list(family_name, fileinfo)
    
    print("Composing the list...")
    
    # assign the authors from the specimen database
    for taxa in taxa_list:
        for specimen in specimens:
            if taxa.specie == specimen.specie and taxa.genus == specimen.genus:
                if taxa.author == None:
                    taxa.author = specimen.author    
    
    # divide species and genus
    species_list = list(filter(lambda t : t.rank == t.rank_specie, taxa_list))
    genus_list = list(filter(lambda t : t.rank == t.rank_genus, taxa_list))
        
    print("Genus retrived:", len(genus_list), "Species retrived:", len(species_list))
    
    return genus_list, species_list


if __name__ == "__main__":
    
    
    
    import FileInfo
    
    base_folder = "./Tests/test_BOLD"
    
    fileinfo = FileInfo.FileInfo(base_folder, "bold", "Mycetophilidae")
    
    # get the stuff
    
    species_list, genus_list = generate_lists(fileinfo.family_name, fileinfo) 
    taxa_list = species_list + genus_list
    
    Taxa.save_taxa_list(taxa_list, fileinfo.pickle_filename("taxa_list"))
    
    # load list
    
    taxa_list = Taxa.load_taxa_list(fileinfo.pickle_filename("taxa_list"))
    
    Taxa.construct_associations(taxa_list)


    
    
