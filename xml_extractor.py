import bz2
import gzip
import json
import lzma
import multiprocessing
import os
import subprocess
import sys
import unicodedata

from gensim.corpora.wikicorpus import extract_pages, filter_wiki
from logzero import logger


def valid_line(l):
    for x in l :
        if unicodedata.category(x)[0] in 'LN':
            return True
    return False

def parse_wiki(wiki):
    title, text, pageid = wiki
    # if title=='Aaron':
    #     d=0
    doc = filter_wiki(text).splitlines()
    doc = [x.strip() for x in doc if x.strip()]
    doc = [x for x in doc if valid_line(x)]
    if not doc or sum(len(x) for x in doc) < 64:
        return
    page = {"title": title, "text": doc}
    return page


def extract(src, out_file, compress_type=''):
    logger.info(f"extract {src}")
    pipe = subprocess.Popen(
        f"bzcat  {src}",shell=True, stdout=subprocess.PIPE, encoding='utf-8', errors='ignore')
    wikis = extract_pages(pipe.stdout)

    if out_file == '-':
        output = sys.stdout
    else:
        if not compress_type:
            output = open(out_file, "w")
        elif compress_type == "bz2":
            output = bz2.BZ2File(out_file, 'w')
        elif compress_type == "gz":
            output = gzip.GzipFile(out_file, 'w')
        elif compress_type == "xz":
            output = lzma.open(out_file, "w")
        else:
            raise ValueError("invalid compress_type "+compress_type)

    batch = []
    n = 0
    pool = multiprocessing.Pool(max(1, os.cpu_count()//2))
    for i, wiki in enumerate(wikis):
        batch.append(wiki)
        if len(batch) >= 1e5:
            re = pool.imap_unordered(parse_wiki, batch)
            for page in re:
                if page:
                    line = json.dumps(page, ensure_ascii=False)+'\n'
                    if compress_type:
                        line = line.encode('utf-8', errors="ignore")
                    output.write(line)
                    n += 1
            batch = []
            logger.info(f"{i}--> {out_file} {n}")
    if len(batch) > 0:
        re = pool.imap_unordered(parse_wiki, batch)
        for page in re:
            if page:
                line = json.dumps(page, ensure_ascii=False)+'\n'
                if compress_type:
                    line = line.encode('utf-8', errors="ignore")
                output.write(line)
                n += 1
        batch = []
        logger.info(f"{i}--> {out_file} {n}")
    output.close()
    if n == 0:
        logger.warning(f" {src} {i} extract --> {out_file} {n} pages ")
        cmd = f"rm {out_file}"
        os.system(cmd)
    else:
        logger.info(f" {src} {i} extract --> {out_file} {n} pages")
    return (out_file, i)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", default="")
    parser.add_argument("--tgt", default="")
    parser.add_argument("--compress_type", type=str, default="")
    args = parser.parse_args()

    extract(args.src,args.tgt, compress_type=args.compress_type)

