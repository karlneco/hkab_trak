#!/bin/sh
export FLASK_APP=main.py
flask db init
flask db migrate -m "initial db"
python -u main.py