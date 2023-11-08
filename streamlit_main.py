import streamlit as st
import os
import sys
import json
import subprocess
import sqlite3

def clean_mark(text):
    clean_text = text.lower()
    for char in vietnamese_grammar['mapping dấu']:
        if char != vietnamese_grammar['mapping dấu'][char]:
            clean_text = clean_text.replace(char,vietnamese_grammar['mapping dấu'][char])
    return clean_text 

@st.cache_data(show_spinner=False)
def load_file():
    with open(os.path.join(PRJ_BASE,'app_metadata/am_tieng_viet.json')) as file:
        vietnamese_grammar = json.load(file)
    return vietnamese_grammar

def find_van_from_db(van, cursor):
    
    cursor.execute(f"SELECT words FROM van_indexing WHERE id = '{van}'")

    # Fetch the first row returned by the SELECT statement
    row = cursor.fetchone()

    # Check if a row was returned
    if row:
        # Print the value associated with the primary key
        return row[0]
    else:
        return "Không có vần nào cả"

PRJ_BASE = os.getcwd()
sys.path.append(PRJ_BASE)

vietnamese_grammar = load_file()
conn = sqlite3.connect('app_metadata/example.db')
db_cursor = conn.cursor()
    
import re
tat_ca_van = sorted(vietnamese_grammar['vần đơn'] + vietnamese_grammar['vần trơn'] + vietnamese_grammar['vần cản'], key=lambda x:len(x), reverse=True)
pattern = re.compile('|'.join(tat_ca_van))

def search_van_indexing(word):
    matches = " ".join(pattern.findall(clean_mark(word)))
    return find_van_from_db(matches, db_cursor)
def search_van_dao_indexing(word):
    matches = " ".join(pattern.findall(clean_mark(word))[::-1])
    return find_van_from_db(matches, db_cursor)

text = st.text_input("Enter your text here: ")
col1, col2 = st.columns(2)
with col1:
    find_van = st.button("Tìm vần đơn/đôi/ba/má")
with col2:
    find_vandao = st.button("Tìm vần đảo")

if find_van and len(text) > 0:
    result = search_van_indexing(text)
    print(type(result))
    st.text(result)
if find_vandao and len(text) > 0:
    result = search_van_dao_indexing(text)
    print(type(result))
    st.text(result)