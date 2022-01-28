#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, traceback
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
def read_gz(p):
    input=gzip.open(p)
    while True:
        line =input.readline()
        if not line:
            break
        yield line

def get_name(path):
    name=os.path.basename(path)
    name=name.split('.')[0]
    name=name.split('-')[0]
    return name

import shutil
def extract_wiki(src):
    # src=f"F:/data/wiki-20211122-cirrussearch-content.json.gz/zhwikibooks-20211122-cirrussearch-content.json.gz"
    # name=src.split('/')[-1]
    # name=os.path.basename(src)
    # name=name.split('-')[0]
    name=get_name(src)
    tgt=f"F:/data/wiki-20211122-cirrussearch-content/{name}.txt"
    xz=tgt+'.xz'
    prefix=name.split('wik')[0]
    # print(f"{name} --> {prefix} \n")
    if len(prefix)!=2:
        for p in [xz,tgt,src]:
            if os.path.exists(p):
                logger.warn(f" {p} removed !")
                os.remove(p)
    if not os.path.exists(tgt) and os.path.exists(xz):
        return f" {xz} exists" 
    # return ''
    logger.info( f"{src}  -->  {tgt} ..." )
    i=0
    with open(tgt,'w') as f:
        input=gzip.open(src,mode='rt',errors='replace',newline='')
        while True:
            a = ''
            i+=1
            try:
                a = input.readline()
                # index = json.loads(a)
                if not a:
                    break
                b=input.readline()
                content = json.loads(b)
                # type = index['index']['_type']
                # id = index['index']['_id']
                # language = content['language']
                # revision = content['version']
                # if type == 'page' and content['namespace'] == 0:
                    # title = content['title']
                    # text = content['text']
                    # drop references:
                    # ^ The Penguin Dictionary
                if 'text' in content:
                    text=content['text']
                    text = re.sub(r'  \^ .*', '', text).strip()       
                    f.write(text+'\n\n')
            except Exception as e:
                logger.error(e)
            if not a:
                break                
    os.system(f"xz {tgt}")
    logger.info( f"{src}  -->  {tgt} lines:{i}" )
    return tgt


if __name__=='__main__':

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--lang', default="global",  type=str)
    args = parser.parse_args()
    print(args)
    lang=args.lang
    gzs = list(glob.iglob(f"F:/data/wiki-20211122-cirrussearch-content.json.gz/*.gz", recursive=True))
    random.shuffle(gzs)
    import multiprocessing
    with multiprocessing.Pool(6) as pool:
        re=pool.imap_unordered(extract_wiki,gzs)
        for x in re:
            logger.info(x)


