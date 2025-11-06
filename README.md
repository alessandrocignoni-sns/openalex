# SVR's OpenAlex scripts
Python 3 scripts, useful to Research Assessment and Open Science Service of Scuola Normale Superiore.

Necessary libraries:
- requests

## Scripts English description
Code is written and commented in Italian. Here a brief description of the scripts:
- **251030_DatiWorksInCSVDaAutore.py** - From OpenAlex author id, it uses the works endopint to get the data for each of their works, then it writes them in a CSV file containing OpenAlex id, DOI, title and publishing date of each work.
- **251103_DatiWorksInCSVDaInstitution.py** - From OpenAlex institution id, it uses the works endpoint to get the data for each of for each publication with at least an author affiliated to the institution, then it writes it them in a CSV file containing OpenAlex id, DOI, title and publishing date of each work.
- **251106_DatiWorksInCSVDaAffiliated.py** From OpenAlex institution id, it uses the authors endpoint to get their OpenAlex id if they have been affiliated to the insititution: for each author it uses the works endopint to get the data for each of their works, then it writes them in a CSV file containing author OpenAlex id, work OpenAlex id, DOI, title and publishing date of each work.
- **251106_DatiWorksInCSVDaCSV** - From author ORCID id, first it uses the organization endopoint to get the OpenAlex id of the author, secondly from a CSV file in the same folder of the script containing fiscal code and ORCID id of authors, it gets the data for each author work, then it writes it in a CSV file containing fiscal code, OpenAlex id of the work, DOI, title and publishing date of each work. It also prints the fiscal code of authors not registered in OpenAlex.
