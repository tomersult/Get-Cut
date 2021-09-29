import base64
import uuid
from datetime import datetime
from functools import wraps
from flask import Blueprint, current_app
from flask import request, jsonify
from database import db
from request.user import token_required
from PIL import Image
import io

barber_bp = Blueprint('account_api_barber', __name__)


class Barber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    barber_name = db.Column(db.String(80))
    location = db.Column(db.String(80))
    location_lat = db.Column(db.String(80))
    location_lng = db.Column(db.String(80))
    grade = db.Column(db.Integer)
    followers = db.Column(db.Integer)
    picture = db.Column(db.String(200))
    creation_time = db.Column(db.String(50))
    sentence = db.Column(db.String(500))
    headline = db.Column(db.String(500))


def barber_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        else:
            return jsonify({'message': 'header x-access-token is missing!'}), 401

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        current_barber = Barber.query.filter_by(public_id=token).first()
        if not current_barber:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_barber, *args, **kwargs)

    return decorated


@barber_bp.route('/createBarber', methods=['POST'])
def create():
    data = request.get_json()
    grade = 0
    followers = 0
    creation_time = datetime.utcnow()

    barbers = Barber.query.all()
    for barber in barbers:
        if barber.barber_name == data['barber_name']:
            return jsonify({'message': 'This barber already created!'})

    new_public_id = str(uuid.uuid4())
    file_name = new_public_id + '.jpeg'
    save_image(file_name, current_app.config['BARBER_PROFILE_IMAGE_PATH'], data['picture'])
    new_barber = Barber(public_id=new_public_id, barber_name=data['barber_name'],
                        location_lat=data['exactLocation']['location_lat'], location_lng=data['exactLocation']['location_lng'],
                        grade=grade, followers=followers, picture=file_name, creation_time=creation_time,
                        sentence=data['summary']['sentence'], headline=data['summary']['headline'], location=data['location'])
    db.session.add(new_barber)
    db.session.commit()
    return jsonify({'message': 'New barber created!'})


@barber_bp.route('/getBarber/<public_id>', methods=['GET'])
def get_barber(public_id):
    barber = Barber.query.filter_by(public_id=public_id).first()
    if not barber:
        return jsonify({'message': 'No Barber found!'})

    exact_location = {}
    summary = {}
    try:
        with open(current_app.config['BARBER_PROFILE_IMAGE_PATH'] + barber.picture, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
    except:
        return jsonify({'message': 'barber dont have profile image!'})

    barber_data = {}
    barber_data['public_id'] = barber.public_id
    barber_data['barber_name'] = barber.barber_name
    exact_location['location_lat'] = barber.location_lat
    exact_location['location_lng'] = barber.location_lng
    barber_data['exact_location'] = exact_location
    barber_data['grade'] = barber.grade
    barber_data['followers'] = barber.followers
    barber_data['picture'] = str(encoded_string)
    summary['creation_time'] = barber.creation_time
    summary['sentence'] = barber.sentence
    summary['headline'] = barber.headline
    barber_data['summary'] = summary

    return jsonify(barber_data)


@barber_bp.route('/getAllBarbers', methods=['GET'])
def get_all_barbers():
    barbers = Barber.query.all()
    output = []
    exact_location = {}
    summary = {}

    for barber in barbers:
        try:
            with open(current_app.config['BARBER_PROFILE_IMAGE_PATH'] + barber.picture, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())
        except:
            return jsonify({'message': 'barber dont have profile image!'})

        barber_data = {}
        barber_data['public_id'] = barber.public_id
        barber_data['barber_name'] = barber.barber_name
        exact_location['location_lat'] = barber.location_lat
        exact_location['location_lng'] = barber.location_lng
        barber_data['exact_location'] = exact_location
        barber_data['grade'] = barber.grade
        barber_data['followers'] = barber.followers
        barber_data['picture'] = str(encoded_string)
        summary['time'] = barber.creation_time
        summary['sentence'] = barber.sentence
        summary['headline'] = barber.headline
        barber_data['summary'] = summary
        output.append(barber_data)

    return jsonify(output)


@barber_bp.route('/getCityBarbers', methods=['GET'])
@token_required
def get_my_city_barbers(user_public_id):
    barbers = Barber.query.filter_by(location=user_public_id.city).all()
    from request.favorites import Favorite
    output = []
    for barber in barbers:
        try:
            with open(current_app.config['BARBER_PROFILE_IMAGE_PATH'] + barber.picture, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())
        except:
            return jsonify({'message': 'barber dont have profile image!'})
        favorite_bool = True
        favorite = Favorite.query.filter_by(barber_public_id=barber.public_id).first()
        if not favorite:
            favorite_bool = False
        barber_data = {}
        summary={}
        exact_location={}
        barber_data['id'] = barber.public_id
        barber_data['barberName'] = barber.barber_name
        barber_data['location'] = barber.location
        exact_location['location_lat'] = barber.location_lat
        exact_location['location_lng'] = barber.location_lng
        barber_data['exactLocation'] = exact_location
        barber_data['grade'] = barber.grade
        barber_data['followers'] = barber.followers
        barber_data['picture'] = str(encoded_string)
        barber_data['favorite'] = favorite_bool
        summary['time'] = barber.creation_time
        summary['sentence'] = barber.sentence
        summary['headline'] = barber.headline
        barber_data['summary'] = summary
        output.append(barber_data)

    return jsonify(output)


@barber_bp.route('/barber/<public_id>', methods=['DELETE'])
def delete_barber(public_id):
    barber = Barber.query.filter_by(public_id=public_id).first()
    from request.favorites import Favorite
    followers = Favorite.query.all()

    for follow in followers:
        if follow.barber_public_id == public_id:
            db.session.delete(follow)
            db.session.commit()

    if not barber:
        return jsonify({'message': 'No barber found!'})

    db.session.delete(barber)
    db.session.commit()

    return jsonify({'message': 'The barber has been deleted!'})


def save_image(file_name, path, image_string):
    image = base64.b64decode(str(image_string))
    image_path = (path + file_name)
    img = Image.open(io.BytesIO(image))
    img.save(image_path, 'jpeg')
