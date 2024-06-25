
import os
import json
import re
import sqlite3
import logging
import random

from typing import List, Dict, Tuple
from pydantic import BaseModel
from enum import Enum
from typing import List
from copy import deepcopy

def init_logger():
    logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

# PRJ_BASE = os.path.dirname(os.getcwd())
PRJ_BASE = os.getcwd()
PRJ_BASE = os.path.abspath(__file__).replace('core/rhyme/utils.py','')
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
        tat_ca_phu_am += [phu_am.capitalize() for phu_am in tat_ca_phu_am]
        tat_ca_phu_am = [self.handle_phu_am_and_skip_if_space(phu_am) for phu_am in tat_ca_phu_am]
        self.pattern_remove_phu_am = re.compile('|'.join(tat_ca_phu_am))
    
    @staticmethod
    def handle_van_trong_phu_am_and_add_space(van:str):
        """Xử lý logic cho phụ âm gi và qu. Với từ gia , quê thì vần lần ượt là a và ê thay vì ia và uê"""
        if van=='ia':
            return '(?<![Gg])' + van + '(?=\s|$)'
        elif van=='ue':
            return '(?<![Qq])' + van + '(?=\s|$)'
        elif van=='ua':
            return '(?<![Qq])' + van + '(?=\s|$)'
        return  van + '(?=\s|$)'
    
    @staticmethod
    def handle_phu_am_and_skip_if_space(phu_am:str):
        """xử lý logic cho các phụ âm, không lấy phụ âm nếu sau phụ âm là khoảng trắng"""
        if phu_am == 'gi':
            return '((^|\s)' + phu_am + '(?![ê\s]))'
        if phu_am == 'qu':
            return '((^|\s)' + phu_am + '(?![ê\s]))'
        return '((^|\s)' + phu_am + '(?!\s))' 

    def bo_dau_va_chuyen_van(self, text):
        """loại bỏ dấu của từ hoặc đoạn sau đó đổi về vần chuẩn - xử lý đặc biệt cho que -> qoe ví dụ que sẽ vần với khoe, y và i đọc giống nhau nên mapping về i"""
        clean_text = text.lower().strip().replace("  "," ") + " " # buffer dấu cách để tìm vần ở cuối từ
        for char, ko_dau_char in self.mapping_dau.items():
            if char != ko_dau_char:
                clean_text = re.sub(char, ko_dau_char, clean_text)
        for char, special_char in self.mapping_special_char.items():
            if char != "y ":
                clean_text = re.sub(char, special_char, clean_text)
        clean_text = re.sub('\by\b', 'i', clean_text)
        return clean_text.strip()
    
    def lay_van_cua_tu_hoac_doan(self, cleaned_text):
        matches = " ".join(self.pattern_tim_van_khong_dau.findall(cleaned_text))
        logging.debug(f"Get van: {matches}, from word: {cleaned_text}")
        return matches.strip()
    
    def lay_van_dao_cua_tu_hoac_doan(self, cleaned_text):
        van_dao = self.pattern_tim_van_khong_dau.findall(cleaned_text)
        van_dao.reverse()
        matches = " ".join(van_dao)
        logging.debug(f"Get van dao: {matches}, from word: {cleaned_text}")
        return matches.strip()
    
    def clean_phu_am(self, cleaned_text):
        filtered_text = re.sub(self.pattern_remove_phu_am, ' ', cleaned_text)
        return filtered_text.strip()

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

class Thanh(Enum):
    SAC = 'sắc'
    HOI = 'hỏi'
    NGA = 'ngã'
    NANG = 'nặng'
    HUYEN = 'huyền'
    NGANG = 'ngang'
    
class Tu(BaseModel):
    phu_am: str
    van: str
    thanh: Thanh
    
