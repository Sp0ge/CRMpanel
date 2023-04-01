pip install -r requirements.txt --no-warn-script-location
set FLASK_APP=project
set FLASK_DEBUG=1
python3 -m flask db init
python3 -m flask db stamp head
python3 -m flask db migrate
python3 -m flask db upgrade
python3 -m flask run --port 443 --cert .\ssl\ssl_cert.crt --key .\ssl\ssl_key.key
