from flask import Blueprint
from flask import jsonify, request, session
from flasgger import swag_from

from server import conn

ic_blueprint = Blueprint('ic_blueprint', __name__)


@ic_blueprint.route('/ic', methods=['GET'])
@swag_from('docs/ic.yml')
def ic():
    data = ""
    status = ""
    if 'username' not in session:
        # no user has logged in
        status = "false"
        data = "Invalid Session"
    elif session['user_type'] != 1:
        # logged in user is not an IC
        status = "false"
        data = "User is not an IC"
    else:
        ic_id = int(session['username'])
        query = """
            select S.name, I.rollno
            from student as S, ic as I
            where S.rollno = I.rollno and
                    I.id = %s
            """
        res = list(conn.execute(query, (ic_id, )).first())
        data = {
            'name': res[0],
            'rollno': res[1],
            'id': ic_id,
        }
        status = "true"

    return jsonify({
        'data': data,
        'status': status
    })


@ic_blueprint.route('/ic/jafs/all', methods=['GET'])
@swag_from('docs/ic_view_all_jafs.yml')
def ic_view_all_jafs():
    data = ""
    status = ""
    if 'username' not in session:
        # no user has logged in
        status = "false"
        data = "Invalid Session"
    elif session['user_type'] != 1:
        # logged in user is not an IC
        status = "false"
        data = "User is not an IC"
    else:
        # ic_id = session['username']

        try:
            query = """
                select
                    company.id,
                    jaf_no,
                    jaf.name,
                    description,
                    stipend,
                    cpi_cutoff,
                    company.name,
                    is_verified
                from jaf, company
                where jaf.company_id = company.id
                """
            res = conn.execute(query)
            data = []
            for row in res:
                eligible_departments = []
                sub_query = """
                    with ed as
                      (
                        select id, name, true as is_eligible
                        from eligibility join department on dept_id = id
                        where company_id = %s
                            and jaf_no = %s
                      )
                    select id, name,
                      case
                        when is_eligible IS null then false
                        else is_eligible
                      end
                    from department natural left join ed
                    """
                sub_res = conn.execute(sub_query, (int(row[0]), int(row[1])))
                for dept in sub_res:
                    eligible_departments.append({
                            'dept_id': int(dept[0]),
                            'name': dept[1],
                            'is_eligible': dept[2]
                        })

                data.append({
                        'company_id': row[0],
                        'company_name': row[6],
                        'jaf_no': row[1],
                        'jaf_name': row[2],
                        'description': row[3],
                        'stipend': row[4],
                        'cpi_cutoff': float(row[5]),
                        'is_verified': row[7],
                        'eligible_departments': eligible_departments
                    })

            status = "true"
        except Exception as e:
            status = "false"
            data = str(e)

    return jsonify({
        'data': data,
        'status': status
    })


@ic_blueprint.route('/ic/jafs/alloted', methods=['GET'])
@swag_from('docs/ic_view_alloted_jafs.yml')
def ic_view_alloted_jafs():
    data = ""
    status = ""
    if 'username' not in session:
        # no user has logged in
        status = "false"
        data = "Invalid Session"
    elif session['user_type'] != 1:
        # logged in user is not an IC
        status = "false"
        data = "User is not an IC"
    else:
        ic_id = int(session['username'])

        try:
            query = """
                with jafs as
                    (select *
                     from jaf
                     where alloted_ic_id = %s)
                select
                    company.id,
                    jaf_no,
                    jafs.name,
                    description,
                    stipend,
                    cpi_cutoff,
                    company.name,
                    is_verified
                from jafs, company
                where jafs.company_id = company.id
                """
            res = conn.execute(query, (ic_id))
            data = []
            for row in res:
                eligible_departments = []
                sub_query = """
                    with ed as
                      (
                        select id, name, true as is_eligible
                        from eligibility join department on dept_id = id
                        where company_id = %s
                            and jaf_no = %s
                      )
                    select id, name,
                      case
                        when is_eligible IS null then false
                        else is_eligible
                      end
                    from department natural left join ed
                    """
                sub_res = conn.execute(sub_query, (int(row[0]), int(row[1])))
                for dept in sub_res:
                    eligible_departments.append({
                            'dept_id': int(dept[0]),
                            'name': dept[1],
                            'is_eligible': dept[2]
                        })

                data.append({
                        'company_id': row[0],
                        'company_name': row[6],
                        'jaf_no': row[1],
                        'jaf_name': row[2],
                        'description': row[3],
                        'stipend': row[4],
                        'cpi_cutoff': float(row[5]),
                        'is_verified': row[7],
                        'eligible_departments': eligible_departments
                    })

            status = "true"
        except Exception as e:
            status = "false"
            data = str(e)

    return jsonify({
        'data': data,
        'status': status
    })


