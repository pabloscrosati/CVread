# Reader for Scribner CV Data Files

**Version 1.1.2, Written by: Pablo Scrosati**

For program usage, use: `python CVread.py -h` or see below:

usage: `CVread.py [-h] [-f xxx.cor [xxx.cor ...]] [-l xxx.txt [xxx.txt ...]] [--details] [-v] [--split] [--override] [-r 0.000]`

optional arguments:

`-h, --help            show this help message and exit`

`-f xxx.cor [xxx.cor ...], --files xxx.cor [xxx.cor ...]` specify input file(s)

`-l xxx.txt [xxx.txt ...], --list xxx.txt [xxx.txt ...]` use a text list containing input file names

`--details` store additional experimental details to file

`-v, --verbose` print additional details while running, including additional error messages

`--split` create new folder for each input file

`--override` override files and folders if they are already present

`-r 0.000, --reference 0.000` specify a reference voltage (V) vs. 0 V SHE for correction

## Current Functionality

* Read COR data files
* Extract comments and CV data from COR data file
* Split multiple scans contained within one COR data file
* Apply reference electrode correction to data

## To Do

* Interactive mode
    * Live modification and correction of data extracted from COR data files
* Baseline subtraction/fitting
    * Include option for subtracting baseline from baseline data or generate a fitted baseline

## Changelog

**Version 1.1 | July 18, 2021**
* Release update
* Command-line functionality for reading and manipulation COR (Scribner) data files
* Added changelog tracking and GitHub updates