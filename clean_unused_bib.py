"""
Install tex (e.g., mactex on Mac via brew install mactex)
Get checkcites.lua from checkcites
Run the following and output to json unused.json
# to generate aux file
pdflatex input.tex

# input the generated aux file
checkcites.lua -u input.aux -j unused.json
For python3.8+, pip install bibtexparser --pre

- Rename the bib file to `input.bib`
- Run this script
- Check the output, remove some unnecessary comments from this python package.
"""

import bibtexparser
import json

bib_file = 'input.bib'
output_file = 'output.bib'
json_file = 'unused.json'
library = bibtexparser.parse_string(open(bib_file, 'r').read())

data = json.load(open(json_file, 'rb'))
unused = data['results']['unused']['occurrences']

toremove = [e for e in library.entries if e.key in unused]
library.remove(toremove)

print(len(library.entries))  # this should equal to the number in the pdf file reference section
open(output_file, 'w').write(bibtexparser.write_string(library))
