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
            'rollno': rollno,
            'cpi': float(res[1]),
            'dept_name': res[2]
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


@student_blueprint.route('/student/jafs', methods=['GET'])
@swag_from('docs/student_jafs.yml')
def student_view_jafs():
    data = []
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
            query = """
                 select dept_id,cpi
                 from student
                 where rollno = %s
                 """
            res = list(conn.execute(query, (rollno, )).first())
            dept_id = int(res[0])
            cpi = float(res[1])

            query = """
                    select
                        company.name,
                        jaf_no,
                        jaf.name,
                        description,
                        stipend,
                        cpi_cutoff,
                        company.id
                    from jaf natural join eligibility
                            join company on company_id = company.id
                    where dept_id =%s
                        and cpi_cutoff <= %s;
                    """
            res = conn.execute(query, (dept_id, cpi))
            for row in res:
                sub_query = """
                    select count(*)
                    from signedjafs
                    where rollno = %s
                        and company_id = %s
                        and jaf_no = %s
                    """
                res2 = list(conn.execute(sub_query, (rollno, int(row[6]), int(row[1]))).first())
                is_signedup = False if res2[0] == 0 else True
                data.append({
                        'company_name': row[0],
                        'jaf_no': row[1],
                        'jaf_name': row[2],
                        'description': row[3],
                        'stipend': row[4],
                        'cpi_cutoff': float(row[5]),
                        'signedup': is_signedup,
                        'company_id': int(row[6])
                    })
            status = "true"

        except Exception as e:
            data = str(e)
            status = "false"

    return jsonify({
        'data': data,
        'status': status
    })


@student_blueprint.route('/student/sign_jaf', methods=['POST'])
@swag_from('docs/student_sign_jaf.yml')
def student_sign_jaf():
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
            request_data = request.get_json()
            company_id = request_data['company_id']
            jaf_no = request_data['jaf_no']

            query = """
                    select count(*)
                    from signedjafs
                    where company_id = %s
                        and jaf_no = %s
                        and rollno = %s
                    """
            res = list(conn.execute(query, (company_id, jaf_no, rollno)).first())
            if res[0] == 0:

                # now check if JAF exists
                query = """
                    select count(*)
                    from jaf
                    where company_id = %s and jaf_no = %s
                    """
                res = list(conn.execute(query, (company_id, jaf_no)).first())
                if (res[0] == 1):
                    query = """
                        insert into
                        signedjafs(rollno, company_id, jaf_no)
                        values(%s, %s, %s)
                        """
                    conn.execute(query, (rollno, company_id, jaf_no))
                    data = "JAF Signed"
                    status = "true"
                else:
                    data = "JAF does not exist"
                    status = "false"
            else:
                data = "JAF already signed"
                status = "false"

        except Exception as e:
            data = str(e)
            status = "false"

    return jsonify({
        'data': data,
        'status': status
    })


@student_blueprint.route('/student/signout_jaf', methods=['POST'])
@swag_from('docs/student_signout_jaf.yml')
def student_signout_jaf():
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
            request_data = request.get_json()
            company_id = request_data['company_id']
            jaf_no = request_data['jaf_no']

            query = """
                    select count(*)
                    from signedjafs
                    where company_id = %s
                        and jaf_no = %s
                        and rollno = %s
                    """
            res = list(conn.execute(query, (company_id, jaf_no, rollno)).first())
            if res[0] == 1:
                # delete from signedjafs
                query = """
                    delete
                    from signedjafs
                    where rollno = %s and
                        company_id = %s and
                        jaf_no = %s
                    """
                conn.execute(query, (rollno, company_id, jaf_no))
                data = "JAF unsigned"
                status = "true"
            else:
                data = "JAF not signed"
                status = "false"

        except Exception as e:
            data = str(e)
            status = "false"

    return jsonify({
        'data': data,
        'status': status
    })


@student_blueprint.route('/student/jaf', methods=['POST'])
@swag_from('docs/student_view_jaf.yml')
def student_view_jaf():
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
            request_data = request.get_json()
            jaf_no = int(request_data['jaf_no'])
            company_id = int(request_data['company_id'])

            query = """
                select count(*)
                from jaf
                where company_id = %s and jaf_no = %s
                """
            res = list(conn.execute(query, (company_id, jaf_no)))
            if (res[0][0] == 1):
                query = """
                    select
                        jaf_no,
                        jaf.name,
                        description,
                        stipend,
                        cpi_cutoff,
                        company.name
                    from jaf, company
                    where jaf.company_id = company.id
                        and company_id = %s and jaf_no = %s
                    """
                res = list(conn.execute(query, (company_id, jaf_no)).first())
                eligible_departments = []
                sub_query = """
                    select id, name
                    from eligibility join department on dept_id = id
                    where company_id = %s
                        and jaf_no = %s
                    """
                sub_res = conn.execute(sub_query, (company_id, jaf_no))
                for dept in sub_res:
                    eligible_departments.append({
                            'dept_id': int(dept[0]),
                            'name': dept[1]
                        })

                sub_query = """
                    select count(*)
                    from signedjafs
                    where rollno = %s
                        and company_id = %s
                        and jaf_no = %s
                    """
                res2 = list(conn.execute(sub_query, (rollno, company_id, jaf_no)).first())
                is_signedup = False if res2[0] == 0 else True

                data = {
                    'jaf_no': jaf_no,
                    'jaf_name': res[1],
                    'description': res[2],
                    'stipend': res[3],
                    'cpi_cutoff': float(res[4]),
                    'company_id': company_id,
                    'company_name': res[5],
                    'signedup': is_signedup,
                    'eligible_departments': eligible_departments
                }

                status = "true"
            else:
                status = "false"
                data = "JAF does not exists"
        except Exception as e:
            status = "false"
            data = str(e)

    return jsonify({
        'data': data,
        'status': status
    })
