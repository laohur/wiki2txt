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

# section_names=collections.Counter()
igored_sections = set(['References', 'External links',
                       'See also', 'Further reading', 'Notes', 'Bibliography', 'Sources', 'Citations'])


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


def parse_text(text, slim=1):
    """
    slim=0: keep all sections
    slim=1: remove igored_sections
    slim=2: keep first section
    slim=3: keep first paragraph
    """
    sections = wtp.parse(text).sections
    # doc = [ section.plain_text() for section in sections]
    doc = []
    for section in sections:
        content = section.plain_text()
        if slim == 3:
            doc.append(content.strip().splitlines()[0])
            break
        if slim == 2:
            doc.append(content)
            break
        # '== See also ==\n\n* Anarchism by country\n* Governance without government\n* List of anarchist political ideologies\n* List of books about anarchism'
        # if ' ==\n\n* ' in content:
        #     break
        if slim == 1:
            if content.startswith('==') and content[3] != '=':
                s2 = content.split('==\n')[0].strip('=').strip()
                # if ',' in s2:
                #     continue
                # section_names[s2]+=1
                if s2 in igored_sections:
                    break
        doc.append(content)
    doc=[wiki_replace(x) for x in doc if x]
    doc=[x for x in doc if x]
    return doc


def extract(src, out_file, slim=1,compress_type='',quiet=False):
    logger.info(f"extract {src}")
    pipe = subprocess.Popen(
        f"bzcat  {src}", stdout=subprocess.PIPE, encoding='utf-8',errors='ignore')
    wiki = extract_pages(pipe.stdout)

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

    i = 0
    progress = tqdm()
    for d in wiki:
        title, text, pageid = d
        if not title or re.findall('^[a-zA-Z]+:', title) or re.findall(u'^#', text):
            continue
        # if title=='Alabama':
        #     d=0
        try:
            doc = parse_text(text, slim)
            if not doc:
                continue
            page = {"title": title, "doc": doc, "pageid": pageid}
            line = json.dumps(page, ensure_ascii=False)+'\n'
            if compress_type:
                line = line.encode('utf-8')
            output.write(line)
            i += 1
            if quiet:
                continue
            progress.update(1)
            if i % 100 == 0:
                progress.set_description(f'{src}已获取{i}篇文章')
        except Exception as e:
            logger.error(e)
            continue

            # print(section_names)
    # names=[(k,v) for k,v in section_names.items() ]
    # names.sort(key=lambda x:-x[1])
    # with open("section_names.txt",'w') as f:
    #    for k,v in names:
    #         f.write(f"{k}\t{v}\n")
    output.close()
    logger.info(f"extract {i} pages--> {out_file} ")
    if i==0:
        os.system(f"rm {out_file}")
    return (out_file, i)

# 导入多线程Thread,多进程的队列Queue,多进程Process，CPU核数cpu_count
# https://blog.51cto.com/u_15687734/5979101
# 存放分段读取的数据队列，注：maxsize控制队列的最大数量，避免一次性读取到内存中的数据量太大
data_queue = Queue(maxsize=cpu_count() * 2)
# 存放等待写入磁盘的数据队列
write_queue = Queue()


def read_data(src: pathlib.Path, data_queue: Queue, size: int = 10000):
    """
    读取数据放入队列的方法
    :return:
    """
    pipe = subprocess.Popen(
        f"bzcat  {src}", stdout=subprocess.PIPE, encoding='utf-8')
    wikis = extract_pages(pipe.stdout)
    for idx, df in enumerate(wikis):
        while data_queue.full():  # 如果队列满了，那就等待
            time.sleep(1)
        data_queue.put((idx + 1, df))
    data_queue.put((None, None))  # 放入结束信号


def write_data(out_file: pathlib.Path, write_queue: Queue, compress_type: str):
    """
    将数据增量写入CSV的方法
    :return:
    """
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

    while True:
        while write_queue.empty():
            time.sleep(1)
        idx, line = write_queue.get()
        if line is None:
            output.close()
            return  # 结束退出
        line += '\n'
        if compress_type:
            line = line.encode('utf-8')
        output.write(line)
        if idx % 100 == 0:
            logger.info(f'已获取{idx}篇文章')


def parse_data(data_queue: Queue, write_queue: Queue, slim: int = 1):
    """
    从队列中取出数据，并加工的方法
    :return:
    """
    while True:
        while write_queue.full() or data_queue.empty():
            time.sleep(1)
        idx, df = data_queue.get()
        if df is None:  # 如果是空的结束信号，则结束退出进程，
            # 特别注意结束前把结束信号放回队列，以便其他进程也能接收到结束信号！！！
            data_queue.put((idx, df))
            return
        """处理数据的业务逻辑略过"""
        title, text, pageid = df
        if not title or re.findall('^[a-zA-Z]+:', title) or re.findall(u'^#', text):
            continue
        # if title=='Alabama':
        #     d=0
        doc = parse_text(text,  slim)
        if not doc:
            continue
        # line=f"{title}\t{text}"
        page = {"title": title, "doc": doc}
        line = json.dumps(page, ensure_ascii=False)
        # line = '【' + title + u'】\n' + text.strip()+'\n\n'
        write_queue.put((idx, line))  # 将处理后的数据放入写队列


def extract_file(src, tgt, slim=1, compress_type=''):
    logger.info(f"extract {src}")
    # 创建一个读取数据的线程
    read_pool = Thread(target=read_data, args=(src, data_queue))
    read_pool.start()  # 开启读取线程

    # 创建一个增量写入CSV数据的线程
    write_pool = Thread(target=write_data, args=(
        tgt, write_queue, compress_type))
    write_pool.start()  # 开启写进程

    pools = []  # 存放解析进程的队列
    for i in range(cpu_count()-1):  # 循环开启多进程，不确定开多少个进程合适的情况下，那么按CPU的核数开比较合理
        pool = Process(target=parse_data, args=(
            data_queue, write_queue, slim))
        pool.start()  # 启动进程
        pools.append(pool)  # 加入队列
    for pool in pools:
        pool.join()  # 等待所有解析进程完成
    # 所有解析进程完成后，在写队列放入结束写线程的信号
    write_queue.put((None, None))
    write_pool.join()  # 等待写线程结束
    logger.info(f"extract --> {tgt} ")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", default="")
    parser.add_argument("--tgt", default="")
    parser.add_argument("--slim", type=int, default=1)
    parser.add_argument("--compress_type", type=str, default="")
    args = parser.parse_args()

    extract(args.src,args.tgt, slim=args.slim, compress_type=args.compress_type)
    # multiprocess
    # extract_file(args.src,args.tgt, slim=args.slim, compress_type=args.compress_type)
    