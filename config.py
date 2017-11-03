import os


basedir = os.path.abspath(os.path.dirname(__file__))
URL = '192.168.0.108'
PORT = '5000'
POSTGRES = {
    'user': 'rajat',
    'pw': '',
    'db': 'db_project',
    'host': 'localhost',
    'port': '5370',
}

DEBUG = True
SECRET_KEY = "RGEUWGREWY"
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://%(user)s:\
%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES

SQLALCHEMY_TRACK_MODIFICATIONS = False
