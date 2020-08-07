#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  7 09:13:23 2020

@author: maurop
"""

# =============================================================================
# Imports
# =============================================================================

# pyimports 
import os

# tkinter imports
import tkinter    
from tkinter import Frame, Label, Entry, Button, filedialog, Checkbutton, StringVar, IntVar, LabelFrame, Text

# project imports
import RememberPaths
import FileInfo
import GenerateTaxaListGBIF
import GenerateFiles
import LogFiles

# =============================================================================
# Logger
# =============================================================================

logger = LogFiles.Logger(__name__)

# =============================================================================
# GUI Classes
# =============================================================================

class GUIElement:
    
    def __init__(self, parent_frame):
        self.pFrame = Frame(parent_frame)

class LabelEntry(GUIElement):
    ''' A class to have a descriptive label in front of a text entry,
    the entry remembers the last thing input in the field, and saves
    the inputs in a file depending on the uid'''
    
    def __init__(self, root_frame, text, uid):
        super().__init__(root_frame)
        
        # principal label
        label = Label(self.pFrame, text=text)
        label.grid(row=0, column=0)
        
        # principal entry
        self.entry = Entry(self.pFrame)
        self.entry.grid(row=0, column=1)
        
        # last used value logger
        self.filename = "./settings/" + uid + ".txt"

        if os.path.isfile(self.filename):
            self.read()
        
    def read(self):
        ''' Function that reads the last input'''
        
        # read from the file
        with open(self.filename, "r") as f:
            data = f.read()
        
        # clean input
        data = data.strip()
        
        # present it in the entry
        self.entry.delete(0, tkinter.END)
        self.entry.insert(0, data)
    
    def write(self):
        ''' Function that saves the last input'''
        # saves the input in the file
        with open(self.filename, "w") as f:
            f.write(self.entry.get())      
        
    def get(self):
        ''' This function will get the input and save the input in the file'''
        self.write()
        return self.entry.get()
    
    def get_csv(self):
        ''' this function will get a comma separated value in the entry, the
        function returns a list, if there is no input returns a empty list'''
        self.write()
        
        # parse the comma separated
        values = self.entry.get().split(",")
        
        # if there is a non empty value as first value
        if values[0]:
            values = map(lambda s : s.strip(), values)
            return list(values)
        # if the value is empty, just return a empty list
        else:
            v = []
            return v
        

class SelectFolder(GUIElement):
    
    ''' This class manages the folder selection and remembers the last given
    path
    '''
    
    def __init__(self, root_frame):
        super().__init__(root_frame)
        
        # the button that will open the askdirectory dialog
        select_button = Button(self.pFrame, text="Select a folder", command=lambda : self.select())
        select_button.grid(row=0, column=0)
        
        # the path to the selected directory
        self.selected_directory = RememberPaths.RememberPath("seldir", "/")
        
        # the variable showing the selected directory
        self.selected_dir_str = StringVar()
        self.selected_dir_str.set(self.selected_directory.get())
        
        # the label displaying the selected directory
        lfolder = Label(self.pFrame, textvariable=self.selected_dir_str)
        lfolder.grid(row=1, column=0)

    def get(self):
        return self.selected_directory.get()
    
    def select(self):
        sel_dir = filedialog.askdirectory(title="Select a directory", initialdir=self.selected_directory.get())
        
        if sel_dir:
            self.selected_directory.assign(sel_dir)
            
            self.selected_dir_str.set(self.selected_directory.get())
            
class ActionButton(GUIElement):
    ''' Radio button for options '''

    def __init__(self, root_frame, text, actions):
        super().__init__(root_frame)
        
        # self introspection of the main class controlling the set of buttons
        self.actions = actions
        
        # text of the checkbutton (also unique identifier)
        self.text = text
        
        # variable controlling the button state
        self.var = IntVar()
        
        # set the variable according to the previous choices saved in the 
        # main button class
        self.var.set(1 if self.actions.action_choice[self.text] else 0)
        
        # check button class
        cb = Checkbutton(self.pFrame, text=self.text, variable=self.var, command=self.cb)
        cb.grid(row=0, column=0)

    def cb(self):
        ''' function that controls the check button
        This will change the check button and save the choice in a file'''
        self.actions.action_choice[self.text] = True if self.var.get() == 1 else False
        self.actions.write()
    
    
class Actions(GUIElement):
    
    ''' Collection of radio buttons to select the actions to perform on the
    retrived taxonomical list'''
    
    # the file where the selected actions are stored
    choice_file = "./settings/choice.txt"
    
    # possible actions
    possible_actions = ["Authority list", "Authority file", "Label table", "Synonym list"]
    
    def __init__(self, root_frame):
        super().__init__(root_frame)
        
        self.lFrame = LabelFrame(self.pFrame, text="Actions")
        self.lFrame.pack()
        
        # prepare the dictionary that holds the selected values
        self.action_choice = {}
        for action in self.possible_actions:
            self.action_choice[action] = False
        
        # reads the file of previously chosen actions
        if os.path.isfile(self.choice_file):
            self.read()
        
        # creates the radio button
        for action in self.possible_actions:
            
            ab = ActionButton(self.lFrame, action, self)
            ab.pFrame.pack()
            
            self.write()
    
    def read(self):
        with open(self.choice_file, "r") as f:
            lines = f.readlines()
            
        for line in lines:
            parts = line.split("=")
            
            choice = True if parts[1].strip() == "1" else False
            self.action_choice[parts[0].strip()] = choice
    
    def write(self):
        with open(self.choice_file, "w") as f:
            for name, choice in self.action_choice.items():
                if choice:
                    f.write(f"{name}=1\n")
                else:
                    f.write(f"{name}=0\n")


class OConsole(GUIElement):
    ''' The class for the output console'''
    
    def __init__(self, root_frame, root):
        super().__init__(root_frame)
        
        self.text = Text(self.pFrame, height=20)
        self.text.pack()
        
        self.root = root
    
    def add_line(self, line):
        self.text.insert(tkinter.END, line + "\n")
        self.text.yview_pickplace("end")
        self.root.update()
        
    
        
class GUI:
    
    def __init__(self):
        
        root = tkinter.Tk()
        
        # family options
        
        fam_frame = LabelFrame(root, text="Family details")
        fam_frame.pack()
        
        self.family_entry = LabelEntry(fam_frame, "Family:", "family")
        self.family_entry.pFrame.pack()
        
        self.ass_family_entry = LabelEntry(fam_frame, "Associated Families:", "associated_family")
        self.ass_family_entry.pFrame.pack()

        self.genera_filter = LabelEntry(fam_frame, "Genera filter:", "genera filter")
        self.genera_filter.pFrame.pack()
        
        # folder options
        
        folder_frame = LabelFrame(root, text="Data Folder")
        folder_frame.pack()
        
        self.select_folder = SelectFolder(folder_frame)
        self.select_folder.pFrame.pack()
        

        # make a selectable actions thingy
        
        self.action_frame = Actions(root)
        self.action_frame.pFrame.pack()
        
        # run button
        
        run_button = Button(root, text="RUN", command=self.run)
        run_button.pack()
        
        # output console
        
        output_console_frame = LabelFrame(text="Output console")
        output_console_frame.pack()
        
        self.oconsole = OConsole(output_console_frame, root)
        self.oconsole.pFrame.pack()
        
        
        root.mainloop()

    def run(self):
        
        # read the various inputs
        
        family = self.family_entry.get()
        
        ass_family = self.ass_family_entry.get_csv()
        
        genera = self.genera_filter.get_csv()

        base_folder = self.select_folder.get()
        
        # processing the information
        fi = FileInfo.FileInfo(base_folder, "gbif", family)
        
        # set logging files
        logger.set_run_log_filename(fi.name_only("report_log"))  
        logger.set_gui_log(self.oconsole)
        
        logger.log_short_report("#### Scrape Tax ####")
                                
        # scrape the thing
        taxa_list = GenerateTaxaListGBIF.scrape_gbif(family, ass_family, base_folder, genera)
        
        # do the actions like creating files and stuff
        actions = []
        
        # convert actions in function parameter actions
        for action_name, action_value in self.action_frame.action_choice.items():
            
            if "synonym" in action_name.lower():
                continue
            
            if action_value:
                actions.append(action_name.lower())
        
        GenerateFiles.generate_files(base_folder, "gbif", family, taxa_list, actions)

        # create synonyms
        if  self.action_frame.action_choice["Synonym list"]:
            synonym_list = GenerateTaxaListGBIF.generate_synonym_list(family, base_folder, taxa_list)  
                
            GenerateFiles.generate_files(base_folder, "gbif", family, synonym_list, ["synonyms file"])    
        
        
        logger.gui_log("--- Program Done ---")