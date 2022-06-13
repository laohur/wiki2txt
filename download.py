#!/usr/bin/env python
# -*- coding: utf-8 -*-
import glob
import requests
import re
from logzero import logger


def get_langs():
    alphabet = ''.join(chr(x) for x in range(ord('a'), ord('z')+1))
    langs = []
    for x in alphabet:
        for y in alphabet:
            langs.append(x+y)
    return langs


langs = get_langs()


def get_dumps():
    # https://ftp.acc.umu.se/mirror/wikimedia.org/other/cirrussearch/20220124/
    files = open("files.txt").read().splitlines()

    # cbk_zamwiki-20220117-cirrussearch-general.json.gz

    names = []
    dumps = set()
    for f in files:
        if not f.endswith("-cirrussearch-content.json.gz"):
            continue
        name = f.split('-')[0]
        if name[2:5] == "wik":
            # names.append(f)
            dump = name[2:]
            dumps.add(dump)
    logger.info(f"dumps {len(dumps) }  {dumps}")
    # dumps 9  {'wikiquote', 'wikibooks', 'wikimedia', 'wikiversity', 'wikivoyage', 'wiktionary', 'wiki', 'wikinews', 'wikisource'}
    return dumps


dumps = ['wikiquote', 'wikibooks', 'wikimedia', 'wikiversity',
         'wikivoyage', 'wiktionary', 'wiki', 'wikinews', 'wikisource']


def get_names():
    # https://ftp.acc.umu.se/mirror/wikimedia.org/other/cirrussearch/20220124/
    files = open("files.txt").read().splitlines()

    # cbk_zamwiki-20220117-cirrussearch-general.json.gz
    languages=set()
    names = []
    for f in files:
        if not f.endswith("-cirrussearch-content.json.gz"):
            continue
        name = f.split('-')[0]
        # if name[2:5] == "wik" or name[3:6] == "wik":
        if name[2:5] == "wik":
            names.append(f)
            lang=name.split("wik")[0]
            languages.add(lang)
    logger.info(("languages", len(languages)))
    logger.info(("languages", (languages)))
    logger.info(("files", len(names)))
    return names


def gen_links1():
    names = get_names()
    # https://ftp.acc.umu.se/mirror/wikimedia.org/other/cirrussearch/20220131/aawiki-20220131-cirrussearch-content.json.gz
    day = "20220131"
    with open("wiki_urls.txt", "w") as f:
        for lang in langs:
            for dump in dumps:
                link = f"https://ftp.acc.umu.se/mirror/wikimedia.org/other/cirrussearch/{day}/{lang}{dump}-{day}-cirrussearch-content.json.gz"
                f.write(link+'\n')


def gen_links():
    names = get_names()
    # https://ftp.acc.umu.se/mirror/wikimedia.org/other/cirrussearch/20220124/advisorywiki-20220124-cirrussearch-content.json.gz
    day = "20220606"
    # host = "https://ftp.acc.umu.se/mirror/wikimedia.org/other/cirrussearch/20220124/"
    with open("wiki_urls.txt", "w") as f:
        for name in names:
            # link = host+name
            link = f"https://ftp.acc.umu.se/mirror/wikimedia.org/other/cirrussearch/{day}/{name}"
            f.write(link+'\n')


def gen_links1():
    import os
    wiki_urls = open("wiki_urls.txt").read().splitlines()
    day = "20220131"

    files = glob.glob(
        rf"F:/data/wiki-{day}-cirrussearch-content-json-gz/*")
    donwload = set([os.path.basename(x) for x in files])
    todownload = []
    for link in wiki_urls:
        name = link.split('/')[-1]
        if name not in donwload:
            todownload.append(link)
    with open("links1.txt", "w") as f:
        for x in todownload:
            f.write(x+'\n')


if __name__ == "__main__":
    get_dumps()
    names = get_names()
    gen_links()
    # gen_links1()
"""
[I 220613 23:29:12 download:62] ('languages', 189)
[I 220613 23:29:12 download:63] ('languages', {'kn', 'fr', 'sg', 'or', 'wb', 'sn', 'sa', 'bs', 'ua', 'ks', 'da', 'ff', 'ie', 'dk', 'li', 'bo', 'mr', 'nl', 'os', 'tk', 'kg', 'ar', 'lt', 'bn', 'eo', 'sl', 'ht', 'mx', 'ee', 'ms', 'bm', 'lg', 'ur', 'sk', 'fj', 'iu', 'eu', 'sq', 'ge', 'ky', 'su', 'yo', 'ja', 'zh', 'bg', 'lo', 'ro', 'av', 'kr', 'ba', 'lb', 'ts', 'tr', 'la', 'ig', 'hi', 'rn', 'fa', 'hy', 'wa', 'km', 've', 'xh', 'cu', 'no', 'hr', 'rs', 'cr', 'en', 'fo', 'bh', 'zu', 'ug', 'mk', 'ty', 'ay', 'ti', 'be', 'ha', 'ak', 'mi', 'ru', 'ab', 'ce', 'ps', 'gu', 'de', 'ss', 'th', 'lv', 'wo', 'ta', 'tw', 'rw', 'ik', 'om', 'ne', 'jv', 'he', 'br', 'az', 'nv', 'kj', 'yi', 'mg', 'gl', 'cn', 'vi', 'co', 'sd', 'dz', 'st', 'it', 'my', 'gd', 'nz', 'et', 'nn', 'sh', 'se', 'kv', 'pa', 'mt', 'tg', 'si', 'uk', 'ka', 'kk', 'cs', 'cy', 'es', 'vo', 'na', 
'is', 'sm', 'aa', 'ia', 'hz', 'pi', 'pl', 'io', 'sr', 'ki', 'tn', 'ml', 'ny', 'gr', 'fy', 'qu', 'tl', 'ii', 'kw', 'sc', 'bi', 'ng', 'kl', 'hu', 'to', 'cv', 'za', 'ku', 'af', 'el', 'gv', 'fi', 'mh', 'sv', 'tt', 'mn', 'id', 'ch', 'an', 'bd', 'ho', 'ga', 'oc', 'as', 'ko', 'te', 'sw', 'uz', 'ca', 'dv', 'ln', 'pt', 'gn', 'am', 'rm', 'so'})  
[I 220613 23:29:12 download:64] ('files', 700)
"""
