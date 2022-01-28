alphabet=''.join( chr(x) for x in range(ord('a'),ord('z')+1) )
langs=[ a+b for a in alphabet for b in alphabet  ]
print(langs)

from logzero import logger
import os
def parse_lang(lang):
    cmd=f" python lang_wiki2txt.py --lang {lang} "
    os.system(cmd)
    return cmd

import multiprocessing
with multiprocessing.Pool(4) as pool:
    re=pool.imap_unordered(parse_lang,langs[:4])
    for i,x in enumerate(re):
        logger.info(f" langs:{i} {x} done")
