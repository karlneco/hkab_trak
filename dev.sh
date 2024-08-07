export FLASK_APP=main.py
export FLASK_ENV=development
export SECRET_KEY=your_secret_key_value
export MAIL_SERVER=***REMOVED***
export MAIL_PORT=465
export MAIL_USE_TLS=0
export MAIL_USE_SSL=True
export MAIL_USERNAME=***REMOVED***
export MAIL_PASSWORD=***REMOVED***
export MAIL_DEFAULT_SENDER=***REMOVED***
#these are v3 and don't seem to work
#export RECAPTCHA_PUBLIC_KEY=***REMOVED***
#export RECAPTCHA_PRIVATE_KEY=***REMOVED***
export RECAPTCHA_PUBLIC_KEY=***REMOVED***
export RECAPTCHA_PRIVATE_KEY=***REMOVED***
export RECAPTCHA_ENABLED=True

flask run --host 0.0.0.0 --port 3000