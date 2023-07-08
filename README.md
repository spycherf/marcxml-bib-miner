# MARCXML Bibliographic Record Data Mining with Regular Expressions

## Author
**Frederic Spycher**, librarian at the Fribourg Cantonal and University Library, Switzerland

## Context
This Python script allows the parsing of MARCXML files to extract user-specified data in a somewhat efficient manner.
It is meant to address the lack of straightforward way to mine specific MARC data from Alma (library management system by Ex Libris).
This was also a bit of a pet project to further improve my knowledge of regular expressions, which I generally find quite useful when working as a librarian, especially one who deals with data analysis on a daily basis.

## Regular expressions vs. dedicated XML parser
The main script, `marcxml_bib_miner.py`, uses regular expressions for data mining.
Its lack of dependencies enables its use in any Python 3 environment.
Furthermore, as there is no need to parse the DOM tree first, the script starts extracting the data right away, no matter the file size.
Of course, the more features to be extracted, the slower the execution time.

For comparison, a similar script using the lxml parser (via Beautiful Soup 4) was written.
As suspected, this script is much slower.
Using regular expressions, 75,000 records can be parsed under a minute, whereas it takes the lxml parser more than 7 minutes to accomplish the same.
However, the code may need to be re-written to be more efficient; more experienced programmers should get in touch with me if they have suggestions.

The code has been written and tested only with MARC 21 XML files as exported by the Alma software.

## Usage
The MARC data can be mined at the field or subfield level (or, in case of the leader and control fields, at the position level).
Control numbers (field 001) are extracted by default.

Optional arguments enables operations which were needed in my projects, such as counting the number of physical and electronic locations, or splitting the rows by holdings.

The output is a CSV file, which can then serve as input to any data analysis tool.

Example of a command: `python marcxml_bib_miner.py sample.xml output.csv "LDR/6,008/23,008/29,300,337$b,338$b,776,856$u"`

Depending on the terminal, different field-subfield separators should be used such as `_` or `-` (e.g., in PowerShell `$` is reserved for variables and thus won't work).

See built-in help (-h) for all information.

## Upcoming development
* Allow extraction of indicators
* Extract data based on the presence of specific indicators
