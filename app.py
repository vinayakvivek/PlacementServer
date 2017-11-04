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
    return jsonify({
        'data': "PlacementAPI: Invalid request",
        'status': "false"
    })


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
            session['user_type'] = user_type
        else:
            status = "false"
            data = "Error: Invalid credentials"

    return jsonify({
        'data': data,
        'status': status
    })


@app.route('/logout', methods=['POST'])
@swag_from('docs/logout.yml')
def logout():
    data = ""
    status = ""
    if 'username' not in session:
        status = "false"
        data = "Invalid Session"
    else:
        session.pop('username', None)
        session.pop('user_type', None)
        status = "true"
        data = ""

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
        # no user has logged in
        status = "false"
        data = "Invalid Session"
    elif session['user_type'] != 0:
        # logged in user is not a student
        status = "false"
        data = "User is not a student"
    else:
        rollno = session['username']
        query = """
            select S.name, S.cpi, D.name
            from student as S, department as D
            where S.rollno = %s and
                  S.dept_id = D.id
            """
        res = list(conn.execute(query, (rollno, )).first())
        data = {
            'name': res[0],
            'cpi': float(res[1]),
            'dept': res[2]
        }
        status = "true"

    return jsonify({
        'data': data,
        'status': status
    })


@app.route('/student/resume/upload', methods=['POST'])
@swag_from('docs/student_resume_upload.yml')
def resume_upload():
    data = ""
    status = ""
    if 'username' not in session:
        # no user has logged in
        status = "false"
        data = "Invalid Session"
    elif session['user_type'] != 0:
        # logged in user is not a student
        status = "false"
        data = "User is not a student"
    else:
        request_data = request.get_json()
        resume_file = bytes(request_data['resume_file'])

        rollno = session['username']

        try:
            query = """
                select count(*)
                from resume
                where rollno = %s
                """
            res = list(conn.execute(query, (rollno, )).first())
            if (res[0] == 0):
                # student has no existing resume
                query = """
                    insert into
                    resume(rollno, resume_file)
                    values(%s, %s)
                    """
                conn.execute(query, (rollno, resume_file))
                data = "successfully added resume"
            else:
                # resume already exists, so update it
                query = """
                    update resume
                    set resume_file = %s
                    where rollno = %s
                    """
                conn.execute(query, (resume_file, rollno, ))
                data = "successfully updated resume"

            status = "true"
        except:
            status = "false"
            data = "database error"
            
    return jsonify({
        'data': data,
        'status': status
    })

@app.route('/student/resume/', methods=['POST'])
@swag_from('docs/student_resume.yml')
def student_resume():
  data = ""
  status = ""
  if 'username' not in session:
        # no user has logged in
        status = "false"
        data = "Invalid Session"
  elif session['user_type'] != 0:
      # logged in user is not a student
      status = "false"
      data = "User is not a student"
  else:
      try:
          rollno = session['username']
          print(rollno)
          query = """
                select count(*)
                from resume where
                rollno = %s
                """
          res = list(conn.execute(query, (rollno, )).first())
          # print(res[0])
          if(res[0] == 0):
            status = "false"
            data = "No resume uploaded"

          else:
            query = """
                    select resume_file
                    from resume where
                    rollno = %s
                    """
            res = list(conn.execute(query, (rollno, )).first())
            status = "true"
            data = {
             'resume_file' : str(res[0])
             }

      except:
        data = "Database error"
        status = "false"

  return jsonify({
        'data': data,
        'status': status
    })

if __name__ == '__main__':
    app.run(threaded=True, host=URL, port=int(PORT))
