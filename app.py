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
            username_col = "email"

        query = "select count(*) from {} where {} = %s and password = %s"\
                .format(table, username_col)

        res = list(conn.execute(query, (username, password, )).first())
        if (res[0] == 1):
            status = "true"
            data = ""

            if(user_type == 2):
                query = """
                        select id 
                        from company
                        where email = %s
                        """
                res = list(conn.execute(query,(username,) ).first())

                session['username'] = res[0]
                session['user_type'] = user_type

            else:
                session['username'] = username
                session['user_type'] = user_type

        else:
            status = "false"
            data = "Error: Invalid credentials"

    return jsonify({
        'data': data,
        'status': status
    })


@app.route('/logout', methods=['GET'])
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


@app.route('/student', methods=['GET'])
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


@app.route('/student/resume/', methods=['GET'])
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
                    'resume_file': str(res[0])
                }

        except:
            data = "Database error"
            status = "false"

    return jsonify({
        'data': data,
        'status': status
    })


@app.route('/student/resume/status', methods=['GET'])
@swag_from('docs/student_resume_status.yml')
def resume_status():
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

        try:
            # check if resume exists
            query = """
                select count(*)
                from resume
                where rollno = %s
                """
            res = list(conn.execute(query, (rollno, )).first())
            if (res[0] == 0):
                data = "no resume"
                status = "false"
            else:
                query = """
                    select verified_ic
                    from resume
                    where rollno = %s
                    """
                res = list(conn.execute(query, (rollno, )).first())
                if res[0] is None:
                    # not verified
                    data = {
                        'is_verified': "false",
                        'verified_ic': ""
                    }
                else:
                    verified_ic = int(res[0])
                    query = """
                        select name
                        from ic, student
                        where ic.id = %s::smallint
                            and ic.rollno = student.rollno
                        """
                    res = list(conn.execute(query, (verified_ic, )).first())
                    data = {
                        'is_verified': "true",
                        'verified_ic': res[0]
                    }
                status = "true"
        except:
            status = "false"
            data = "database error"

    return jsonify({
        'data': data,
        'status': status
    })


@app.route('/company/', methods=['GET'])
@swag_from('docs/company.yml')
def company():
    data = ""
    status = ""
    if 'username' not in session:
        # no user has logged in
        status = "false"
        data = "Invalid Session"
    elif session['user_type'] != 2:
        # logged in user is not a company
        status = "false"
        data = "User is not a company"
    else:
        company_id = session['username']
        try:
            query = """
                    select name,email
                    from company 
                    where id = %s
                    """
            res = list(conn.execute(query,(company_id, )).first())
            data = {
                'name':res[0],
                'email':res[1]
            }
            status = "true"
        except:
            data = "Database error"
            status = "false"
            
    return jsonify({
        'data': data,
        'status': status
    })


@app.route('/company/addjaf', methods=['POST'])
@swag_from('docs/company_add_jaf.yml')
def add_jaf():
    data = ""
    status = ""
    if 'username' not in session:
        # no user has logged in
        status = "false"
        data = "Invalid Session"
    elif session['user_type'] != 2:
        # logged in user is not a company
        status = "false"
        data = "User is not a company"
    else:
        company_id = session['username']
        request_data = request.get_json()

        jaf_no = int(request_data['jaf_no'])
        name = request_data['name']
        description = request_data['description']
        stipend = request_data['stipend']
        cpi_cutoff = request_data['cpi_cutoff']

        # check if jaf_no already exists
        try:
            query = """
                select count(*)
                from jaf
                where company_id = %s
                    and jaf_no = %s
                """
            res = list(conn.execute(query, (company_id, jaf_no, )).first())
            if (res[0] == 1):
                status = "false"
                data = "JAF already exists"
            else:
                query = """
                    insert into
                    jaf(company_id, jaf_no, name, description, stipend, cpi_cutoff)
                    values(%s, %s, %s, %s, %s, %s)
                    """
                conn.execute(query, (company_id, jaf_no, name, description, stipend, cpi_cutoff, ))
                status = "true"
                data = "successfully added new JAF"
        except:
            status = "false"
            data = "database error"
            
    return jsonify({
        'data': data,
        'status': status
    })


@app.route('/company/register', methods=['POST'])
@swag_from('docs/company_register.yml')
def company_register():
    data = ""
    status = ""

    request_data = request.get_json()
    company_name = request_data['name']
    company_email = request_data['email']
    company_password = request_data['password']

    try:
        query = """
                insert into company(name,email,password)
                values(%s,%s,%s)
                """
        conn.execute(query,(company_name,company_email,company_password))
        data = "Company registered"
        status = "true"
    except:
        data = "Company Email already used"
        status = "false"

    return jsonify({
        'data': data,
        'status': status
    })


if __name__ == '__main__':
    app.run(threaded=True, host=URL, port=int(PORT))
