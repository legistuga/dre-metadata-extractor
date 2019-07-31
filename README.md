DRE Metadata Extractor
======================

A tool to extract references to laws within the Portuguese law. It
reads files containing Portuguese legal documents (in plantext), finds
references to other laws and adds links to them


Setup Instructions
-------------

### Environment
The software was made in the context of a linux system and it is
possibly that it won't behave as expected in windows systems

### install the development environment
You can use any virtual environment tool for python. Here we are using Virtalenv:
- `mkvirtualenv -p /usr/bin/python3 dre-metatada-extractor`
- `pip install -r requirements.txt`

### get the data
Get the Portuguese law as a series of `.txt` files
(a law document per file) and copy them over to `data/text/`.

Some sample data is already provided in `data/sample`

### Execute

To see the regex applied to the law files you run the following

``` bash
# we are using pandoc because extractor.py does not add the html header and encoding
# only the links. By doing so, pandoc adds the missing parts
cat data/texto/[law-id].txt | python ./extractor.py | pandoc -s -f html -t html > /tmp/$(basename $1).html
```

## TODO

* Detetar documentos das nações unidas:
    `Resolução A/RES/68/262, adotada pela Assembleia Geral das Nações Unidas` (no `Aviso n.º 114/2016`)
