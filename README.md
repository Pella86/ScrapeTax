# ScrapeTax

ScrapeTax is a program to gather species and genus names from a given family, the program uses different online databases as a resource

# Usage

clone the repository and move to the program folder and use a terminal where you can digit

```python main.py```

# Inputs

- The program will prompt for a folder where to store the program data
- The program will ask for a Family name
- The program will ask if you want to concentrate the results on specific genera

The program will scan the GBIF database (https://www.gbif.org) for names, then use the BOLD database (http://www.boldsystems.org) to find subfamilies and tribes relations, finally the program will use the (https://nbnatlas.org) to gather information about author spelling and authors.

# Outputs

The progam will then output:
- A CSV file that can be imported in the PreCaptureApp (https://sourceforge.net/p/datashot/wiki/PreCapture%20Application/) and used as an authority file
- A html file containing an alphabetical ordered list of names
- A html file containing labels
- A html file containing an alphabetically ordered synonym list

- The program will also log which names are excluded (because they have missing information or badly formatted)
