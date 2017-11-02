from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
# from sqlalchemy import create_engine, MetaData, Table


app = Flask(__name__)
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)
db.init_app(app)


@app.route('/')
def hello():
    return str(db.engine.execute('select * from department').first())


@app.route('/<name>')
def hello_name(name):
    return "Hello {}!".format(name)


if __name__ == '__main__':
    app.run()
