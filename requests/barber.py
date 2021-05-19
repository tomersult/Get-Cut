from datetime import datetime
from flask import Blueprint
from flask import request, jsonify
from database import db
from requests.user import token_required

barber_bp = Blueprint('account_api_barber', __name__)


class Barber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    barber_name = db.Column(db.String(50))
    location = db.Column(db.String(80))
    grade = db.Column(db.Integer)
    followers = db.Column(db.Integer)
    creation_time = db.Column(db.String(50))
    opening_hours = db.Column(db.String(50))
    specialization = db.Column(db.String(50))
    description = db.Column(db.String(500))


@barber_bp.route('/createBarber', methods=['POST'])
@token_required
def create(current_barber):
    data = request.get_json()
    grade = 0
    followers = 0
    creation_time = datetime.utcnow()

    barbers = Barber.query.all()
    for barber in barbers:
        if barber.public_id == current_barber.public_id:
            return jsonify({'message': 'this barber already created!'})

    new_barber = Barber(public_id=current_barber.public_id, barber_name=data['barber_name'], location=data['location'],
                        grade=grade, followers=followers, creation_time=creation_time,
                        specialization=data['specialization'], description=data['description'])
    db.session.add(new_barber)
    db.session.commit()

    return jsonify({'message': 'New barber created!'})


@barber_bp.route('/getAllBarbers', methods=['GET'])
def get_all_barbers():
    barbers = Barber.query.all()
    output = []

    for barber in barbers:
        barber_data = {}
        barber_data['public_id'] = barber.public_id
        barber_data['barber_name'] = barber.barber_name
        barber_data['grade'] = barber.grade
        barber_data['followers'] = barber.followers
        barber_data['creation_time'] = barber.creation_time
        barber_data['specialization'] = barber.specialization
        barber_data['description'] = barber.description
        output.append(barber_data)

    return jsonify({'barbers': output})


@barber_bp.route('/barber/<public_id>', methods=['DELETE'])
def delete_barber(public_id):
    barber = Barber.query.filter_by(public_id=public_id).first()
    from requests.favorites import Favorite
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
