from core.utils import (
    clean_mark, 
    extract_van, 
    extract_van_dao,
    DbHanlder)

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db_handler = DbHanlder()

@app.get("/")
async def homepage():
    return FileResponse("static/index.html")
@app.get("/tim_van/{words}")
async def tim_van(words: str = None, n_received: int = 0, n_request: int = 20):
    if words:
        result:str = db_handler.find_van_from_db(extract_van(words)).split('\n')
        if result:
            if n_received >= len(result):
                n_received = max(0,len(result) - n_request)
            return {"status":"success", "van": "\n".join(result[n_received: n_received + n_request])}
    return {"status":"fail"}

@app.get("/tim_van_dao/{words}")
async def tim_van_dao(words: str = None, n_received: int = 0, n_request: int = 20):
    if words:
        result:str = db_handler.find_van_from_db(extract_van_dao(words)).split('\n')
        if result:
            if n_received >= len(result):
                n_received = max(0,len(result) - n_request)
            return {"status":"success", "van": "\n".join(result[n_received: n_received + n_request])}
    return {"status":"fail"}