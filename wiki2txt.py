#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import json
import os

def extract2doc(bz_path,doc_dir='./',processes=4):
    # return __doc/AA/
    # python ./WikiExtractor.py --json /media/u/t1/data/wiki/xml/betawikiversity-20200520-pages-articles-multistream.xml   -o /media/u/t1/data/wiki/json  --processes 4  -b 1000000000000   
    cmd=['python','./WikiExtractor.py',bz_path,'--processes ',str(processes),'-b 1000000000000 ','--json']
    if doc_dir:
        cmd+=['-o',doc_dir]
    subprocess.call(' '.join(cmd), shell=True)
    doc_path= doc_dir+'/AA/wiki_00'
    print(f" bz_path:{bz_path} ---->    doc_path:{doc_path}")
    return doc_path

def plain(doc_path,text_path,chuck_size=10000):
    import re
    def plain_line(line):
        sentence_delimiter = ['。','？','?','！','!','；',';']
        sentence_delimiter+=['.\'','."',';','!','. ']
        for delimiter in sentence_delimiter:
             line = re.sub(re.escape(delimiter), r"\g<0>\n", line)
        line = re.sub(r'^\s+', '', line)
        line = re.sub(r'\s+$', '', line)
        # return line
        lines=line.split('\n')
        doc=[]
        for line in lines:
            if line and len(line)>1:
                doc.append(line)
        return '\n'.join(doc)

    buffer=[]
    infile=open(doc_path,'r')
    outfile=open(text_path,'w')
    for line in infile:
        item=json.loads(line)
        line=item['text']
        line=plain_line(line)
        buffer.append(line+'\n\n')
        if len(buffer)>=chuck_size:
            # outfile.writelines([ line +'\n'  for line in buffer])
            outfile.writelines(buffer)
            buffer=[]
    if len(buffer)>0:
            # outfile.writelines([ line +'\n'  for line in buffer])
            outfile.writelines(buffer)

    infile.close()
    outfile.close()
    print(f" doc_path:{doc_path} plained --> text_path{text_path} ")


def simplify(text_path,simplified_path):
    cmd = ["opencc", "-i", text_path, "-o", simplified_path, "-c", "t2s.json"]
    subprocess.call(' '.join(cmd), shell=True)
    print(f" text_path:{text_path} simplified --> simplified_path:{simplified_path}")

def process_wiki(wiki_dir,dump):

    bz_dir=wiki_dir+'bz/'
    doc_dir=wiki_dir+'_doc'

    bz_file=bz_dir+dump+'.xml.bz2'
    doc_path=extract2doc(bz_file,doc_dir)  #/media/u/t1/data/wiki/_doc/AA/wiki_00
    # doc_path='/media/u/t1/data/wiki/_doc/AA/wiki_00'
    
    plain_dir=wiki_dir+'plain/'
    plain_path=plain_dir+dump+'.txt'
    plain(doc_path,plain_path)
    # doc_path='/media/u/t1/data/wiki/_doc/AA/wiki_00'
    
    simplified_dir=wiki_dir+"simplified/"
    simplified_path=simplified_dir+dump+'.txt'
    simplify(plain_path,simplified_path)    
    # doc_path='/media/u/t1/data/wiki/_doc/AA/wiki_00'





if __name__=='__main__':
    wiki_dir="/media/u/t1/data/wiki/"
    # dump="zhwikiversity-20200520-pages-articles-multistream"
    # process_wiki(wiki_dir,dump)
    

    bz_dir=wiki_dir+'bz/'
    suffix='.xml.bz2'
    dumps=[]
    for file in os.listdir(bz_dir):
        if  file.endswith(suffix):
            dump=file[:-len(suffix)]
            # print(dump)
        # process_wiki(wiki_dir,dump)
            dumps.append(dump)
    
    print(f" dumps:",'\n'.join(dumps))
    for dump in dumps:
        process_wiki(wiki_dir,dump)


    '''
 bz_path:/media/u/t1/data/wiki/bz/zhwikiversity-20200520-pages-articles-multistream.xml.bz2 ---->    doc_path:/media/u/t1/data/wiki/_doc/AA/wiki_00
doc_path:/media/u/t1/data/wiki/_doc/AA/wiki_00 plained --> text_path/media/u/t1/data/wiki/plain/zhwikiversity-20200520-pages-articles-multistream.txt 
text_path:/media/u/t1/data/wiki/plain/zhwikiversity-20200520-pages-articles-multistream.txt simplified --> simplified_path:/media/u/t1/data/wiki/simplified/zhwikiversity-20200520-pages-articles-multistream.txt
    '''