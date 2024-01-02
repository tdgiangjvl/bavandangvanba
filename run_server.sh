conda activate vuatiengviet_env
nohup uvicorn main:app --port 8501 --reload> fast_api_timvan.log &
# cd /root/vuatiengviet-ui
# pm2 start --name ui "yarn start"
# cd /root/vuatiengviet-cms
# pm2 start --name cms "yarn start"
# sudo service nginx restart