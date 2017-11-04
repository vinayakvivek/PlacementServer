from flask import Flask, jsonify, request, session
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, MetaData
from flasgger import Swagger
from flasgger import swag_from
from local import URL, PORT, SQLALCHEMY_DATABASE_URI


app = Flask(__name__)
app.config.from_pyfile('local.py')

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


@app.route('/')
def hello():
    return str(db.engine.execute('select * from department').first())


@app.route('/login', methods=['POST'])
@swag_from('docs/login.yml')
def login():
    data = ""
    status = ""

    request_data = request.get_json()

    if 'username' not in request_data:
        data = "no username"
    elif 'password' not in request_data:
        data = "no password"
    elif 'type' not in request_data:
        data = "no type"
    else:
        username = request_data['username']
        password = request_data['password']
        user_type = int(request_data['type'])

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

        query = "select count(*) from {} where {} = %s and password = %s"\
                .format(table, username_col)

        res = list(conn.execute(query, (username, password, )).first())
        if (res[0] == 1):
            status = "true"
            data = ""
            session['username'] = username
        else:
            status = "false"
            data = "Error: Invalid credentials"

    return jsonify({
        'data': data,
        'status': status
    })


@app.route('/student', methods=['POST'])
@swag_from('docs/student.yml')
def student():
    data = ""
    status = ""
    if 'username' not in session:
        status = "false"
        data = "Invalid Session"
    else:
        username = session['username']
        data = username
        status = "true"

    return jsonify({
        'data': data,
        'status': status
    })


if __name__ == '__main__':
    app.run(threaded=True, host=URL, port=int(PORT))
