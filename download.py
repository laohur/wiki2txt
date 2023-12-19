#!/usr/bin/env python
# -*- coding: utf-8 -*-


if __name__ == "__main__":
    """
    https://mirror.accum.se/mirror/wikimedia.org/other/cirrussearch/
    aawiki-20230904-cirrussearch-content.json.gz
    https://mirror.accum.se/mirror/wikimedia.org/other/cirrussearch/20230904/aawiki-20230904-cirrussearch-content.json.gz
    """
    names=open("names.txt").read().splitlines()
    names=[x for x in names if len(x)>=4 and x[2:].startswith("wiki") or x[3:].startswith("wiki")   ]

    for name in names:
        # url=f"https://mirror.accum.se/mirror/wikimedia.org/dumps/zhwiki/20231201/zhwiki-20231201-pages-articles.xml.bz2"
        url=f"https://mirror.accum.se/mirror/wikimedia.org/dumps/{name}/20231201/{name}-20231201-pages-articles.xml.bz2"
        print(url)
        