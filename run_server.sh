conda activate vuatiengviet_env
nohup uvicorn main:app --port 8501 --reload --log-config unicorn_log_config.py > fast_api_timvan.log &