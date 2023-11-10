import pandas as pd
import subprocess
import logging
import re
import json
from typing import Dict
import os
import sys
PRJ_BASE = os.path.dirname(os.getcwd())
sys.path.append(PRJ_BASE)

with open(os.path.join(PRJ_BASE,'app_metadata/am_tieng_viet.json')) as file:
    vietnamese_grammar = json.load(file)

def init_logger():
    logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

def clean_mark(text):
    clean_text = text
    for char in vietnamese_grammar['mapping dấu']:
        if char != vietnamese_grammar['mapping dấu'][char]:
            clean_text = clean_text.replace(char,vietnamese_grammar['mapping dấu'][char])
    return clean_text 

def contains_only_vietnamese_letters_and_spaces(text, 
        suffixes = vietnamese_grammar['vần đơn'] + vietnamese_grammar['vần trơn'] + vietnamese_grammar['vần cản'],
        pattern = re.compile(r'^[A-Za-zÀ-ỹ\s]+$')
    ):
    clean_text = clean_mark(text)
    if not bool(pattern.match(clean_text)):
        return False
    # Check if my_str ends with any of the suffixes
    if not any(clean_text.endswith(suffix) for suffix in suffixes):
        return False
    if any(char in clean_text for char in ['f','w','z','F','W','Z']):
        return False
    return True

def clean_upper_case(words:Dict[str, int]):
    del_list = set()
    for w_idx,(word,count) in enumerate(words.items()):
        if w_idx %10000 == 0:
            logging.info(f'  - processed {w_idx} words')
        word_lower = word.lower()
        if word_lower not in words or word == word_lower:
            continue
        if " " not in word:
            words[word_lower] += count
            del_list.add(word)
        elif count < words[word_lower]//2:
            words[word_lower] += count
            del_list.add(word)
    logging.info(f'  - processed {w_idx} words')      
    result_words = {}
    for key,value in words.items():
        if key not in del_list:
            result_words[key] = value    
    
    return result_words

def clean_words_dict(words:Dict[str, int]):
    new_words = words
    word_keys = list(new_words.keys())

    for word in word_keys:
        if not contains_only_vietnamese_letters_and_spaces(word):
            del new_words[word]

    return clean_upper_case(new_words)