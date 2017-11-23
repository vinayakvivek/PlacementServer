from flask import Blueprint
from flask import jsonify, request, session
from flasgger import swag_from

from server import conn

company_blueprint = Blueprint('company_blueprint', __name__)


def get_departments():
    query = """
        select *
        from department
        """
    res = conn.execute(query)
    data = []
    for row in res:
        data.append({
                'dept_id': row[0],
                'name': row[1]
            })
    return res


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
            res = list(conn.execute(query, (company_id, )).first())
            data = {
                'name': res[0],
                'email': res[1]
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
            name = request_data['jaf_name']
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
                # get IC with lowest no of jafs alloted to him/her
                query = """
                    with ic_jaf_count as
                      (select alloted_ic_id, count(*) as jaf_count
                       from jaf
                       group by alloted_ic_id
                       order by jaf_count asc)
                    select ic.id, rollno,
                        case
                          when jaf_count IS null then 0
                          else jaf_count
                        end
                    from ic left outer join ic_jaf_count
                        on ic.id = ic_jaf_count.alloted_ic_id
                    order by jaf_count asc
                    limit 1
                    """

                res = list(conn.execute(query).first())

                query = """
                    insert into
                    jaf(company_id, jaf_no, name, description, stipend, cpi_cutoff, alloted_ic_id)
                    values(%s, %s, %s, %s, %s, %s, %s)
                    """
                conn.execute(query, (company_id, jaf_no, name, description, stipend, cpi_cutoff, int(res[0])))

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

        except Exception as e:
            status = "false"
            data = str(e)

    return jsonify({
        'data': data,
        'status': status
    })


@company_blueprint.route('/company/editjaf', methods=['POST'])
@swag_from('docs/company_edit_jaf.yml')
def edit_jaf():
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
            name = request_data['jaf_name']
            description = request_data['description']
            stipend = request_data['stipend']
            cpi_cutoff = request_data['cpi_cutoff']
            eligible_depts = request_data['eligible_departments']

            # check if jaf_no already exist
            # cannot edit once verified by IC
            query = """
                select count(*)
                from jaf
                where company_id = %s
                    and jaf_no = %s
                    and is_verified = false
                """
            res = list(conn.execute(query, (company_id, jaf_no, )).first())
            if (res[0] == 0):
                status = "false"
                data = "JAF does not exist / already verified"
            else:
                query = """
                    update jaf
                    set name = %s,
                        description = %s,
                        stipend = %s ,
                        cpi_cutoff = %s
                    where company_id = %s
                        and jaf_no = %s
                    """
                conn.execute(query, (name, description, stipend, cpi_cutoff, company_id, jaf_no))

                # delete related entries in eligibility
                query = """
                    delete
                    from eligibility
                    where company_id = %s and jaf_no = %s
                    """
                conn.execute(query, (company_id, jaf_no))

                query = """
                    insert into
                    eligibility
                    values (%s, %s, %s)
                    """
                for dept in eligible_depts:
                    conn.execute(query, (company_id, jaf_no, int(dept['dept_id'])))

                status = "true"
                data = "successfully updated JAF"

        except Exception as e:
            status = "false"
            data = str(e)

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
                    cpi_cutoff,
                    is_verified
                from jaf
                where company_id = %s
                """
            res = conn.execute(query, (company_id))
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

                sub_res = conn.execute(sub_query, (company_id, int(row[0])))
                for dept in sub_res:
                    eligible_departments.append({
                            'dept_id': int(dept[0]),
                            'name': dept[1],
                            'is_eligible': dept[2]
                        })

                data.append({
                        'jaf_no': row[0],
                        'jaf_name': row[1],
                        'description': row[2],
                        'stipend': row[3],
                        'cpi_cutoff': float(row[4]),
                        'is_verified': row[5],
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


@company_blueprint.route('/company/jaf', methods=['POST'])
@swag_from('docs/company_jaf_details.yml')
def comapany_view_jaf_details():
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
            request_data = request.get_json()
            jaf_no = int(request_data['jaf_no'])

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
                        name,
                        description,
                        stipend,
                        cpi_cutoff,
                        is_verified
                    from jaf
                    where company_id = %s and jaf_no = %s
                    """
                res = list(conn.execute(query, (company_id, jaf_no)).first())
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
                sub_res = conn.execute(sub_query, (company_id, jaf_no))
                for dept in sub_res:
                    eligible_departments.append({
                            'dept_id': int(dept[0]),
                            'name': dept[1],
                            'is_eligible': dept[2]
                        })

                data = {
                    'jaf_no': jaf_no,
                    'jaf_name': res[1],
                    'description': res[2],
                    'stipend': res[3],
                    'cpi_cutoff': float(res[4]),
                    'is_verified': res[5],
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


@company_blueprint.route('/company/jaf/students', methods=['POST'])
@swag_from('docs/company_signed_students.yml')
def comapany_view_signed_students():
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
            request_data = request.get_json()
            jaf_no = int(request_data['jaf_no'])

            # check if jaf exists
            query = """
                select count(*)
                from jaf
                where company_id = %s and jaf_no = %s
                """
            res = list(conn.execute(query, (company_id, jaf_no)).first())
            if (res[0] == 1):
                query = """
                    select
                        student.name,
                        cpi,
                        department.name,
                        is_shortlisted,
                        date_signed
                    from signedjafs natural join student, department
                    where company_id = %s
                        and jaf_no = %s
                        and department.id = dept_id
                    """
                res = conn.execute(query, (company_id, jaf_no))
                data = []
                for row in res:
                    data.append({
                            'name': row[0],
                            'cpi': float(row[1]),
                            'dept': row[2],
                            'is_shortlisted': bool(row[3]),
                            'date_signed': row[4]
                        })
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


@company_blueprint.route('/company/jaf/shortlist', methods=['POST'])
@swag_from('docs/company_shortlist_student.yml')
def shortlist_student():
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
            request_data = request.get_json()
            jaf_no = int(request_data['jaf_no'])
            rollno = request_data['rollno']

            # check if student signed jaf exists
            query = """
                select count(*)
                from signedjafs
                where company_id = %s
                    and jaf_no = %s
                    and rollno = %s
                """
            res = list(conn.execute(query, (company_id, jaf_no, rollno)).first())
            if (res[0] == 1):
                query = """
                    update signedjafs
                    set is_shortlisted = true
                    where company_id = %s
                        and jaf_no = %s
                        and rollno = %s
                    """
                conn.execute(query, (company_id, jaf_no, rollno))
                status = "true"
                data = "successfully shortlisted student"
            else:
                status = "false"
                data = "student hasn't signed up JAF"

        except Exception as e:
            status = "false"
            data = str(e)

    return jsonify({
        'data': data,
        'status': status
    })
