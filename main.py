from core.utils import (
    clean_mark, 
    extract_van, 
    extract_van_dao,
    DbHanlder)

from fastapi import FastAPI

app = FastAPI()
db_handler = DbHanlder()

@app.get("/tim_van/{words}")
async def tim_van(words: str = None):
    if words:
        result = db_handler.find_van_from_db(extract_van(words))
        if result:
            return {"status":"success", "van": result}
    return {"status":"fail"}

@app.get("/tim_van_dao/{words}")
async def tim_van_dao(words: str = None):
    if words:
        result = db_handler.find_van_from_db(extract_van_dao(words))
        if result:
            return {"status":"success", "van": result}
    return {"status":"fail"}