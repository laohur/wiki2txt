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

## download
链接link: https://pan.baidu.com/s/19WlO9Jr4TPRq5BYKTqur3A  密码passwd: emv3

## reference 
* https://github.com/howl-anderson/chinese-wikipedia-corpus-creator
* https://github.com/attardi/wikiextractor