
import os
import json
import re
import sqlite3

# PRJ_BASE = os.path.dirname(os.getcwd())
PRJ_BASE = os.getcwd()
print(PRJ_BASE)
with open(os.path.join(PRJ_BASE,'app_metadata/am_tieng_viet.json')) as file:
    vietnamese_grammar = json.load(file)
    
tat_ca_van = sorted(vietnamese_grammar['vần đơn'] + vietnamese_grammar['vần trơn'] + vietnamese_grammar['vần cản'], key=lambda x:len(x), reverse=True)
pattern = re.compile('|'.join(tat_ca_van))

def clean_mark(text):
    clean_text = text
    for char in vietnamese_grammar['mapping dấu']:
        if char != vietnamese_grammar['mapping dấu'][char]:
            clean_text = clean_text.replace(char,vietnamese_grammar['mapping dấu'][char])
    return clean_text 

def extract_van(word):
    matches = " ".join(pattern.findall(clean_mark(word)))
    return matches

def extract_van_dao(word):
    matches = " ".join(pattern.findall(clean_mark(word))[::-1])
    return matches

class DbHanlder:
    def __init__(self):
        self.conn = sqlite3.connect(os.path.join(PRJ_BASE,'app_metadata/example.db'))
        self.db_cursor = self.conn.cursor()
    def find_van_from_db(self, van:str):    
        self.db_cursor.execute(f"SELECT words FROM van_indexing WHERE id = '{van}'")
        row = self.db_cursor.fetchone()
        if row:
            return row[0]
        else:
            return None
