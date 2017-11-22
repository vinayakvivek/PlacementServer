from flask import Flask, jsonify
from flasgger import Swagger
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, MetaData
from local import URL, PORT, SQLALCHEMY_DATABASE_URI

app = Flask(__name__)
app.config.from_pyfile('../local.py')

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
  "host": URL + ':' + PORT,  # overrides localhost:5000
  "basePath": "/",  # base bash for blueprint registration
  "schemes": [
    "http",
    "https"
  ],
  "operationId": "getmyData"
}
swagger = Swagger(app, template=template)

db = SQLAlchemy(app)
db.init_app(app)

engine = create_engine(SQLALCHEMY_DATABASE_URI, convert_unicode=True)
metadata = MetaData(bind=engine)
conn = engine.connect()

from api.auth import auth_blueprint
from api.student import student_blueprint
from api.company import company_blueprint
from api.ic import ic_blueprint

app.register_blueprint(auth_blueprint)
app.register_blueprint(student_blueprint)
app.register_blueprint(company_blueprint)
app.register_blueprint(ic_blueprint)


@app.route('/')
def hello():
    return jsonify({
        'data': "Welcome to the PlacementAPI",
        'status': "true"
    })
