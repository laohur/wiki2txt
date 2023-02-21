## wiki2text

wiki2text is a easy tool for extract wiki.xml.dump/wiki.cirrus.dump to plain text.

## wiki.xml.dump
    
    download from http://ftp.acc.umu.se/mirror/wikimedia.org/dumps/
    python xml_extractor.py  --src="zhwiki-20230101-pages-articles.xml.bz2" --tgt="zhwiki.json.gz" --compress_type=gz  

## wiki.cirrus.dump
    download from https://ftp.acc.umu.se/mirror/wikimedia.org/other/cirrussearch/
    python cirrus_extractor.py  --src="enwiki-20230130-cirrussearch-content.json.gz" --tgt="enwiki.json.gz" --compress_type=gz  




## wiki-1m-corpus
* corpus/wiki-1m.zip
* 179 languages  1MB