from datetime import datetime
from flask import Blueprint
from flask import request, jsonify, make_response
from database import db

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
def upload():
    data = request.get_json()
    grade = 0
    followers = 0
    creation_time = datetime.utcnow()
    new_barber = Barber(public_id=data['public_id'], barber_name=data['barber_name'], location=data['location'],
                        grade=grade, followers=followers, creation_time=creation_time,
                        specialization=data['specialization'], description=data['description'])
    db.session.add(new_barber)
    db.session.commit()

    return jsonify({'message': 'New barber created!'})

