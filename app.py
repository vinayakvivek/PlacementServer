from flask import Flask, jsonify, request
from flask.ext.sqlalchemy import SQLAlchemy
# from sqlalchemy import create_engine, MetaData, Table
from flasgger import Swagger
from flasgger import swag_from


app = Flask(__name__)
app.config.from_pyfile('config.py')

template = {
  "swagger": "2.0",
  "info": {
    "title": "PlacementAPI",
    "description": "API for Placement App",
    "contact": {
      "responsibleOrganization": "Gallants",
    },
    "version": "0.0.1"
  },
  "host": "localhost:5000",  # overrides localhost:5000
  "basePath": "/api",  # base bash for blueprint registration
  "schemes": [
    "http",
    "https"
  ],
  "operationId": "getmyData"
}
swagger = Swagger(app, template=template)

db = SQLAlchemy(app)
db.init_app(app)


@app.route('/')
def hello():
    return str(db.engine.execute('select * from department').first())


@app.route('/login', methods=['POST'])
@swag_from('docs/login.yml')
def login():
    return jsonify('YO')


if __name__ == '__main__':
    app.run()
