## wiki-processer

## prepare
* donwnload wiki/dumps/*.xml.bz to wiki/bz  
     example    wget -O wiki/bz/   -c "https://ftp.acc.umu.se/mirror/wikimedia.org/dumps/zhwiki/20200520/zhwiki-20200520-pages-articles-multistream.xml.bz2" 
* [optional for simplify chinese]     
     sudo apt install -y opencc     or pip install opencc

## usage
    python wiki2text.py

it will do as blows:

    1. extract to json 

    2.  plain json to lines
            line +'\n'
            item+'\n\n'

    3.  simplify  chinese [optional]

## paths of "zhwikiversity-20200520-pages-articles"
    bz_path:/media/u/t1/data/wiki/bz/zhwikiversity-20200520-pages-articles.xml.bz2 ---->    doc_path:/media/u/t1/data/wiki/_doc/AA/wiki_00
    doc_path:/media/u/t1/data/wiki/_doc/AA/wiki_00 plained --> text_path/media/u/t1/data/wiki/plain/zhwikiversity-20200520-pages-articles.txt  
    simplified_path:/media/u/t1/data/wiki/simplified/zhwikiversity-20200520-pages-articles.txt    traditional_path:/media/u/t1/data/wiki/traditional/zhwikiversity-20200520-pages-articles.txt
    

##  preprocessed and  download


链接link: https://pan.baidu.com/s/19WlO9Jr4TPRq5BYKTqur3A  密码passwd: emv3

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


## reference 
* https://github.com/howl-anderson/chinese-wikipedia-corpus-creator
* https://github.com/attardi/wikiextractor