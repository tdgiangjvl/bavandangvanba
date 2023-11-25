conda activate vuatiengviet_env
nohup uvicorn main:app --port 8501 --reload > fast_api_timvan.log &