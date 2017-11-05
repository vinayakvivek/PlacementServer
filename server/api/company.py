from flask import Blueprint
from flask import jsonify, request, session
from flasgger import swag_from

from app import conn

company_blueprint = Blueprint('company_blueprint', __name__)


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


@company_blueprint.route('/company/register', methods=['POST'])
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
        conn.execute(query, (company_name, company_email, company_password))
        data = "Company registered"
        status = "true"
    except:
        data = "Company Email already used"
        status = "false"

    return jsonify({
        'data': data,
        'status': status
    })