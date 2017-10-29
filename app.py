from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, MetaData, Table
import os


app = Flask(__name__)
# app.config.from_object(os.environ['APP_SETTINGS'])


POSTGRES = {
    'user': 'rajat',
    'pw': '',
    'db': 'db_project',
    'host': 'localhost',
    'port': '5370',
}

app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:\
%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
db.init_app(app)


engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], convert_unicode=True)
metadata = MetaData(bind=engine)

department = Table('department',metadata, autoload=True)
student = Table('student',metadata, autoload=True)
  
con = engine.connect()
print(engine.execute('select * from department').first())

@app.route('/')
def hello():
    return "Hello World!"


@app.route('/<name>')
def hello_name(name):
    return "Hello {}!".format(name)


if __name__ == '__main__':
    app.run()