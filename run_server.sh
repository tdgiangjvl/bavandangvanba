conda activate vuatiengviet_env_py311
nohup uvicorn main:app --port 8501 --reload > fast_api_timvan.log &