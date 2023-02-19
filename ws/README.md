#Run server (cmdline / no Docker)

#run ngrok (example)
ngrok http 5555 --subdomain=cognigy

#run api server
alias python=python3
python server_chat_connect.py
