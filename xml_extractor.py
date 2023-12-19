import bz2
import gzip
import json
import lzma
import multiprocessing
import os
import re
import subprocess
import sys
import unicodedata
import html
import regex as re
from gensim.corpora.wikicorpus import extract_pages, filter_wiki
from logzero import logger
from mediawiki_dump.tokenizer import clean
# import wikitextparser as wtp
import mwparserfromhell
import math


def readStream(input_file):
    if input_file == "-":
        return sys.stdin
    if input_file.endswith(".xz"):
        input = lzma.open(input_file, "rt", errors="ignore")
    elif input_file.endswith(".bz2"):
        input = bz2.open(input_file, "rt", errors="ingore")
    elif input_file.endswith(".zip"):
        pipe = subprocess.Popen("unzip -p " + input_file, shell=True, stdout=subprocess.PIPE, errors="ingore")
        return pipe.stdout
    elif input_file.endswith(".gz"):
        input = gzip.open(input_file, "rt", errors="ignore")
    else:
        input = open(input_file, errors="ingore")
    return input


def clean_line(line):
    l = html.unescape(line).strip()
    l = re.sub("[\(|（][\p{C}|p{M}|\p{P}\p{S}|\p{Z}]{1,}[\)|）]", " ", l)
    l = " ".join(x for x in l.split() if x)
    return l


def valid_line(l):
    letters = "".join(x for x in l if unicodedata.category(x)[0] in "L")
    B = len(letters.encode())
    if B < 30:
        return 0
    if B / len(l.encode()) > 0.75:
        return 1
    return 0


def wiki_replace(s):
    # https://spaces.ac.cn/archives/4176
    s = re.sub(":*{\|[\s\S]*?\|}", "", s)
    s = re.sub("<gallery>[\s\S]*?</gallery>", "", s)
    s = re.sub("(.){{([^{}\n]*?\|[^{}\n]*?)}}", "\\1[[\\2]]", s)
    s = filter_wiki(s)
    s = re.sub("\* *\n|'{2,}", "", s)
    s = re.sub("\n+", "\n", s)
    s = re.sub("\n[:;]|\n +", "\n", s)
    # s = re.sub('\n==', '\n\n==', s)
    return s


def wiki_replace2(s):
    # https://spaces.ac.cn/archives/4176
    s = re.sub(":*{\|[\s\S]*?\|}", "", s)
    s = re.sub("<gallery>[\s\S]*?</gallery>", "", s)
    s = re.sub("(.){{([^{}\n]*?\|[^{}\n]*?)}}", "\\1[[\\2]]", s)
    s = clean(s)
    s = re.sub("\* *\n|'{2,}", "", s)
    s = re.sub("\n+", "\n", s)
    s = re.sub("\n[:;]|\n +", "\n", s)
    # s = re.sub('\n==', '\n\n==', s)
    return s


def parse_wiki(wiki):
    title, text, pageid = wiki
    if not title or re.findall("^[a-zA-Z]+:", title) or re.findall("^#", text):
        return
    # doc = filter_wiki(text).strip()
    # sections=wtp.parse(text).get_sections()
    # doc = wtp.parse(text).plain_text().strip()
    # doc = clean(text).strip()
    sections = mwparserfromhell.parse(text, skip_style_tags=True).get_sections()
    # doc= mwparserfromhell.parse(text,skip_style_tags=True).strip_code().strip()
    doc1 = [str(x) for x in sections[: len(sections) - math.ceil(len(sections) / 10)]]
    # doc1 = doc.split('\n\n')
    # doc2=doc1[:len(doc1)-math.ceil(len(doc1)/10)]
    doc2 = [clean(s).strip() for s in doc1]
    doc3 = [x.strip() for x in doc2 if valid_line(x)]

    sent = "\n".join(doc3)
    if not sent or len(sent.encode("utf-8")) < 100:
        return
    page = {"title": title, "text": sent}
    return page


def extract(src, out_file, compress_type="", mp=0):
    logger.info(f"extract {src}")
    # input = subprocess.Popen(
    #     f"bzcat  {src}", shell=True, stdout=subprocess.PIPE, encoding='utf-8', errors='ignore').stdout
    input = readStream(src)
    wikis = extract_pages(input)

    if out_file == "-":
        output = sys.stdout
    else:
        if not compress_type:
            output = open(out_file, "w")
        elif compress_type == "bz2":
            output = bz2.BZ2File(out_file, "w")
        elif compress_type == "gz":
            output = gzip.GzipFile(out_file, "w")
        elif compress_type == "xz":
            output = lzma.open(out_file, "w")
        else:
            raise ValueError("invalid compress_type " + compress_type)

    n = 0
    # pool = multiprocessing.Pool(max(1, os.cpu_count()-1))
    if mp > 0:
        pool = multiprocessing.Pool()
        end = False
        batch = []
        for i in range(10**10):
            try:
                d = next(wikis)
                batch.append(d)
            except:
                end = True
            if end or len(batch) >= 10000:
                re = pool.imap_unordered(parse_wiki, batch)
                for page in re:
                    if page:
                        line = json.dumps(page, ensure_ascii=False) + "\n"
                        if compress_type:
                            line = line.encode("utf-8", errors="ignore")
                        output.write(line)
                        n += 1
                batch = []
                logger.info(f"{i}--> {out_file} {n}")
    else:
        for i, d in enumerate(wikis):
            page = parse_wiki(d)
            if page:
                line = json.dumps(page, ensure_ascii=False) + "\n"
                if compress_type:
                    line = line.encode("utf-8", errors="ignore")
                output.write(line)
                n += 1
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

