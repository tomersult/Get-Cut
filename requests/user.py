from flask import Blueprint
from flask import request, jsonify, make_response
import uuid
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from requests.notification_counter import NotificationCounter

user_bp = Blueprint('account_api_user', __name__)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(200))
    email = db.Column(db.String(80))
    city = db.Column(db.String(50))
    gender = db.Column(db.String(8))
    dateOfBirth = db.Column(db.String(30))


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        else:
            return jsonify({'message': 'header x-access-token is missing!'}), 401

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        current_user = User.query.filter_by(public_id=token).first()

        if not current_user:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


@user_bp.route('/userInfo/<public_id>', methods=['GET'])
def get_one_user(public_id):
    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message': 'No user found!'})

    user_data = {'name': user.name, 'email': user.email, 'city': user.city, 'gender': user.gender}

    return jsonify(user_data)


@user_bp.route('/createUser', methods=['POST'])
def create_user():
    data = request.get_json()

    users = User.query.all()
    for user in users:
        if user.email == data['email']:
            return jsonify({'message': 'This email already exist!'}), 401

    hashed_password = generate_password_hash(data['password'], method='sha256')
    public_id = str(uuid.uuid4())
    new_user = User(public_id=public_id, name=data['userName'], password=hashed_password, email=data['email'],
                    city=data['location'], gender=data['gender'], dateOfBirth=data['dateOfBirth'])
    db.session.add(new_user)
    db.session.commit()

    new_notification_counter = NotificationCounter(user_public_id=public_id, counter=0)
    db.session.add(new_notification_counter)
    db.session.commit()

    return jsonify({'message': 'New user created!'})


@user_bp.route('/login', methods=['POST'])
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    user = User.query.filter_by(name=auth.username).first()

    if not user:
        return make_response('User name not found', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    if check_password_hash(user.password, auth.password):
        token = user.public_id
        return {"token": token}

    return make_response('Wrong password', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})
