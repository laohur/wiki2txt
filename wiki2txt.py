#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import json
import os


def extract2doc(bz_path,doc_path,doc_dir='.'):
    # return __doc/AA/
    # python ./WikiExtractor.py --json /media/u/t1/data/wiki/xml/betawikiversity-20200520-pages-articles-multistream.xml   -o /media/u/t1/data/wiki/json  --processes 4  -b 1000000   
    json_dir=doc_dir+'_json/'
    process=os.cpu_count()-1
    # cmd=['python','./WikiExtractor.py',bz_path,'-b 30m --processes ', str(process),  '--json  -o',json_dir]
    # cmd=['python  ./WikiExtractor.py ',bz_path,'-b 30m ',  '--json  -o',json_dir]
    cmd=['python',  './WikiExtractor.py',bz_path,  '--json',  '-o',json_dir]
    cmd=' '.join(cmd)
    # cmd=f" python  ./WikiExtractor.py {bz_path} --json -o {json_dir} "
    print(f" extract2doc start cmd:{cmd}  bz_path:{bz_path} ---->    doc_path:{json_dir}   .......")
    # os.system(' '.join(cmd)+" | 1 > extractor.log")
    # subprocess.call(cmd, shell=True)
    subprocess.call(cmd, shell=True)
    # with open("extractor.log","w") as fout:
        # os.open(' '.join(cmd),stdout=fout)
        # subprocess.Popen(' '.join(cmd),stdout=fout)

    print(f" cat _json_path:{json_dir} ---->    doc_path:{doc_path}")
    # doc_path= doc_dir+'/dump.json'
    cmd=[" find ",json_dir," -name 'wiki*' -exec cat {} \; > ",doc_path]
    subprocess.call(' '.join(cmd), shell=True)

    cmd=f" rm -rf {json_dir}/*"
    subprocess.call(cmd, shell=True)
    # cmd=[" rm -rf  ",json_dir]
    # subprocess.call(' '.join(cmd), shell=True)

    return doc_path

def plain(doc_path,text_path,simplified_path='',traditional_path='', chuck_size=100000):
    import re
    import opencc
    t2s = opencc.OpenCC('t2s.json')
    s2t = opencc.OpenCC('s2t.json')
    def plain_line(line):
        sentence_delimiter = (
            '。',
            '. ',
            '？',
            '?',
            '！',
            '!',
            '；',
            ';',
            '。。。。。。',
            '...'
        )
        sentence_delimiter=list(set(sentence_delimiter))
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
    simpfile=open(simplified_path,'w') if simplified_path else None
    tradifile=open(traditional_path,'w') if traditional_path else None
    for line in infile:
        item=json.loads(line)
        line=item['text']
        line=plain_line(line)
        buffer.append(line+'\n\n')
        # converter.convert('汉字')  # 漢字
        if len(buffer)>=chuck_size:
            # outfile.writelines([ line +'\n'  for line in buffer])
            outfile.writelines(buffer)
            if simpfile:
                buffer2=[  t2s.convert(line)  for line in buffer  ]
                simpfile.writelines(buffer2)
            if tradifile:
                buffer2=[  s2t.convert(line)  for line in buffer  ]
                tradifile.writelines(buffer2)
            buffer=[]
    if len(buffer)>0:
            # outfile.writelines([ line +'\n'  for line in buffer])
            outfile.writelines(buffer)
            if simpfile:
                buffer2=[  t2s.convert(line)  for line in buffer  ]
                simpfile.writelines(buffer2)
                buffer2=[  s2t.convert(line)  for line in buffer  ]
                tradifile.writelines(buffer2)
                # print(buffer[:10])
                # print(simpbuffer[:10])
    
    infile.close()
    outfile.close()
    print(f" doc_path:{doc_path} plained --> text_path{text_path}  ")
    if simpfile:
        simpfile.close()
        print(f"  simplified_path:{simplified_path}   ")
    if tradifile:
        tradifile.close()
        print(f"  traditional_path:{traditional_path}")


def simplify(text_path,simplified_path):
    cmd = ["opencc", "-i", text_path, "-o", simplified_path, "-c", "t2s.json"]
    subprocess.call(' '.join(cmd), shell=True)
    print(f" text_path:{text_path} simplified --> simplified_path:{simplified_path}")

