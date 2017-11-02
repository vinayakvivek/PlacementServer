import os


basedir = os.path.abspath(os.path.dirname(__file__))
POSTGRES = {
    'user': 'vinayakvivek',
    'pw': '',
    'db': 'db_project',
    'host': 'localhost',
    'port': '5432',
}

DEBUG = True
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://%(user)s:\
%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES

SQLALCHEMY_TRACK_MODIFICATIONS = False
