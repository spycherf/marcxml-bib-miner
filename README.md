# MARCXML Bibliographic Record Data Mining with Regular Expressions

## Author

**Frederic Spycher**, librarian at the Fribourg Cantonal and University Library (BCU Fribourg), Switzerland

## Description

This Python script uses regular expressions to extract user-specified data from a MARCXML file in a somewhat efficient manner (faster than the lxml parser).
The output is a CSV file.

The script addresses the lack of straightforward ways to mine specific MARC data from Alma (library management system by Ex Libris).
This was also a bit of a pet project to further improve my knowledge of regular expressions, which I generally find quite useful for library data analysis.

The code has been tested only with MARC 21 XML files as exported by the Alma software.

## Usage

The MARC data can be mined at the field or subfield level (or, in the case of the leader and control fields, at the position level).
It is possible to extract data conditionally based on the value of indicators.
Control numbers (field 001) are extracted by default.

Optional arguments include:

- Splitting the rows by holdings (requires embedded holdings data)
- Extracting field indicators (which appear in the output between curly brackets, e.g., {10})
- Counting the number of physical locations (852), electronic locations (856), and/or local extensions ($9 LOCAL) for each record

Example of a command:
`python marcxml_bib_miner.py sample.xml output.csv "LDR/6,264ind1= ind2=4,300,852_h,856ind2=1_u" -s`

See built-in help (-h) for more information on command usage.
