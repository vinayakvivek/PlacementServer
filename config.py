import os


basedir = os.path.abspath(os.path.dirname(__file__))
URL = 'localhost'
PORT = '5000'
POSTGRES = {
    'user': 'vinayakvivek',
    'pw': '',
    'db': 'db_project',
    'host': 'localhost',
    'port': '5432',
}

DEBUG = True
SECRET_KEY = "RGEUWGREWY"
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://%(user)s:\
%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES

SQLALCHEMY_TRACK_MODIFICATIONS = False