class TuHanlder(BaseModel):
    mapping_van_dau: dict
    bien_the_thanh: dict = {
        Thanh.NGA: [Thanh.HOI], 
        Thanh.HOI: [Thanh.NGA]
        }
    bien_the_van: dict = {
        "ac":["ăc", "at"],
        "au":["ao"],
        "ao":["au"],
        "ăc":["ac", "ăt"],
        "at":["ac","ăt"],
        "ăt":["ăc","at"],
        "êt":["êc"],
        "êc":["êt"],
        "ât":["âc"],
        "an":["ang"],
        "ang":["an"],
        
    }
    bien_the_phu_am: dict = {
        "gi":["d","v"],
        "d":["gi","v"],
        "v":["d","gi"],
        "k":["c"],
        "c":["k"],
        "s":["x"],
        "x":["s"],
        "ch":["tr"],
        "tr":["ch"]
    }
    mapping_thanh_cua_van: dict = None
    def __init__(self, **data):
        super().__init__(**data)
        self.mapping_thanh_cua_van = {}
        for van_thanh, van in self.mapping_van_dau.items():
            _,thanh = van_thanh.split()
            self.mapping_thanh_cua_van[van] = Thanh(thanh)
            
    def render_tu(self, tu: Tu):
        van_va_dau = self.mapping_van_dau.get(f"{tu.van} {tu.thanh.value}",'')
        if van_va_dau:
            if (tu.van[0] == 'i' and tu.phu_am == 'gi') or (tu.van[0] == 'u' and tu.phu_am == 'qu'):
                return tu.phu_am[0] + tu.van
            return tu.phu_am + van_va_dau
        return ""
    
    def render_tu_list(self, tu_list: List[Tu]):
        return " ".join([self.render_tu(tu) for tu in tu_list])
    
    def render_bien_the(self, tu_list: List[Tu]):
        bien_the_text = []
        for idx in range(len(tu_list)):
            for van in self.bien_the_van.get(tu_list[idx].van,[]):
                bien_the = deepcopy(tu_list)
                bien_the[idx].van = van
                bien_the_text.append(self.render_tu_list(bien_the))
            for thanh in self.bien_the_thanh.get(tu_list[idx].thanh,[]):
                bien_the = deepcopy(tu_list)
                bien_the[idx].thanh = thanh
                bien_the_text.append(self.render_tu_list(bien_the))
            for phu_am in self.bien_the_phu_am.get(tu_list[idx].phu_am,[]):
                bien_the = deepcopy(tu_list)
                bien_the[idx].phu_am = phu_am
                bien_the_text.append(self.render_tu_list(bien_the))
        return bien_the_text
    
    def render_tu_lai(self, tu_list: List[Tu]):
        tu_lai_tieu_chuan = []
        tu_lai_tu_do = []
        exclude = set()
        exclude.add(self.render_tu_list(tu_list))
        exclude.add(self.render_tu_list([tu_list[-1]] + tu_list[1:-1] + [tu_list[0]]))
        if len(tu_list) > 1:
            for i in range(6):
                tu_list[0].phu_am, tu_list[-1].phu_am = tu_list[-1].phu_am, tu_list[0].phu_am
                if i % 2 == 1:
                    tu_list[0].van, tu_list[-1].van = tu_list[-1].van, tu_list[0].van
                if i % 4 == 3:
                    tu_list[0].thanh, tu_list[-1].thanh = tu_list[-1].thanh, tu_list[0].thanh
                tu_lai_tieu_chuan.append(self.render_tu_list(tu_list))
                tu_lai_tu_do.extend(self.render_bien_the(tu_list))
        set_tu_lai_tieu_chuan = set([tu_lai for tu_lai in tu_lai_tieu_chuan if tu_lai != ""])
        set_tu_lai_tieu_chuan.difference_update(exclude)
        return list(set_tu_lai_tieu_chuan), list(set(tu_lai_tu_do))
    
    def parse_tu(self, tu_str: str, vn_grammar_handler: GrammarHandler) -> List[Tu]:
        lower_text = tu_str.lower()
        cleaned_tu = vn_grammar_handler.bo_dau_va_chuyen_van(lower_text)
        list_tu = []
        if vn_grammar_handler.clean_phu_am(cleaned_tu) == vn_grammar_handler.lay_van_cua_tu_hoac_doan(cleaned_tu):

            for raw_tu in lower_text.split():
                if raw_tu:
                    van = vn_grammar_handler.clean_phu_am(raw_tu)
                    phu_am = raw_tu.replace(van,'')
                    thanh = self.mapping_thanh_cua_van.get(van)
                    list_tu.append(
                        Tu(
                            phu_am=phu_am,
                            van = self.mapping_van_dau.get(f"{van} {Thanh.NGANG.value}"),
                            thanh = thanh
                        )
                    )
        return list_tu
    
    def render_bien_the_van_indexing(self, match_van: str) -> List[str]:
        vans = match_van.split()
        final_vans = [vans[0]] + self.bien_the_van.get(vans[0],[])
        for i in range(1,len(vans)):
            tmp_vans = []
            for current_van in final_vans:
                for next_van in [vans[i]] + self.bien_the_van.get(vans[i],[]):
                    tmp_vans.append(current_van + ' ' + next_van)
            final_vans = tmp_vans
        return final_vans


with open(os.path.join(PRJ_BASE,'app_metadata/am_tieng_viet.json'), 'r') as loaded_json_str:
    vietnamese_grammar = json.loads(loaded_json_str.read())
vn_grammar_handler = GrammarHandler(
    nguyen_am = vietnamese_grammar['nguyên âm'],
    phu_am = vietnamese_grammar['phụ âm'],
    phu_am_ghep = vietnamese_grammar['phụ âm ghép'],
    van_don = vietnamese_grammar['vần đơn'],
    van_tron = vietnamese_grammar['vần trơn'],
    van_can = vietnamese_grammar['vần cản'],
    mapping_dau = vietnamese_grammar['mapping dấu'],
    mapping_special_char = vietnamese_grammar["mapping âm tiết đặc biệt"]
)
db_handler = DbHanlder()

tu_handler = TuHanlder(
    mapping_van_dau=vietnamese_grammar['mapping vần và thanh']
)


class FunnySentenceHandler(BaseModel):
    idioms: List[str] = []
    punchlines: List[str] = []
    def get_sentence(self):
        return random.choice(self.idioms)
    
with open(os.path.join(PRJ_BASE,'app_metadata/idioms.txt'), 'r') as file:
    lines = file.readlines()
    lines = set([line.strip() for line in lines])
    lines.remove("")
    idioms = list(lines)
    
funny_sentence_handler = FunnySentenceHandler(
    idioms = idioms,
    punchlines = [],
)
