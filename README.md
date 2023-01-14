## wiki2text

wiki2text is a easy tool for extract wiki.xml.dump/wiki.cirrus.dump to plain text.

## wiki.xml.dump
* compress_type could be '','bz2','xz
* slim xml page sections

| slim                           |   |   |   |   |
|--------------------------------|---|---|---|---|
| slim=0: keep all sections      |   |   |   |   |
| slim=1: remove igored_sections |   |   |   |   |
| slim=2: keep first section     |   |   |   |   |
| slim=3: keep first paragraph   |   |   |   |   |
    
    download from https://ftp.acc.umu.se/mirror/wikimedia.org/dumps/
    python cirrus_extractor.py --src --tgt --compress_type --language

## wiki.cirrus.dump
    download from https://ftp.acc.umu.se/mirror/wikimedia.org/other/cirrussearch/current/
    python xml_extractor.py  --src --tgt --compress_type --slim




## wiki-1m-corpus
* corpus/wiki-1m.zip
* 179 languages ✖ 1MB