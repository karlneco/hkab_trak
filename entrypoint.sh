#!/bin/sh
export FLASK_APP=main.py
flask db init
flask db migrate -m "initial db"
flask create-admin
python -u main.py