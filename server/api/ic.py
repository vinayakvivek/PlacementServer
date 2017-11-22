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
