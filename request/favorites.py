from flask import Blueprint
from flask import request, jsonify
from database import db
from request.barber import Barber
from request.user import token_required, User

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
    barber = Barber.query.filter_by(public_id=data['barber_public_id']).first()
    for favorite in favorites:
        if (favorite.user_public_id == current_user.public_id) & (favorite.barber_public_id == data['barber_public_id']):
            db.session.delete(favorite)
            db.session.commit()
            barber.followers -= 1
            db.session.commit()
            return jsonify({'message': 'Now you unfollow this barber !'})
    new_favorite = Favorite(user_public_id=current_user.public_id, barber_public_id=data['barber_public_id'])
    db.session.add(new_favorite)
    db.session.commit()

    if not barber:
        db.session.delete(new_favorite)
        db.session.commit()
        return jsonify({'message': 'No Barber found!'})
    barber.followers += 1
    db.session.commit()

    return jsonify({'message': 'New favorite added!'})


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

            barber = Barber.query.filter_by(public_id=data['barber_public_id']).first()
            if not barber:
                return jsonify({'message': 'No Barber found!'})
            barber.followers -= 1
            db.session.commit()
            return jsonify({'message': 'Favorite deleted!'})
    return jsonify({'message': 'No favorite found!'})
