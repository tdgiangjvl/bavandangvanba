from core.utils import (
    vn_grammar_handler,
    db_handler,
    logger)

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

@app.get("/")
async def homepage():
    return FileResponse("static/index.html")
@app.get("/tim_van/{words}")
async def tim_van(words: str = None, n_received: int = 0, n_request: int = 20):
    if words:
        result:str = db_handler.find_van_from_db(vn_grammar_handler.lay_van_cua_tu_hoac_doan(words))
        if result:
            result = result.split('\n')
            if n_received >= len(result):
                n_received = max(0,len(result) - n_request)
            return {"status":"success", "van": "\n".join(result[n_received: n_received + n_request])}
    return {"status":"fail"}

@app.get("/tim_van_dao/{words}")
async def tim_van_dao(words: str = None, n_received: int = 0, n_request: int = 20):
    if words:
        result:str = db_handler.find_van_from_db(vn_grammar_handler.lay_van_dao_cua_tu_hoac_doan(words))
        if result:
            result = result.split('\n')
            if n_received >= len(result):
                n_received = max(0,len(result) - n_request)
            return {"status":"success", "van": "\n".join(result[n_received: n_received + n_request])}
    return {"status":"fail"}

@app.get("/tim_tu_lai/{words}")
async def tim_van_dao(words: str = None):
    if True:
        return {"status":"success", 
            "tieu_chuan": "\n".join(["bác cạn","các bạn", "cán bạc"]),
            "tu_do": "\n".join(["bắc cạn","cắt bạn"])}
    else:
        return {"status":"fail"}