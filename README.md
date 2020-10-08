## wiki2text

wiki2text is a easy tool for extract wiki.dump to plain,cleand text.
In specially, generate simplified / traditional  text for "zhwik*".

## prepare
* donwnload wiki/dumps/*.xml.bz to wiki/bz  
     example    wget -O wiki/bz/   -c "https://ftp.acc.umu.se/mirror/wikimedia.org/dumps/zhwiki/20200520/zhwiki-20200520-pages-articles-multistream.xml.bz2" 
* [optional for simplify chinese]     
     pip install opencc or  sudo apt install -y opencc  

## usage
    python wiki2text.py

it will do as blows:

    1. extract to small  json  files

    2.  plain json to lines
            line +'\n'
            page+'\n\n'

    3.  simplify /traditionise chinese [optional]

    

## reference 
* https://github.com/howl-anderson/chinese-wikipedia-corpus-creator
* https://github.com/attardi/wikiextractor