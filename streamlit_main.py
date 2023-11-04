import streamlit as st
import os
import sys
import json

def clean_mark(text):
    clean_text = text
    for char in vietnamese_grammar['mapping dấu']:
        if char != vietnamese_grammar['mapping dấu'][char]:
            clean_text = clean_text.replace(char,vietnamese_grammar['mapping dấu'][char])
    return clean_text 

@st.cache_data(show_spinner=False)
def load_file():
    with open(os.path.join(PRJ_BASE,'data/am_tieng_viet.json')) as file:
        vietnamese_grammar = json.load(file)

    with open(os.path.join(PRJ_BASE,"app_metadata/index_van.json"), "r") as json_file:
        van_indexed = json.load(json_file)
    return vietnamese_grammar, van_indexed

PRJ_BASE = os.getcwd()
sys.path.append(PRJ_BASE)

vietnamese_grammar, VAN_INDEXED = load_file()
    
import re
tat_ca_van = sorted(vietnamese_grammar['vần đơn'] + vietnamese_grammar['vần trơn'] + vietnamese_grammar['vần cản'], key=lambda x:len(x), reverse=True)
pattern = re.compile('|'.join(tat_ca_van))

def search_van_indexing(word):
    matches = " ".join(pattern.findall(clean_mark(word)))
    if matches not in VAN_INDEXED:
        return []
    return VAN_INDEXED[matches]
def search_van_dao_indexing(word):
    matches = " ".join(pattern.findall(clean_mark(word))[::-1])
    if matches not in VAN_INDEXED:
        return []
    return VAN_INDEXED[matches]

text = st.text_input("Enter your text here: ")
col1, col2 = st.columns(2)
with col1:
    find_van = st.button("Tìm vần đơn/đôi/ba/má")
with col2:
    find_vandao = st.button("Tìm vần đảo")

if find_van and len(text) > 0:
    result = search_van_indexing(text)
    st.write([x[0] for x in result])
if find_vandao and len(text) > 0:
    result = search_van_dao_indexing(text)
    st.write([x[0] for x in result])