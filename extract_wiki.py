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


def parse_line(a, b):
    # page = ""
    text = ""
    index = json.loads(a)
    content = json.loads(b)
    type = index['index']['_type']
    # id = index['index']['_id']
    # language = content['language']
    # revision = content['version']
    if type == 'page' and content['namespace'] == 0:
        # title = content['title']
        text = content['text']
        # drop references:
        # ^ The Penguin Dictionary
        text = re.sub(r'  \^ .*', '', text)
        # urlbase = 'http://it.wikipedia.org/'
        # urlbase = f'http://{language}.wikipedia.org/'
        # url = urlbase + 'wiki?curid=' + id
        # header = '<doc id="%s" url="%s" title="%s" language="%s" revision="%s">\n' % (
        #     id, url, title, language, revision)
        # page = header + title + '\n\n' + text + '\n</doc>\n'
    return text.strip()


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
        if not compress_type:
            output = open(out_file, "w")
        elif compress_type == "bz2":
            output = bz2.BZ2File(out_file + '.bz2', 'w')
        elif compress_type == "xz":
            output = lzma.open(out_file+'.xz', "w")
        elif compress_type == "test":
            output = None
        else:
            raise ValueError("invalid compress_type "+compress_type)

    # process dump
    # format
    # {"index":{"_type":"page","_id":"3825914"}}
    # {"namespace":0,"title":TITLE,"timestamp":"2014-06-29T15:51:09Z","text":TEXT,...}
    n_line = 0
    while True:
        line = input.readline()
        if not line:
            break
        if not output:
            continue
        doc = input.readline()
        n_line += 2
        try:
            page = parse_line(line, doc)
            if page:
                page += '\n'
                output.write(page.encode('utf-8'))
        except Exception as e:
            logger.error(e)
    return n_line


def extract_wiki(src, tgt, compress_type=""):
    if os.path.exists(tgt):
        os.remove(tgt)
    xz = tgt+'.xz'
    if os.path.exists(xz):
        logger.info(f" -->  {xz}  exists!")
        return
    logger.info(f"{src}  -->  ...")
    try:
        n_line = process_dump(src, tgt, compress_type)
        logger.info(f" -->  {tgt} n_line:{n_line}")
    except Exception as e:
        logger.error(e)
        if os.path.exists(xz):
            os.remove(xz)
            logger.warning(f" -->  {xz}  removed!")
            return
    return tgt


def parse_all(lang="*", compress_type="xz"):
    srcs = glob.glob(
        rf"F:/data/wiki-20220131-cirrussearch-content-json-gz/{lang}*.gz")
    srcs = list(srcs)
    srcs.sort()
    for src in srcs:
        name = os.path.basename(src)
        t = name.rstrip(".json.gz")
        if t[:2] <= 'a ':
            continue
        tgt = "F:/data/wiki-20220131-cirrussearch-content-txt-xz/"+t+'.txt'
        extract_wiki(src, tgt, compress_type)
        # break


def test_all(lang="a0", compress_type="test"):
    srcs = glob.glob(
        rf"F:/data/wiki-20220131-cirrussearch-content-json-gz/{lang}*.gz")
    srcs = list(srcs)
    srcs.sort()
    for src in srcs:
        name = os.path.basename(src)
        t = name.rstrip(".json.gz")
        if t[:2] <= lang:
            continue
        tgt = "F:/data/wiki-20220131-cirrussearch-content-txt-xz/"+t+'.txt'
        extract_wiki(src, tgt, compress_type)
        # break


if __name__ == '__main__':
    # test_all()
    parse_all()