def process_wiki(wiki_dir,dump):

    bz_dir=wiki_dir+'bz/'
    doc_dir=wiki_dir+'doc/'

    bz_file=bz_dir+dump+'.xml.bz2'
    doc_path= doc_dir+dump+'.json'

    doc_path=extract2doc(bz_file,doc_path,doc_dir)  #/media/u/t1/data/wiki/_doc/AA/wiki_00
    # doc_path='/media/u/t1/data/wiki/_doc/AA/wiki_00'
    
    plain_dir=wiki_dir+'plain/'
    plain_path=plain_dir+dump+'.txt'
    
    simplified_path,traditional_path='',''
    if dump.startswith('zhwik') :
        simplified_path=wiki_dir+"simplified/"+dump+'.txt'
        traditional_path=wiki_dir+"traditional/"+dump+'.txt'
    plain(doc_path,plain_path,simplified_path,traditional_path)
    # doc_path='/media/u/t1/data/wiki/_doc/AA/wiki_00'
    
    # simplified_dir=wiki_dir+"simplified/"
    # simplified_path=simplified_dir+dump+'.txt'
    # simplify(plain_path,simplified_path)    
    # doc_path='/media/u/t1/data/wiki/_doc/AA/wiki_00'


if __name__=='__main__':
    # demo and test
    wiki_dir="/media/u/t1/data/wiki/"
    # dump="zhwikiversity-20200520-pages-articles"
    # dump="betawikiversity-20200520-pages-articles"
    # process_wiki(wiki_dir,dump)
    # sys.exit()
    
    langs=['ar','de','en','es','fr','it','ja','pt','ru','zh']
    bz_dir=wiki_dir+'bz/'
    suffix='.xml.bz2'
    dumps=[]
    for file in os.listdir(bz_dir):
        if  file.endswith(suffix):
            dump=file[:-len(suffix)]
            # print(dump)
        # process_wiki(wiki_dir,dump)
            dumps.append(dump)
    dumps.sort(reverse=True)
    print(f" dumps:",'\n'.join(dumps))
    for dump in dumps:
        # if dump. startswith(langs[9]+'wik'):
        #     if dump.startswith('zhwikisource') or dump.startswith("zhwiki-"):
        #         continue
        process_wiki(wiki_dir,dump)


    '''
 bz_path:/media/u/t1/data/wiki/bz/zhwikiversity-20200520-pages-articles.xml.bz2 ---->    doc_path:/media/u/t1/data/wiki/_doc/AA/wiki_00
 doc_path:/media/u/t1/data/wiki/_doc/AA/wiki_00 plained --> text_path/media/u/t1/data/wiki/plain/zhwikiversity-20200520-pages-articles.txt  
 simplified_path:/media/u/t1/data/wiki/simplified/zhwikiversity-20200520-pages-articles.txt    traditional_path:/media/u/t1/data/wiki/traditional/zhwikiversity-20200520-pages-articles.txt
 
dumps: arwiki-20200520-pages-articles
arwikisource-20200520-pages-articles
arwiktionary-20200520-pages-articles
dewiki-20200520-pages-articles
dewikisource-20200520-pages-articles
dewiktionary-20200520-pages-articles
enwiki-20200520-pages-articles
enwikibooks-20200520-pages-articles
enwikiquote-20200520-pages-articles
enwikisource-20200520-pages-articles
enwikiversity-20200520-pages-articles
enwikivoyage-20200520-pages-articles
enwiktionary-20200520-pages-articles
eswiki-20200520-pages-articles
eswikisource-20200520-pages-articles
eswiktionary-20200520-pages-articles
frwiki-20200520-pages-articles
frwikisource-20200520-pages-articles
frwiktionary-20200520-pages-articles
itwiki-20200520-pages-articles
itwikisource-20200520-pages-articles
itwiktionary-20200520-pages-articles
jawiki-20200520-pages-articles
jawikisource-20200520-pages-articles
jawiktionary-20200520-pages-articles
ptwiki-20200520-pages-articles
ptwikisource-20200520-pages-articles
ptwiktionary-20200520-pages-articles
ruwiki-20200520-pages-articles
ruwikisource-20200520-pages-articles
ruwiktionary-20200520-pages-articles
zhwiki-20200520-pages-articles
zhwikibooks-20200520-pages-articles
zhwikinews-20200520-pages-articles
zhwikiquote-20200520-pages-articles
zhwikisource-20200520-pages-articles
zhwikiversity-20200520-pages-articles
zhwikivoyage-20200520-pages-articles
zhwiktionary-20200520-pages-articles

    '''