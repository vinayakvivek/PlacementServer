# API for Placement App

### Running the server
- clone the repo
- go to the project directory
- create a virtualenv with python2: `virtualenv -p python2 venv`
- acticate virtualenv: `source venv/bin/activate`
- install requirements: `pip install -r requirements`
- create a file named `local.py` in the project root, and copy contents of `config.py` to it
    - make changes if required, like `POSTGRES`, `URL`
    - `local.py` should look like this:
      ```python
      import os

      BASE_DIR = os.path.abspath(os.path.dirname(__file__))
      URL = '<HOST_URL>'
      PORT = <HOST_PORT>
      POSTGRES = {
          'user': '<postgres_username>',
          'pw': '<postgres_password>',
          'db': '<database_name>',
          'host': '<database_host_url>',
          'port': '<database_port>',
      }

      DEBUG = True
      SECRET_KEY = "<some_secret_key>"
      SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://%(user)s:\
      %(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES

      SQLALCHEMY_TRACK_MODIFICATIONS = False
      ```
- run `python run.py`
