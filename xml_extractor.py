import bz2
import lzma
import os
import pathlib
import sys
import time
from gensim.corpora.wikicorpus import extract_pages, filter_wiki
import collections
import re
import json
import multiprocessing
from tqdm import tqdm
import codecs
import subprocess
from html2text import html2text as htt
import wikitextparser as wtp
from logzero import logger
from threading import Thread
from multiprocessing import Queue, Process, cpu_count
import queue


def wiki_replace(s):
    # https://spaces.ac.cn/archives/4176
    s = re.sub(':*{\|[\s\S]*?\|}', '', s)
    s = re.sub('<gallery>[\s\S]*?</gallery>', '', s)
    s = re.sub('(.){{([^{}\n]*?\|[^{}\n]*?)}}', '\\1[[\\2]]', s)
    s = filter_wiki(s)
    s = re.sub('\* *\n|\'{2,}', '', s)
    s = re.sub('\n+', '\n', s)
    s = re.sub('\n[:;]|\n +', '\n', s)
    s = re.sub('\n==', '\n\n==', s)
    return s


ref_words = ['\n*', 'refer to:', 'See also']
ref_words = [x.lower() for x in ref_words]


def pure_section(x):
    x = x.strip()
    if x.endswith('=='):
        return ''
    for ref in ref_words:
        if ref in x[:32]:
            return ''
    lines = [l.strip() for l in x.splitlines()]
    doc = [x for x in lines if not x.startswith(
        'File:') and not x.startswith('* ')]
    doc = [x.strip() for x in doc if x]
    if sum(1 if x.startswith('==') else 0 for x in doc) == len(doc):
        return ''
    return ''.join(doc).strip()


def parse_text(text):
    """
    slim=0: keep all sections
    slim=1: remove igored_sections
    slim=2: keep first section
    slim=3: keep first paragraph
    """
    sections = wtp.parse(text).sections
    contents = [
        section.plain_text(
            replace_templates=False,
            replace_parser_functions=False,
            replace_parameters=True,
            replace_tags=True,
            replace_external_links=True,
            replace_wikilinks=True,
            unescape_html_entities=True,
            replace_bolds_and_italics=True,
            _is_root_node=False
        )
        for section in sections]
    spans = [wiki_replace(x) for x in contents]
    doc = [pure_section(x) for x in spans]
    return doc


def parse_wiki(wiki):
    title, text, pageid = wiki
    if not title or re.findall('^[a-zA-Z]+:', title) or re.findall(u'^#', text):
        return
    doc = parse_text(text)
    if not doc or sum(len(x) for x in doc) < 64:
        return
    page = {"title": title, "text": doc}
    line = json.dumps(page, ensure_ascii=False)+'\n'
    return line


def extract(src, out_file, compress_type=''):
    logger.info(f"extract {src}")
    pipe = subprocess.Popen(
        f"bzcat  {src}", stdout=subprocess.PIPE, encoding='utf-8', errors='ignore')
    wikis = extract_pages(pipe.stdout)

    if out_file == '-':
        output = sys.stdout
    else:
        if not compress_type:
            output = open(out_file, "w")
        elif compress_type == "bz2":
            output = bz2.BZ2File(out_file, 'w')
        elif compress_type == "xz":
            output = lzma.open(out_file, "w")
        else:
            raise ValueError("invalid compress_type "+compress_type)

    batch = []
    n = 0
    pool = multiprocessing.Pool(max(1, os.cpu_count()-1))
    for i, wiki in enumerate(wikis):
        batch.append(wiki)
        if len(batch) >= 1e5:
            re = pool.imap_unordered(parse_wiki, batch)
            for line in re:
                if line:
                    if compress_type:
                        line = line.encode('utf-8')
                    output.write(line)
                    n += 1
            batch = []
            logger.info(f"{i}--> {out_file} {n}")

    if len(batch) > 0:
        re = pool.imap_unordered(parse_wiki, batch)
        for line in re:
            if line:
                if compress_type:
                    line = line.encode('utf-8')
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

    extract("F:/data/wiki-xml-dumps/enwiki-20230101-pages-articles.xml.bz2",
            "F:/data/wiki-xml-json//enwiktionary-xml.json", compress_type=args.compress_type)
