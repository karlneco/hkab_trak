## Hoshuko Absence Tracker

This application will allow parents to register their students absences

### Configuration
To get this to run correctly, we need a `prod.conf` file in the `instance` folder. This is where our 
database will live as well.

#### **`prod.conf`**
```python
import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = 'your_awesome_password'
DEBUG = True

SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(BASEDIR,'data.sqlite')
SQLALCHEMY_TRACK_MODIFICATIONS = True

RECAPTCHA_SITE_KEY="your_site_key"
RECAPTCHA_SECRET_KEY="your_secret_key"
RECAPTCHA_ENABLED=True
```

### DB Setup

Initialize the database with:
`flask db init`

create the SQLite file with:
`flask db migrate -m "initial db"`

If you upgrade the model, update the db with:
`flask db upgrade`

