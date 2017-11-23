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
        ic_id = session['username']
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
                    select id, name
                    from eligibility join department on dept_id = id
                    where company_id = %s
                        and jaf_no = %s
                    """
                sub_res = conn.execute(sub_query, (int(row[0]), int(row[1])))
                for dept in sub_res:
                    eligible_departments.append({
                            'dept_id': int(dept[0]),
                            'name': dept[1]
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
        ic_id = session['username']

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
                    select id, name
                    from eligibility join department on dept_id = id
                    where company_id = %s
                        and jaf_no = %s
                    """
                sub_res = conn.execute(sub_query, (int(row[0]), int(row[1])))
                for dept in sub_res:
                    eligible_departments.append({
                            'dept_id': int(dept[0]),
                            'name': dept[1]
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
