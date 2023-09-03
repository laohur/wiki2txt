#!/usr/bin/env python
# -*- coding: utf-8 -*-
import bz2
import lzma
import subprocess
import sys
import json
import os
import re
import argparse
import gzip

from logzero import logger

def readStream(input_file):
    if input_file == '-':
        return sys.stdin
    if input_file.endswith('.xz'):
        input = lzma.open(input_file,"rt",errors="ignore")
    elif input_file.endswith('.bz2'):
        input = bz2.open(input_file,"rt",errors='ingore')
    elif input_file.endswith('.zip'):
        pipe = subprocess.Popen(
            "unzip -p "+input_file, shell=True, stdout=subprocess.PIPE, errors='ingore')
        return pipe.stdout
    elif input_file.endswith('.gz'):
        input = gzip.open(input_file,"rt",errors="ignore")
    else:
        input = open(input_file,errors='ingore')
    return input
# https://github.com/attardi/wikiextractor



def parse_line(a, b):
    index = json.loads(a)
    content = json.loads(b)
    type = index['index']['_type']
    # revision = content['version']
    # if type == 'page' and content['namespace'] == 0:
    if type == '_doc' and content['namespace'] == 0:
        # opening_text =   # content['opening_text']

        text = content['text']
        # drop references:
        # ^ The Penguin Dictionary
        text = re.sub(r'  \^ .*', '', text).strip()

        # doc = text.splitlines()
        # doc=[x.strip() for x in doc if x.strip() ]
        # urlbase = 'http://it.wikipedia.org/'
        # urlbase = f'http://{language}.wikipedia.org/'
        # url = urlbase + 'wiki?curid=' + id
        # header = '<doc id="%s" url="%s" title="%s" language="%s" revision="%s">\n' % (
        #     id, url, title, language, revision)
        # page = header + title + '\n\n' + text + '\n</doc>\n'
        if not text or len(text) < 64:
            return
        page={
            "id":index['index']['_id'],
            "language":content['language'],
            'wiki':content['wiki'],
            "title":content['title'],
            "opening_text":content.get('opening_text',""),
            "text":text,
        }
        return page


def process_dump(input_file, out_file, compress_type=""):
    """
    :param input_file: name of the wikipedia dump file; '-' to read from stdin
    :param out_file: directory where to store extracted data, or '-' for stdout
    :param file_size: max size of each extracted file, or None for no max (one file)
    :param file_compress: whether to compress files with bzip.
    """

    # if input_file == '-':
    #     input = sys.stdin
    # else:
    #     input = gzip.open(input_file)
    input=readStream(input_file)

    if out_file == '-':
        output = sys.stdout
    else:
        if not compress_type:
            output = open(out_file, "w")
        elif compress_type == "bz2":
            output = bz2.BZ2File(out_file, 'w')
        elif compress_type == "gz":
            output = gzip.GzipFile(out_file, 'w')
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
        n_src += 1
        page = parse_line(line, doc)
        if not page:
            continue
        l = json.dumps(page, ensure_ascii=False) + '\n'
        if compress_type:
            l = l.encode('utf-8', errors="ignore")
        output.write(l)
        n_tgt += 1
        if n_src % 100000 == 0:
            logger.info(f"{n_src} --> {out_file} {n_tgt}")
    output.close()
    return n_src, n_tgt


def extract(src, tgt, compress_type="",):
    n_src, n_tgt = process_dump(src, tgt, compress_type)
    line=f" {src}:{n_src} --> {tgt}:{n_tgt} "
    logger.info(line)
    if not n_tgt:
        os.system(f"rm {tgt}")
        logger.warning(f" --> empty {tgt}  cleaned!")
        return
    return line


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", default="")
    parser.add_argument("--tgt", default="-")
    parser.add_argument("--compress_type", default="")
    args = parser.parse_args()

    extract(args.src, args.tgt, args.compress_type)


