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
import argparse
import gzip

from logzero import logger

# https://github.com/attardi/wikiextractor


def parse_line(a, b):
    page = None
    index = json.loads(a)
    content = json.loads(b)
    type = index['index']['_type']
    # id = index['index']['_id']
    language = content['language']
    # revision = content['version']
    if type == 'page' and content['namespace'] == 0:
        # title = content['title'].strip()   # nosense
        text = content['text'].strip()
        # drop references:
        # ^ The Penguin Dictionary
        text = re.sub(r'  \^ .*', '', text)
        # urlbase = 'http://it.wikipedia.org/'
        # urlbase = f'http://{language}.wikipedia.org/'
        # url = urlbase + 'wiki?curid=' + id
        # header = '<doc id="%s" url="%s" title="%s" language="%s" revision="%s">\n' % (
        #     id, url, title, language, revision)
        # page = header + title + '\n\n' + text + '\n</doc>\n'
        page = text.strip()
    return page, language


def process_dump(input_file, out_file, compress_type="", same_language=False):
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
            output = bz2.BZ2File(out_file, 'w')
        elif compress_type == "xz":
            output = lzma.open(out_file, "w")
        else:
            raise ValueError("invalid compress_type "+compress_type)

    # process dump
    # format
    # {"index":{"_type":"page","_id":"3825914"}}
    # {"namespace":0,"title":TITLE,"timestamp":"2014-06-29T15:51:09Z","text":TEXT,...}
    n_src = 0
    n_tgt = 0
    while True:
        line = input.readline()
        if not line:
            break
        if not output:
            continue
        doc = input.readline()
        n_src += 2
        try:
            page, language = parse_line(line, doc)
            if not page:
                continue
            name = os.path.basename(input_file)
            if same_language and language[:2] != name[:2]:
                logger.warning(
                    f"{ language[:2]}!={name[:2]} ignore {page[:100]} ")
                continue
            page += '\n'
            if compress_type:
                page = page.encode('utf-8')
            output.write(page)
            n_tgt += 1
        except Exception as e:
            logger.error(e)
    return n_src, n_tgt


def extract_wiki(src, tgt, compress_type="", same_language=False):
    if os.path.exists(tgt):
        # os.remove(tgt)
        logger.warning(f" -->  {tgt}  exists!")
        return
    logger.info(f"{src}  -->  ...")
    try:
        n_src, n_tgt = process_dump(src, tgt, compress_type,
                                    same_language=same_language)
        logger.info(f" n_src:{n_src} --> n_tgt：{n_tgt} {tgt} ")
        if not n_tgt:
            os.remove(tgt)
            logger.warning(f" --> empty {tgt}  cleaned!")
            return
    except Exception as e:
        logger.error(e)
        if os.path.exists(tgt):
            os.remove(tgt)
            logger.error(f" -->  {tgt}  cleaned!")
            return

    return tgt


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--src",
                        help="Cirrus Json wiki dump file")
    parser.add_argument("--tgt", default="-")
    parser.add_argument("--compress_type", default="")
    parser.add_argument("--same_language", default=False)

    args = parser.parse_args()
    extract_wiki(args.src, args.tgt, args.compress_type,
                 same_language=args.same_language)
