import pandas as pd
import subprocess
import logging
import re
import json
from typing import Dict
import os
import sys
    
from core.rhyme.utils import (
    vn_grammar_handler,
    init_logger)
init_logger()


def contains_only_vietnamese_letters_and_spaces(text):
    cleaned_text = vn_grammar_handler.bo_dau_va_chuyen_van(text)
    matches_01 = vn_grammar_handler.lay_van_cua_tu_hoac_doan(cleaned_text)
    matches_02 = vn_grammar_handler.clean_phu_am(cleaned_text)
    # Check if my_str ends with any of the suffixes
    if matches_01 != matches_02:
        return False
    return True

def clean_upper_case(words:Dict[str, int]):
    del_list = set()
    for w_idx,(word,count) in enumerate(words.items()):
        word_lower = word.lower()
        if word_lower not in words or word == word_lower:
            continue
        if " " not in word:
            words[word_lower] += count
            del_list.add(word)
        elif count < words[word_lower]//2:
            words[word_lower] += count
            del_list.add(word)    
    result_words = {}
    for key,value in words.items():
        if key not in del_list:
            result_words[key] = value    
    
    return result_words

def get_ngram_from_sentences(sentences, ngrams = [1,2,3,4]):
    n_gram_phrases = {}
    for st_idx,sentence in enumerate(sentences):
        for n_gram in [1,2,3,4]:
            for idx in range(len(sentence) - n_gram + 1):
                n_gram_phrase = ' '.join(sentence[idx:idx + n_gram])
                if len(n_gram_phrase.split()) > max(ngrams):
                    break
                if n_gram_phrase not in n_gram_phrases:
                    n_gram_phrases[n_gram_phrase] = 0
                n_gram_phrases[n_gram_phrase] += 1
    return n_gram_phrases

def clean_words_dict(words:Dict[str, int]):
    new_words = words
    word_keys = list(new_words.keys())

    for word in word_keys:
        if not contains_only_vietnamese_letters_and_spaces(word):
            del new_words[word]

    return clean_upper_case(new_words)
