#!/usr/bin/env python
# -*- coding: utf-8 -*-
import bz2
import lzma
import sys
import traceback
import glob
import subprocess
import json
import os
import requests
import re
import random
import time
import shutil
from logzero import logger

import gzip

# https://github.com/attardi/wikiextractor

def parse_line(a,b):
    page=""
    index = json.loads(a)
    content = json.loads(b)
    type = index['index']['_type']
    id = index['index']['_id']
    language = content['language']
    revision = content['version']
    if type == 'page' and content['namespace'] == 0:
        title = content['title']
        text = content['text']
        # drop references:
        # ^ The Penguin Dictionary
        text = re.sub(r'  \^ .*', '', text)
        # urlbase = 'http://it.wikipedia.org/'
        urlbase = f'http://{language}.wikipedia.org/'
        url = urlbase + 'wiki?curid=' + id
        header = '<doc id="%s" url="%s" title="%s" language="%s" revision="%s">\n' % (
            id, url, title, language, revision)
        page = header + title + '\n\n' + text + '\n</doc>\n'
    return page

def process_dump(input_file, out_file, compress_type=""):
    """
    :param input_file: name of the wikipedia dump file; '-' to read from stdin
    :param out_file: directory where to store extracted data, or '-' for stdout
    :param file_size: max size of each extracted file, or None for no max (one file)
    :param file_compress: whether to compress files with bzip.
    """

    if input_file == '-':
        input = sys.stdin
    else:
        input = gzip.open(input_file)

    if out_file == '-':
        output = sys.stdout
    else:
        if compress_type == "bz2":
            output = bz2.BZ2File(out_file + '.bz2', 'w')
        elif compress_type == "xz":
            output = lzma.open(out_file+'.xz', "w")
        else:
            output = open(out_file, "w")

    # process dump
    # format
    # {"index":{"_type":"page","_id":"3825914"}}
    # {"namespace":0,"title":TITLE,"timestamp":"2014-06-29T15:51:09Z","text":TEXT,...}
    n_line = 0
    while True:
        line = input.readline()
        if not line:
            break
        doc = input.readline()
        n_line += 2
        try:
            page=parse_line(line,doc)
            if page:
                output.write(page.encode('utf-8'))
        except Exception as e:
            logger.error(e)
    return n_line


def extract_wiki(src, tgt, compress_type=""):
    xz = tgt+'.xz'
    # if not os.path.exists(tgt) and os.path.exists(xz):
    # return f" {xz} exists"
    # return ''
    for p in [tgt, xz]:
        if os.path.exists(p):
            os.remove(p)
    logger.info(f"{src}  -->  ...")
    n_line = process_dump(src, tgt, compress_type)
    logger.info(f" -->  {tgt} n_line:{n_line}")
    # os.system(f"xz {tgt}")
    return tgt


def mparse():

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--lang', default="global",  type=str)
    args = parser.parse_args()
    print(args)
    lang = args.lang
    gzs = list(glob.iglob(
        f"F:/data/wiki-20220124-cirrussearch-content.json.gz/*.gz", recursive=True))

    params = []
    for src in gzs:
        name = os.path.basename(src)
        src = "F:/data/wiki-20220124-cirrussearch-content-json-gz/"+name
        if not os.path.exists(src):
            continue
        t = name.rstrip(".json.gz")
        tgt = "F:/data/wiki-20220124-cirrussearch-content-txt-xz/"+t+'.txt'
        param = (src, tgt)
        params.append(param)

    random.shuffle(params)
    import multiprocessing
    with multiprocessing.Pool(6) as pool:
        re = pool.imap_unordered(extract_wiki, params)
        for x in re:
            logger.info(x)


def parse_all():
    srcs = glob.glob(
        rf"F:/data/wiki-20220124-cirrussearch-content-json-gz/*.gz")
    for src in srcs:
        name=os.path.basename(src)
        t = name.rstrip(".json.gz")
        # if not t.startswith("enwiki"):
            # continue
        tgt = "F:/data/wiki-20220124-cirrussearch-content-txt-xz/"+t+'.txt'
        extract_wiki(src, tgt, 'xz')
        # break


if __name__ == '__main__':
    parse_all()
