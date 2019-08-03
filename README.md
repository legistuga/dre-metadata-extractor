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

The program `extractor.py` reads from the `stdin` and outputs to the `stdout`.
So to use it we read the law file into it and write it to a file.

``` bash
# we are using pandoc because extractor.py does not add the html header and encoding
# only the links. By doing so, pandoc adds the missing parts
cat data/texto/[law-id].txt | python ./extractor.py | pandoc -s -f markdown -t html > /tmp/$(basename $1).html
```

to view the file you just open `/tmp/[law-id].txt` in a browser.

## TODO

* Detetar documentos das nações unidas:
    `Resolução A/RES/68/262, adotada pela Assembleia Geral das Nações Unidas` (no `Aviso n.º 114/2016`)

* Melhorar deteção de id_lei para:

  * Detetar leis antigas:
      `Decreto-Lei n.º 35717, de 24 de junho de 1946` (nao é do fomato `X/Y`) (no Decreto-Lei n.º 82/2016)
