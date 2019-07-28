#!/usr/bin/env python
# coding=utf-8

"""
Coverts raw text law into markdown throught the use of regular expressions

input: stdin
output: stdout
"""

import fileinput
import re

# url de pesquisa de lei no dre.pt ("%s" é onde ficarão os temos de pesquisa)
law_search_url = "https://dre.pt/web/guest/pesquisa/-/search/488789/details/normal?q=%s"

# expressões regulares para identificar referências a leis
tipo_de_lei = '(' + '|'.join([
    'Assento',
    'Aviso',
    'Circular',
    'Decreto',
    'Decreto do Presidente da República',
    'Decreto dos Representantes da República para as Regiões Autónomas', # TODO check
    'Decreto (Legislativo )?Regional',
    'Decreto\-Lei',
    'Decreto Regulamentar( Regional)?', # TODO check
    'Despacho',
    'Despacho Ministeral',
    'Despacho Normativo',
    'Lei',
    'Lei Constitucional',
    'Lei Orgânica',
    'Parecer',
    'Portaria',
    'Rectificação', # TODO check
    'Regulamento \(CE\)',
    'Regulamento de Execução \(UE\)'
    'Resolução',
    'Resolução da Assembleia da República',
    'Resoluções da Assembleia Legislativa das Regiões Autónomas', # TODO check
    'Resolução do Conselho de Ministros',
]) + ')'

# data publicação da lei
meses = "janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro"
data_completa = "((\d+ de ("+meses+")( de \d+)?)|(\d+\-\d+\-\d+))"

# identificador da lei (ex: 63/2017)
id_lei = "[\d+\-\w]+(/[\d+\-\w]+)+"

# diario da republica
diario = "Diário d(o|a) (Governo|República)"
serie = "((1|2).ª (Série|série|s.))|((Série|serie|s.)(-B)? ((1|I|2|II)(-(A|B))?))"
suplemento = "1º Suplemento" # FIXME completar

regexs = [
    tipo_de_lei + " n.º " + id_lei + "(,? ((de|em) " + data_completa + "))*",
    diario + "(,? (("+suplemento+")|("+serie+")|(n.º "+id_lei+")|(de "+data_completa+")))+",
    "Constituição"
]

def passage_add_links(text):
    """
    Usa uma regex para dar match de qualquer referência a uma lei e adiciona um
    link para essa lei no url da variável law_search_url
    """
    # build all inclusive regex from regexs variable
    general_regex = "|".join(regexs)

    def add_links(match):
        return "<a href=\"%s\">%s</a>" % (law_search_url % match.group(0), match.group(0))

    text = re.sub(general_regex, add_links, text, re.IGNORECASE|re.VERBOSE)

    return text

if __name__ == '__main__':
    for line in fileinput.input(): # take input from stdin
        line = passage_add_links(line)
        print(line) # send to stdout
