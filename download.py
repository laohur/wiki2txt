#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import re


def get_langs():
    alphabet = ''.join(chr(x) for x in range(ord('a'), ord('z')+1))
    langs = []
    for x in alphabet:
        for y in alphabet:
            langs.append(x+y)
    return langs


langs = get_langs()

# https://ftp.acc.umu.se/mirror/wikimedia.org/other/cirrussearch/current/
files = open("files.txt").read().splitlines()

# cbk_zamwiki-20220117-cirrussearch-general.json.gz

names = []
for f in files:
    if not f.endswith("-cirrussearch-content.json.gz"):
        continue
    name = f.split('-')[0]
    if name[2:5] == "wik":
        names.append(f)

    # https://ftp.acc.umu.se/mirror/wikimedia.org/other/cirrussearch/current/amwikimedia-20220117-cirrussearch-content.json.gz
host = "https://saimei.ftp.acc.umu.se/mirror/wikimedia.org/other/cirrussearch/current/"
with open("wiki_urls.txt", "w") as f:
    for name in names:
        link = host+name
        f.write(link+'\n')
