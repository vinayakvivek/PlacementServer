from flask import Blueprint
from flask import jsonify, request, session
from flasgger import swag_from

from server import conn

company_blueprint = Blueprint('company_blueprint', __name__)


@company_blueprint.route('/company/register', methods=['POST'])
@swag_from('docs/company_register.yml')
def company_register():
    data = ""
    status = ""

    request_data = request.get_json()

    try:
        company_name = request_data['name']
        company_email = request_data['email']
        company_password = request_data['password']

        query = """
                insert into company(name,email,password)
                values(%s,%s,%s)
                """
        conn.execute(query, (company_name, company_email, company_password))
        data = "Company registered"
        status = "true"
    except KeyError:
        data = "bad request"
        status = "false"
    except:
        data = "Company Email already used"
        status = "false"

    return jsonify({
        'data': data,
        'status': status
    })


@company_blueprint.route('/company/', methods=['GET'])
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


@company_blueprint.route('/company/addjaf', methods=['POST'])
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

        try:
            jaf_no = int(request_data['jaf_no'])
            name = request_data['name']
            description = request_data['description']
            stipend = request_data['stipend']
            cpi_cutoff = request_data['cpi_cutoff']
            eligible_depts = request_data['eligible_departments']

            # check if jaf_no already exists
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

                query = """
                    insert into
                    eligibility
                    values (%s, %s, %s)
                    """
                for dept in eligible_depts:
                    # print(dept['dept_id'], dept['name'])
                    conn.execute(query, (company_id, jaf_no, int(dept['dept_id'])))

                status = "true"
                data = "successfully added new JAF"
        except KeyError:
            data = "bad request"
            status = "false"
        except:
            status = "false"
            data = "database error"

    return jsonify({
        'data': data,
        'status': status
    })


@company_blueprint.route('/company/jafs', methods=['GET'])
@swag_from('docs/company_jafs.yml')
def comapany_view_jafs():
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
                select
                    jaf_no,
                    name,
                    description,
                    stipend,
                    cpi_cutoff
                from jaf
                where company_id = %s
                """
            res = conn.execute(query, (company_id))
            data = []
            for row in res:
                eligible_departments = []
                sub_query = """
                    select id, name
                    from eligibility join department on dept_id = id
                    where company_id = %s
                        and jaf_no = %s
                    """
                sub_res = conn.execute(sub_query, (company_id, int(row[0])))
                for dept in sub_res:
                    eligible_departments.append({
                            'dept_id': int(dept[0]),
                            'name': dept[1]
                        })

                data.append({
                        'jaf_no': row[0],
                        'jaf_name': row[1],
                        'description': row[2],
                        'stipend': row[3],
                        'cpi_cutoff': float(row[4]),
                        'eligible_departments': eligible_departments
                    })

            status = "true"
        except:
            status = "false"
            data = "database error"

    return jsonify({
        'data': data,
        'status': status
    })


# @company_blueprint.route('/company/jaf/students', methods=['POST'])
# @swag_from('docs/company_signed_students.yml')
# def comapany_view_signed_students():
#     pass
