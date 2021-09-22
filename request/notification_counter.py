from flask import Blueprint, request, jsonify
from database import db


class NotificationCounter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_public_id = db.Column(db.String(50))
    counter = db.Column(db.Integer)


notification_counter_bp = Blueprint('account_api_notification_counter', __name__)


def reset_notification_counter(user_public_id):
    notification_counter = NotificationCounter.query.filter_by(user_public_id=user_public_id).first()
    notification_counter.counter = 0
    db.session.commit()
    return jsonify({'message': 'Notification counter reset!'})


def add_one_to_notification_counter(user_public_id):
    notification_counter = NotificationCounter.query.filter_by(user_public_id=user_public_id).first()
    if not notification_counter:
        return jsonify({'message': 'This user does not have counter!'})
    notification_counter.counter += 1
    db.session.commit()
