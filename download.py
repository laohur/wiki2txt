#!/usr/bin/env python
# -*- coding: utf-8 -*-
import glob
import requests
import re


def get_langs():
    alphabet = ''.join(chr(x) for x in range(ord('a'), ord('z')+1))
    langs = []
    for x in alphabet:
        for y in alphabet:
            langs.append(x+y)
    return langs


def get_names():
    # https://ftp.acc.umu.se/mirror/wikimedia.org/other/cirrussearch/20220124/
    files = open("files.txt").read().splitlines()

    # cbk_zamwiki-20220117-cirrussearch-general.json.gz

    names = []
    for f in files:
        if not f.endswith("-cirrussearch-content.json.gz"):
            continue
        name = f.split('-')[0]
        if name[2:5] == "wik":
            names.append(f)
    return names


def gen_links():
    names = get_names()
    # https://ftp.acc.umu.se/mirror/wikimedia.org/other/cirrussearch/20220124/advisorywiki-20220124-cirrussearch-content.json.gz
    host = "https://ftp.acc.umu.se/mirror/wikimedia.org/other/cirrussearch/20220124/"
    with open("wiki_urls.txt", "w") as f:
        for name in names:
            link = host+name
            f.write(link+'\n')


def gen_links1():
    import os
    wiki_urls = open("wiki_urls.txt").read().splitlines()
    files = glob.glob(
        r"F:/data/wiki-20220124-cirrussearch-content-json-gz/*")
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
    gen_links()
    gen_links1()
