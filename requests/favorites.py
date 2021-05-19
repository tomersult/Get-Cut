from flask import Blueprint
from flask import request, jsonify
from database import db
from requests.barber import Barber
from requests.user import token_required, User

favorite_bp = Blueprint('account_api_favorite', __name__)


class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_public_id = db.Column(db.String(50))
    barber_public_id = db.Column(db.String(50))


@favorite_bp.route('/addFavorite', methods=['POST'])
@token_required
def add_favorite_follow(current_user):
    data = request.get_json()

    favorites = Favorite.query.all()
    for favorite in favorites:
        if (favorite.user_public_id == current_user.public_id) & (favorite.barber_public_id == data['barber_public_id']):
            return jsonify({'message': 'this barber already in favorites!'})

    new_favorite = Favorite(user_public_id=current_user.public_id, barber_public_id=data['barber_public_id'])
    db.session.add(new_favorite)
    db.session.commit()

    return jsonify({'message': 'New favorite added!'})


@favorite_bp.route('/getFavorite', methods=['GET'])
@token_required
def get_favorite(current_user):
    favorites = Favorite.query.all()
    barbers = Barber.query.all()
    output = []

    for favorite in favorites:
        if favorite.user_public_id == current_user.public_id:

            for barber in barbers:
                if favorite.barber_public_id == barber.public_id:
                    barber_data = {}
                    barber_data['public_id'] = barber.public_id
                    barber_data['barber_name'] = barber.barber_name
                    barber_data['grade'] = barber.grade
                    barber_data['followers'] = barber.followers
                    barber_data['creation_time'] = barber.creation_time
                    barber_data['specialization'] = barber.specialization
                    barber_data['description'] = barber.description
                    output.append(barber_data)

    return jsonify({'favorites': output})


@favorite_bp.route('/getFollowers', methods=['GET'])
@token_required
def get_followers(current_barber):
    followers = Favorite.query.all()
    users = User.query.all()
    output = []

    for follow in followers:
        if follow.barber_public_id == current_barber.public_id:
            for user in users:
                if user.public_id == follow.user_public_id:
                    user_data = {}
                    user_data['public_id'] = user.public_id
                    user_data['name'] = user.name
                    user_data['password'] = user.password
                    user_data['admin'] = user.admin
                    output.append(user_data)

    return jsonify({'users': output})


@favorite_bp.route('/countFollowers', methods=['GET'])
@token_required
def get_followers_number(current_barber):
    followers = Favorite.query.all()
    users = User.query.all()
    counter = 0

    for follow in followers:
        if follow.barber_public_id == current_barber.public_id:
            for user in users:
                if user.public_id == follow.user_public_id:
                    counter += 1

    return jsonify({'followers': counter})


@favorite_bp.route('/favorite', methods=['DELETE'])
@token_required
def delete_favorite(current_user):
    data = request.get_json()
    favorites = Favorite.query.all()

    for favorite in favorites:
        if (favorite.user_public_id == current_user.public_id) & (data['barber_public_id'] == favorite.barber_public_id):
            db.session.delete(favorite)
            db.session.commit()

    return jsonify({'message': 'Favorite deleted!'})