@ic_blueprint.route('/ic/jaf', methods=['POST'])
@swag_from('docs/ic_view_jaf.yml')
def ic_view_jaf():
    data = ""
    status = ""
    if 'username' not in session:
        # no user has logged in
        status = "false"
        data = "Invalid Session"
    elif session['user_type'] != 1:
        # logged in user is not an IC
        status = "false"
        data = "User is not an IC"
    else:
        ic_id = int(session['username'])

        try:
            request_data = request.get_json()
            company_id = int(request_data['company_id'])
            jaf_no = int(request_data['jaf_no'])

            query = """
                with jafs as
                    (select *
                     from jaf
                     where alloted_ic_id = %s)
                select
                    company.id,
                    jaf_no,
                    jafs.name,
                    description,
                    stipend,
                    cpi_cutoff,
                    company.name,
                    is_verified
                from jafs, company
                where jafs.company_id = company.id
                    and jaf_no = %s
                    and company_id = %s
                """
            res = list(conn.execute(query, (ic_id, jaf_no, company_id)).first())

            eligible_departments = []
            sub_query = """
                with ed as
                  (
                    select id, name, true as is_eligible
                    from eligibility join department on dept_id = id
                    where company_id = %s
                        and jaf_no = %s
                  )
                select id, name,
                  case
                    when is_eligible IS null then false
                    else is_eligible
                  end
                from department natural left join ed
                """
            sub_res = conn.execute(sub_query, (int(res[0]), int(res[1])))
            for dept in sub_res:
                eligible_departments.append({
                        'dept_id': int(dept[0]),
                        'name': dept[1],
                        'is_eligible': dept[2]
                    })

            data = {
                    'company_id': res[0],
                    'company_name': res[6],
                    'jaf_no': res[1],
                    'jaf_name': res[2],
                    'description': res[3],
                    'stipend': res[4],
                    'cpi_cutoff': float(res[5]),
                    'is_verified': res[7],
                    'eligible_departments': eligible_departments
                }
            status = "true"
        except Exception as e:
            status = "false"
            data = str(e)

    return jsonify({
        'data': data,
        'status': status
    })


@ic_blueprint.route('/ic/verify', methods=['POST'])
@swag_from('docs/ic_verify_jaf.yml')
def ic_verify_jaf():
    data = ""
    status = ""
    if 'username' not in session:
        # no user has logged in
        status = "false"
        data = "Invalid Session"
    elif session['user_type'] != 1:
        # logged in user is not an IC
        status = "false"
        data = "User is not an IC"
    else:
        ic_id = int(session['username'])

        try:
            request_data = request.get_json()
            company_id = int(request_data['company_id'])
            jaf_no = int(request_data['jaf_no'])

            query = """
                select alloted_ic_id, is_verified
                from jaf
                where company_id = %s
                    and jaf_no = %s
                """
            res = list(conn.execute(query, (company_id, jaf_no)).first())

            if (res[0] == ic_id):
                if not res[1]:
                    # verify, update jaf table
                    query = """
                        update jaf
                        set is_verified = true
                        where company_id = %s and jaf_no = %s
                        """
                    conn.execute(query, (company_id, jaf_no))
                    status = "true"
                    data = "verified successfully"
                else:
                    status = "false"
                    data = "Already verified"
            else:
                status = "false"
                data = "alloted IC is different."

        except Exception as e:
            status = "false"
            data = str(e)

    return jsonify({
        'data': data,
        'status': status
    })


@ic_blueprint.route('/ic/pending_resume', methods=['GET'])
@swag_from('docs/ic_pending_resume.yml')
def pending_resume_verification():
    data = ""
    status = ""
    if 'username' not in session:
        # no user has logged in
        status = "false"
        data = "Invalid Session"
    elif session['user_type'] != 1:
        # logged in user is not an IC
        status = "false"
        data = "User is not an IC"
    else:
        try:
            query = """
                select rollno
                from resume
                where verified_ic is null;
                """
            students = conn.execute(query)

            data = []
            for row in students:
                rollno = row[0]
                sub_query = """
                    select
                        rollno,
                        S.name,
                        S.cpi,
                        D.name
                    from student as S, department as D
                    where S.dept_id = D.id
                        and S.rollno = %s
                    """
                res = list(conn.execute(sub_query, (rollno)).first())
                data.append({
                        'rollno': res[0],
                        'name': res[1],
                        'cpi': float(res[2]),
                        'dept_name': res[3]
                    })
            status = "true"
        except Exception as e:
            status = "false"
            data = str(e)

    return jsonify({
        'data': data,
        'status': status
    })
