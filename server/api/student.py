from flask import Blueprint
from flask import jsonify, request, session
from flasgger import swag_from

from server import conn

student_blueprint = Blueprint('student_blueprint', __name__)


@student_blueprint.route('/student', methods=['GET'])
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


@student_blueprint.route('/student/resume/upload', methods=['POST'])
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


@student_blueprint.route('/student/resume/', methods=['GET'])
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


@student_blueprint.route('/student/resume/status', methods=['GET'])
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
