#!/usr/bin/env python
# -*- coding: utf-8 -*-
import glob
# import requests
import re
from logzero import logger



def dumpname2lang(basename):
    # zh_min_nanwiktionary-20221219-cirrussearch-content.txt.bz2   zh_min_nanwiktionary
    name = basename.split('-')[0]
    lang = name.split('wik')[0]
    prefix = lang.split('_')[0]
    if len(prefix) <= 1 or len(prefix) >= 4:
        logger.info(f"{name}--> wiki")
        lang = 'wiki'
    for x in prefix:
        if not 'a'<=x<='z':
            logger.info(f"{name}--> wiki")
            lang = 'wiki'
    return lang

def get_dumps(select= ['wiki', 'wikisource']):
    # https://ftp.acc.umu.se/mirror/wikimedia.org/other/cirrussearch/20220124/
    files = open("dumpnames.txt").read().splitlines()
    dumps = []
    for f in files:
        lang=dumpname2lang(f)
        if lang=='wiki':
            continue
        if select:
            for x in select:
                if f.endswith(x):
                    dumps.append(f)
        else:
            dumps.append(f)

    logger.info(f"dumps {len(dumps) } ")
    # dumps 9  {'wikiquote', 'wikibooks', 'wikimedia', 'wikiversity', 'wikivoyage', 'wiktionary', 'wiki', 'wikinews', 'wikisource'}
    return dumps

def gen_xml_links(dumpnames):
    """ 
    https://ftp.acc.umu.se/mirror/wikimedia.org/dumps/aawiki/20230101/aawiki-20230101-pages-articles.xml.bz2
    https://ftp.acc.umu.se/mirror/wikimedia.org/dumps/enwikisource/20230101/enwikisource-20230101-pages-articles.xml.bz2
     """
    with open("links.txt", "w") as f:
        for dumpname in dumpnames:
            lang=dumpname2lang(dumpname)
            link = f"https://ftp.acc.umu.se/mirror/wikimedia.org/dumps/{dumpname}/20230101/{dumpname}-20230101-pages-articles.xml.bz2"
            tgt=f"{dumpname}.json.bz2"
            f.write(f"{lang}\t{dumpname}\t{link}\t{tgt}"+'\n')

def gen_cirrussearch_links(dumpnames):
    """ 
      https://ftp.acc.umu.se/mirror/wikimedia.org/other/cirrussearch/20230220/eswiki-20230220-cirrussearch-content.json.gz
     """
    with open("links.txt", "w") as f:
        for dumpname in dumpnames:
            lang=dumpname2lang(dumpname)
            # link = f"https://ftp.acc.umu.se/mirror/wikimedia.org/other/cirrussearch/current/{dumpname}-20230213-cirrussearch-content.json.gz"
            link = f"https://ftp.acc.umu.se/mirror/wikimedia.org/other/cirrussearch/20230220/{dumpname}-20230220-cirrussearch-content.json.gz"
            tgt=f"{dumpname}.json.gz"
            f.write(f"{lang}\t{dumpname}\t{link}\t{tgt}"+'\n')

if __name__ == "__main__":
    """
    https://mirror.accum.se/mirror/wikimedia.org/other/cirrussearch/current
    aawiki-20230828-cirrussearch-content.json.gz
    https://mirror.accum.se/mirror/wikimedia.org/other/cirrussearch/current/aawiki-20230828-cirrussearch-content.json.gz
    """
    raw=open("html.txt").read().splitlines()
    names=[x.split() for x in raw ]
    names=[x[1] for x in names if x and x[0]=="[ARC]"]
    urls=[(name,f"https://mirror.accum.se/mirror/wikimedia.org/other/cirrussearch/current/{name}") for name in names if 'content' in name]
    with open("urls.txt","w") as f:
        for name,url in urls:
            f.write(url+'\n')

    step=200
    for i in range(0,len(urls),step):
        with open(f"urls-{i}.txt","w") as f:
            for name,url in urls[i:i+step]:
                f.write(url+'\n')        

    # print(dumpname2lang("zh_min_nanwiktionary"))
    # dumpnames=get_dumps()
    # print(dumpnames)
    # gen_links()
    # gen_xml_links(dumpnames)
    # gen_cirrussearch_links(dumpnames)

"""

"""
