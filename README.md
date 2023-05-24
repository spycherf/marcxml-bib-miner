# MARCXML Bibliographic Record Data Mining with Regular Expressions

## Author
**Frederic Spycher**, librarian at the Fribourg Cantonal and University Library, Switzerland

## Context
This Python script provides a way of parsing MARCXML files to extract user-specified data in a somewhat efficient way.
As there is no need load any external module or parse the DOM tree first, the script has fast execution times on smaller files (thousands of records). However, if a lot of features need to be extracted over hundreds of thousands or even millions of records, a dedicated XML parser like lxml will do a better job.

The main advantage of this script is its lack of dependencies and therefore its ability to be used in any Python 3 environment.
It was also a bit of a pet project to further improve my knowledge of regular expressions, which I generally find quite useful when working as a librarian, especially one who deals with data on a daily basis.

The code has been written and tested only with MARC 21 XML files as exported by the Alma software (Ex Libris).


## Usage
The MARC data can be mined at the field or subfield level (or, in case of the leader and control fields, at the position level).

Optional arguments enables operations which were needed in my projects, such as counting the number of physical and electronic locations, or splitting the rows by holding.

The data can then serve as input to any data analysis tool.

Example of a command: `python marcxml_bib_miner.py sample.xml output.csv LDR/6,008/23,337$b,338$b,776,856$u`

See built-in help (-h) for all information.
