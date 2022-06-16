#!/usr/bin/env python
# -*- coding: utf-8 -*-
import bz2
import lzma
import sys
import traceback
import glob
import subprocess
import json
import os
import requests
import re
import random
import time
import shutil
import argparse
import gzip

from logzero import logger

from extractor import extract_wiki


def parse_all(src_dir, tgt_dir, lang="*", compress_type="xz", same_language=False):
    srcs = glob.glob(rf"{src_dir}/{lang}*.gz")
    srcs = list(srcs)
    srcs.sort()
    for src in srcs:
        name = os.path.basename(src)
        t = name.rstrip(".json.gz")
        if t[:2] <= 'a ':
            continue
        tgt = f"{tgt_dir}/{t}.txt.{compress_type}"
        extract_wiki(src, tgt, compress_type, same_language)
        # break


if __name__ == '__main__':
    src_dir = "F:/data/wiki-20220606-cirrussearch-content-json-gz"
    tgt_dir = "F:/data/wiki-20220606-cirrussearch-content-txt-bz2"
    parse_all(src_dir, tgt_dir, compress_type="bz2", same_language=True)
