
import os
import json
import re
import sqlite3
import logging

from pydantic import BaseModel
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)

# PRJ_BASE = os.path.dirname(os.getcwd())
PRJ_BASE = os.getcwd()
PRJ_BASE = os.path.abspath(__file__).replace('core/utils.py','')
print(PRJ_BASE)

class GrammarHandler(BaseModel):
    nguyen_am: List[str] # nguyên âm
    phu_am: List[str] # phụ âm
    phu_am_ghep: List[str] # phụ âm ghép
    van_don: List[str] # vần đơn
    van_tron: List[str] # vần trơn
    van_can: List[str] # vần cản
    mapping_dau: Dict[str,str] # mapping dấu
    mapping_special_char: Dict[str,str]
    pattern_tim_van_khong_dau: re.Pattern = None # công thức regex để tìm vần không dấu
    pattern_remove_phu_am: re.Pattern = None # công thức regex để tìm vần không dấu
    def __init__(self, **data):
        super().__init__(**data)
        tat_ca_van = sorted(self.van_don + self.van_tron + self.van_can, key=lambda x:(-len(x),x))
        tat_ca_van = [self.handle_van_trong_phu_am_and_add_space(van) for van in tat_ca_van]
        self.pattern_tim_van_khong_dau = re.compile('|'.join(tat_ca_van))
        
        tat_ca_phu_am = sorted(self.phu_am + self.phu_am_ghep, key=lambda x:(-len(x),x))
        tat_ca_phu_am = [self.handle_phu_am_and_skip_if_space(phu_am) for phu_am in tat_ca_phu_am]
        self.pattern_remove_phu_am = re.compile('|'.join(tat_ca_phu_am))
    
    @staticmethod
    def handle_van_trong_phu_am_and_add_space(van:str):
        """Xử lý logic cho phụ âm gi và qu. Với từ gia , quê thì vần lần ượt là a và ê thay vì ia và uê"""
        if van=='ia':
            return '(?<![Gg])' + van + '(?=\s|$)'
        elif van=='uê':
            return '(?<![Qq])' + van + '(?=\s|$)'
        return  van + '(?=\s|$)'
    
    @staticmethod
    def handle_phu_am_and_skip_if_space(phu_am:str):
        """xử lý logic cho các phụ âm, không lấy phụ âm nếu sau phụ âm là khoảng trắng"""
        return phu_am + r'(?!\s)' 

    def bo_dau_va_chuyen_van(self, text):
        """loại bỏ dấu của từ hoặc đoạn sau đó đổi về vần chuẩn - xử lý đặc biệt cho que -> qoe ví dụ que sẽ vần với khoe, y và i đọc giống nhau nên mapping về i"""
        clean_text = text.lower() + " " # buffer dấu cách để tìm vần ở cuối từ
        for char, ko_dau_char in self.mapping_dau.items():
            if char != ko_dau_char:
                clean_text = re.sub(char, ko_dau_char, clean_text)
        for char, special_char in self.mapping_special_char.items():
            if char != "y ":
                clean_text = re.sub(char, special_char, clean_text)
        clean_text = re.sub('\by\b', 'i', clean_text)
        return clean_text.strip()
    
    def lay_van_cua_tu_hoac_doan(self, text):
        matches = " ".join(self.pattern_tim_van_khong_dau.findall(self.bo_dau_va_chuyen_van(text)))
        logger.info(f"Get van: {matches}, from word: {text}")
        print(f"Get van: {matches}, from word: {text}")
        return matches
    def lay_van_dao_cua_tu_hoac_doan(self, text):
        van_dao = self.pattern_tim_van_khong_dau.findall(self.bo_dau_va_chuyen_van(text))
        van_dao.reverse()
        matches = " ".join(van_dao)
        logger.info(f"Get van dao: {matches}, from word: {text}")
        print(f"Get van dao: {matches}, from word: {text}")
        return matches
    def clean_phu_am(self, text):
        filtered_text = re.sub(self.pattern_remove_phu_am, '', self.bo_dau_va_chuyen_van(text))
        return filtered_text

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
            return ""


with open(os.path.join(PRJ_BASE,'app_metadata/Vietnamese_Handler.json'), 'r') as infile:
    loaded_json_str = infile.read()
    
vn_grammar_handler = GrammarHandler.parse_raw(loaded_json_str)
db_handler = DbHanlder()

