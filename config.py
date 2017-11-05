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