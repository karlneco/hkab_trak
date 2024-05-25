#!/bin/sh
export FLASK_APP=main.py
flask db init
flask db migrate -m "initial db"
flask db upgrade
sleep 5
flask create-admin
python -u main.py