from flask import Blueprint
from flask import request, jsonify
from database import db
from requests.barber import Barber
from requests.user import token_required, User

rating_bp = Blueprint('account_api_rating', __name__)


class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_public_id = db.Column(db.String(50))
    barber_public_id = db.Column(db.String(50))
    rate = db.Column(db.Integer)


@rating_bp.route('/addRate', methods=['POST'])
@token_required
def add_rate(current_user):
    data = request.get_json()

    # add new rate to database rating table
    rating = Rating.query.all()
    for one_rate in rating:
        if (one_rate.user_public_id == current_user.public_id) & \
                (one_rate.barber_public_id == data['barber_public_id']):
            one_rate.rate = data['rate']
            db.session.commit()
            updateRating(data, False)
            return jsonify({'message': 'The rate changed!'})
    new_rate = Rating(user_public_id=current_user.public_id, barber_public_id=data['barber_public_id'],
                      rate=data['rate'])
    db.session.add(new_rate)
    db.session.commit()

    updateRating(data, new_rate)

    return jsonify({'message': 'New rate added!'})


@rating_bp.route('/removeRate', methods=['DELETE'])
@token_required
def delete_rate(current_user):
    data = request.get_json()
    rating = Rating.query.all()
    if not rating:
        return jsonify({'message': 'Rate not found!'})
    for one_rate in rating:
        if (one_rate.user_public_id == current_user.public_id) & \
                (data['barber_public_id'] == one_rate.barber_public_id):
            db.session.delete(one_rate)
            db.session.commit()
            updateRating(data, False)
            return jsonify({'message': 'Rate deleted!'})
    return jsonify({'message': 'Rate not found!'})


def updateRating(data, new_rate):
    # update average barber rating
    rating = Rating.query.all()
    rate_counter = 0
    cumulative_rating = 0
    for one_rate in rating:
        if one_rate.barber_public_id == data['barber_public_id']:
            cumulative_rating += one_rate.rate
            rate_counter += 1
    average_rating = 0
    if rate_counter != 0 and cumulative_rating != 0:
        average_rating = cumulative_rating / rate_counter
    barber = Barber.query.filter_by(public_id=data['barber_public_id']).first()
    if not barber:
        if new_rate is not False:
            db.session.delete(new_rate)
            db.session.commit()
        return jsonify({'message': 'No Barber found!'})
    barber.grade = average_rating
    db.session.commit()
