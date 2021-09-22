import base64
import datetime
from flask import Blueprint, current_app
from flask import jsonify
from database import db
from request.barber import Barber
from request.notification_counter import add_one_to_notification_counter, reset_notification_counter
from request.user import User, token_required
from request.appointment import Appointment
import schedule
import time
import requests


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    barber_public_id = db.Column(db.String(50))
    user_public_id = db.Column(db.String(50))
    barber_name = db.Column(db.String(50))
    barber_avatar = db.Column(db.String(100))
    date = db.Column(db.String(50))
    time = db.Column(db.String(50))
    was_read = db.Column(db.Boolean, unique=False, default=False)
    message = db.Column(db.String(200))
    short_message = db.Column(db.String(50))


notification_bp = Blueprint('account_api_notification', __name__)


@notification_bp.route('/notifications', methods=['GET'])
@token_required
def get_user_notifications(current_user):
    notifications = Notification.query.filter_by(user_public_id=current_user.public_id).all()
    if not notifications:
        return jsonify({'message': 'This user does not have notifications yet'})

    output = []
    for notification in notifications:
        # reset notification counter of this user
        reset_notification_counter(current_user.public_id)
        barber = Barber.query.filter_by(public_id=notification.barber_public_id).first()
        try:
            with open(current_app.config['BARBER_PROFILE_IMAGE_PATH'] + barber.picture, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())
        except:
            return jsonify({'message': 'barber dont have profile image!'})

        notification_data = {}
        notification_data['barber_public_id'] = notification.barber_public_id
        notification_data['user_public_id'] = notification.user_public_id
        notification_data['barber_name'] = notification.barber_name
        notification_data['barber_avatar'] = str(encoded_string)
        notification_data['date'] = notification.date
        notification_data['time'] = notification.time
        notification_data['was_read'] = notification.was_read
        notification_data['message'] = notification.message
        notification_data['short_message'] = notification.short_message
        output.append(notification_data)
    return jsonify(output)


def predict_new_appointment(current_user):
    appointments = Appointment.query.filter_by(user_public_id=current_user.public_id).all()
    centroids = {}
    counter_for_cen = 0
    for appointment in appointments:
        present = datetime.datetime.now()
        day = datetime.datetime(int(appointment.year), int(appointment.month), int(appointment.day))
        if day < present:
            if not centroids:
                centroids[counter_for_cen] = {'centroid': appointment.haircut_type + appointment.barber_public_id,
                                              'cluster': [appointment]}
                counter_for_cen += 1

            else:
                for key, value in centroids.items():
                    if value['centroid'] == appointment.haircut_type + appointment.barber_public_id:
                        my_key = key
                centroids[my_key]['cluster'].append(appointment)

    notifications = []
    for key, value in centroids.items():
        time_cycle, closest_appointment = calculate_time_cycle(value['cluster'])
        current_day = datetime.datetime.now()
        latest_appointment_date = datetime.datetime(int(closest_appointment.year), int(closest_appointment.month),
                                                    int(closest_appointment.day))
        latest_date_and_time_cycle = latest_appointment_date + datetime.timedelta(days=time_cycle)
        if (current_day - latest_date_and_time_cycle).days == 1:
            notifications.append(closest_appointment)
    return notifications


def calculate_time_cycle(appointments):
    if len(appointments) == 1:
        return -1, appointments[0]
    days = []
    for appointment in appointments:
        day = datetime.datetime(int(appointment.year), int(appointment.month), int(appointment.day))
        days.append([day, appointment])
    counter = 0
    current_day = datetime.datetime.now()
    closest_day = days[0]
    delta = 0
    for i in range(len(days) - 1):
        day0 = days[i][0]
        day1 = days[i + 1][0]
        # check witch appointment was the latest
        first_different = current_day - closest_day[0]
        second_different = current_day - day1
        if first_different > second_different:
            closest_day = days[i + 1]
        different_between_day0_day1 = abs(day0 - day1)
        delta += int(different_between_day0_day1.days)
        counter += 1
    time_cycle = int(delta / counter)
    return time_cycle, closest_day[1]


@notification_bp.route('/auto', methods=['GET'])
def check_every_user_notification():
    users = User.query.all()
    for user in users:
        notifications = predict_new_appointment(user)
        if not notifications:
            print(user.name + ' does not have notifications today')
        else:
            for appointment in notifications:
                barber = Barber.query.filter_by(public_id=appointment.barber_public_id).first()
                user = User.query.filter_by(public_id=appointment.user_public_id).first()
                current_date = str(datetime.datetime.today().date())
                current_time = str(datetime.datetime.today().time().replace(microsecond=0))
                message = 'Hello ' + user.name + '! ' + 'I noticed you did not make a ' + appointment.haircut_type + \
                          'in a long time '
                short_message = 'time to get a ' + appointment.haircut_type
                new_notification = Notification(barber_public_id=barber.public_id, barber_name=barber.barber_name,
                                                barber_avatar=barber.picture, user_public_id=user.public_id,
                                                date=current_date, time=current_time, was_read=False, message=message,
                                                short_message=short_message)
                db.session.add(new_notification)
                db.session.commit()
                add_one_to_notification_counter(user.public_id)
    return jsonify({'message': 'Sent all the relevant notification !'})


def auto_request():
    requests.get('http://127.0.0.1:5000/auto')
    requests.get('http://127.0.0.1:5000/daybookPlusDay')


def auto_func_for_notification():
    schedule.every().day.at("19:22").do(auto_request)
    while True:
        schedule.run_pending()
        time.sleep(61)
