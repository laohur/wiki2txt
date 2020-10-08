#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, traceback
import glob
import subprocess
import json
import os
from ltp import LTP

pouncts='。，、＇：∶；?‘’“”""'
pouncts += "'',.?!:;"
pouncts = set(list(pouncts))
print(f"pouncts {pouncts}")

def extract2doc(bz_path,tmp_dir='_tmp'):
    if os.path.exists(tmp_dir):
        raise Exception(f"{tmp_dir} exists! " )
        sys.exit()
    # process=os.cpu_count()-2
    cmd = ['python  ./WikiExtractor.py ', bz_path, '-b 30m', '--json  -o', tmp_dir]
    #  python ./WikiExtractor.py  /media/u/t1/data/wiki/bz/zhwiki-20200520-pages-articles.xml.bz2 --processes 4 -b 40m --json -o  ./json
    #  python ./WikiExtractor.py  /media/u/t1/data/wiki/bz/zhwiki-20200520-pages-articles.xml.bz2 --processes 4 -b 40m  -o  ./json
    cmd=' '.join(cmd)
    print(f" extract2doc start cmd:{cmd}  bz_path:{bz_path}   .......")
    subprocess.call(cmd, shell=True)

def detect_doc(doc):
    n_p, n_c = 0, 0
    for line in doc:
        n_c += len(line)
        for c in line:
            if c in pouncts:
                n_p+=1
    p = n_p / n_c
    return p>0.05

def plain_doc(doc,t2s=False,s2t=False):
    for i in range(len(doc)):
        doc[i] = doc[i].strip()

    if t2s:
        import opencc
        t2s = opencc.OpenCC('t2s.json')
        doc = [t2s.convert(line) for line in doc]
    if s2t:
        import opencc    
        s2t = opencc.OpenCC('s2t.json')
        doc=[  s2t.convert(line)  for line in doc  ]

    lines=ltp.sent_split(doc)
    doc = [x for x in lines if x]
    return doc

def plain_file(src,tgt):
    folder=[]
    for line in open(src).readlines():
        item=json.loads(line.strip())
        text=item['text']
        doc=text.split("\n")
        if detect_doc(doc):
            doc = plain_doc(doc)
            folder.append('\n'.join(doc))
    print(f" {src} extracted {len(folder)} doc   ")
    if len(folder)>100:
        with open(tgt, 'w') as w:
            w.writelines("\n\n".join(folder)+"\n\n")
            print( f" plained -> {tgt}" )

def wiki2text(src, tgt):
    tmp_dir =  '_tmp'
    extract2doc(src,tmp_dir)
    files = glob.iglob(f"{tmp_dir}/*/*", recursive=True)
    files = list(files)
    files.sort()
    print(f" {tmp_dir} found {len(files)} files")
    for source in files:
        name = os.path.basename(source)
        target=os.path.join(tgt,name+".txt")
        plain_file(source, target)
    print(f" {src} plained {len(files)} -->{tgt} ")

if __name__=='__main__':
    ltp = LTP()  # 默认加载 Small 模型
    src = "/media/u/t1/data/wiki/bz/zhwiki-20200920-pages-articles.xml.bz2"
    tgt = "/media/u/t1/data/self/zhwiki"
    
    src = "/media/u/t1/data/wiki/bz/zhwikisource-20200920-pages-articles.xml.bz2"
    tgt = "/media/u/t1/data/self/zhwikisource"

    wiki2text(src,tgt)
