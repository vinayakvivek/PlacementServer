from flask import Blueprint
from flask import jsonify, request, session
from flasgger import swag_from

from app import conn

auth_blueprint = Blueprint('auth_blueprint', __name__)


@auth_blueprint.route('/login', methods=['POST'])
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


@auth_blueprint.route('/logout', methods=['GET'])
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
