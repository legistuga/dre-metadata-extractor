#!/usr/bin/env python
# coding=utf-8

"""
Coverts raw text law into markdown throught the use of regular expressions

input: stdin
output: stdout
"""

import fileinput
import re

import logging

# configure logging
root = logging.getLogger()
root.setLevel(logging.DEBUG)

# url de pesquisa de lei no dre.pt ("%s" é onde ficarão os temos de pesquisa)
law_search_url = "https://dre.pt/web/guest/pesquisa/-/search/basic?q=%s"

# expressões regulares para identificar referências a leis nacionais
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
    'Resolução',
    'Resolução da Assembleia da República',
    'Resoluções da Assembleia Legislativa das Regiões Autónomas', # TODO check
    'Resolução do Conselho de Ministros',
]) + ')'

# expressões regulares para identificar referências a leis europeias
tipo_de_lei_eu = '(' + '|'.join([
    'Regulamento \(CE\)',
    'Regulamento \(UE\)',
    'Regulamento de Execução \(UE\)',
    'Regulamento Delegado \(UE\)'
]) + ')'

# data publicação da lei
meses = "janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro"
data_completa = "(?:(?:\d+ de (?:"+meses+")(?: de \d+)?)|(?:\d+\-\d+\-\d+))"
data = "(?:,? (?:(?:de|em) " + data_completa + "))*"

# identificador da lei (ex: 63/2017)
id_lei = "(?:[\d+\-\w]+(?:/[\d+\-\w]+)+)"

# diario da republica
diario = "Diário d(?:o|a) (?:Governo|República)"
serie = "(?:(?:1|2).ª (?:Série|série|s.))|(?:(?:Série|serie|s.) ((?:1|I|2|II)(?:\-(?:A|B))?))"
suplemento = "1º Suplemento" # FIXME completar
id_diario = "(%s|\w+)" % id_lei # diario tambem pode ser referido como [nº] ou "[nº]/[ano]"

# documentos EU
orgaos_europeus = '(' + '|'.join([
    'da Comissão', # comissão europeia
    'do Conselho', # conselho europeu
    'do Parlamento Europeu'
]) + ')'
# regex para referencias aos orgãos da UE, por exemplo:
#      do Parlamento Europeu e do Conselho
#      da Comissão
orgao_europeu = "(?P<orgao_europeu>,? %s(?:(?:,? %s)|(?: e %s))*)" % \
                 (orgaos_europeus, orgaos_europeus, orgaos_europeus)

regexs = [
    tipo_de_lei + " n.º " + id_lei + data,
    tipo_de_lei_eu + " (?:n.º )?" + id_lei + orgao_europeu + data,
    diario + "(?:,? (?:(?:"+suplemento+")|(?:"+serie+")|(?:n.º "+id_diario+")+"+data+"))+",
    "Constituição"
]

def passage_add_links_multiple(text):
    """
    Encontra leis referenciadas multiplas e seguidas, como por exemplo

      "Decretos-Leis n.os 261/2001, de 26 de setembro, 249/2002, de 19 de
       novembro, 33/2003, de 24 de fevereiro, e 192/2008, de 1 de outubro"

    e adiciona-lhes links para a respetiva lei.

    """

    tipo_de_lei_plural_singular_mapping = {
        # plural : singular,
        "Resoluções do Conselho de Ministros" : "Resolução do Conselho de Ministros",
        "Leis constitucionais" : "Lei constitucional",
        "Leis orgânicas" : "Lei orgânica",
        "Leis" : "Lei",
        "Decretos-leis" : "Decreto-lei",
        "Decretos legislativos regionais" : "Decreto legislativo regional", # TODO check
        "Decretos do Presidente da República" : "Decreto do Presidente da República",
        "Resoluções da Assembleia da República" : "Resolução da Assembleia da República",
        "Resoluções do Conselho de Ministros" : "Resolução do Conselho de Ministros",
        "Resoluções das Assembleias Legislativas das Regiões Autónomas" : "Resolução das Assembleias Legislativas das Regiões Autónomas",
        "Decisões de tribunais" : "Decisão de tribunal", # TODO check
        "Decretos regulamentares" : "Decreto regulamentar",
        "Decretos regulamentares regionais" : "Decreto regulamentare regional",
        "Decretos dos Representantes da República para as Regiões Autónomas" : "Decreto dos Representantes da República para as Regiões Autónomas",
        "Despachos Normativos" : "Despacho Normativo",
        "Portarias" : "Portaria",
        "Pareceres" : "Parecer",
        "Avisos" : "Aviso",
        "Declarações" : "Declaração"
    }

    # regex para encontrar referencia de lei em sequências, por exemplo, em
    # "67/2014, de 12 de março, e 219/2015, de 23 de julho" retorna
    # "67/2014, de 12 de março" e "219/2015, de 23 de julho"
    short_id_lei = "%s(?:,? (?:de|em) %s)?" % (id_lei, data_completa)

    # regex que faz match com nome de documentos legislativos no plural.
    # Explicação dos "named groups" de regex:
    #   - tipo_de_lei : tipo de documento legislativo (ex: Decreto-lei) :
    id_lei_plural_regex  = "(?P<tipo_de_lei>" + "|".join(tipo_de_lei_plural_singular_mapping) + ")"
    id_lei_plural_regex += " n.os((?:,|, e)? %s(?:,? (?:de|em) %s)?)+" % (id_lei, data_completa)

    def expand_law(match):

        tipo_de_lei = match.group("tipo_de_lei")
        shortened_lei = match.group()

        try:
            tipo_de_lei_singular = tipo_de_lei_plural_singular_mapping[tipo_de_lei]
            logging.info('multiple laws of type "%s" found' % tipo_de_lei)

        except KeyError:
            logging.error('Tipo de lei descolhecido: %s' % tipo_de_lei)

        # due to a limitation in the python regex, we can only access the last
        # match of a group. To overcome this, we'll do a regex on top of the
        # other one to find each specific law

        def add_links(match):
            law_full_name =  tipo_de_lei_singular + " n.º " + match.group(0)
            logging.info("adding link to %s" % law_full_name)

            return create_link(law_search_url % law_full_name, match.group(0))

        return re.sub(short_id_lei, add_links, shortened_lei, re.IGNORECASE|re.VERBOSE)

    return re.sub(id_lei_plural_regex, expand_law, text, re.IGNORECASE|re.VERBOSE)


def passage_add_links(text):
    """
    Usa uma regex para dar match de qualquer referência a uma lei e adiciona um
    link para essa lei no url da variável law_search_url
    """

    # build all inclusive regex from regexs variable
    general_regex = "|".join(regexs)

    def add_links(match):
        logging.info("adding link to %s" % match.group(0))
        return create_link(law_search_url % match.group(0), match.group(0))

    text = re.sub(general_regex, add_links, text, re.IGNORECASE|re.VERBOSE)

    return text

"""
    Utils (small helper functions)
"""
def create_link(target, text):
    """
    creates an html link like <a href="[target]">[text]</a>
    """
    return "<a href=\"%s\">%s</a>" % (target, text)

if __name__ == '__main__':
    for line in fileinput.input(): # take input from stdin
        line = passage_add_links(line)
        line = passage_add_links_multiple(line) # needs to be after passage_add_links
        print(line) # send to stdout
