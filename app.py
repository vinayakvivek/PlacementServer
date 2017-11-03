from flask import Flask, jsonify, request, session
from flask.ext.sqlalchemy import SQLAlchemy
# from sqlalchemy import create_engine, MetaData, Table
from flasgger import Swagger
from flasgger import swag_from
from config import URL, PORT

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


@app.route('/')
def hello():
    return str(db.engine.execute('select * from department').first())


@app.route('/login', methods=['POST'])
@swag_from('docs/login.yml')
def login():
    data = {
        'status': "",
        'data': ""
    }

    request_data = request.get_json()

    username = request_data['username']
    password = request_data['password']
    user_type = int(request_data['type'])

    if not username:
        data['data'] = "no username"
    elif not password:
        data['data'] = "no password"
    elif not type:
        data['data'] = "no type"
    else:
        table = ""
        username_col = ""
        if user_type == 0:
            # student
            table = "student"
            username_col = "rollno"
        elif user_type == 1:
            table = "ic"
            username_col = "id"
        elif user_type == 2:
            table = "company"
            username_col = "id"

        query = "select count(*) from %s where %s = '%s' and password = '%s'" %\
            (table, username_col, username, password)

        res = list(db.engine.execute(query).first())
        if (res[0] == 1):
            data['status'] = "true"
            data['data'] = ""
            session['username'] = username
        else:
            data['status'] = "false"
            data['data'] = "Error: Invalid credentials"

    return jsonify(data)


if __name__ == '__main__':
    app.run(threaded=True, host=URL, port=int(PORT))
