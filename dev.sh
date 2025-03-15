export FLASK_APP=main.py
export FLASK_ENV=development
export FLASK_DEBUG=1

if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

flask run --host 0.0.0.0 --port 3000
