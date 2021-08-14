from flask import Blueprint
from flask import request, jsonify
from database import db
from requests.user import token_required
import datetime
from requests.dayBook import DayBook, updateTime

appointment_bp = Blueprint('appointment_api_barber', __name__)


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_public_id = db.Column(db.String(50))
    barber_public_id = db.Column(db.String(50))
    day = db.Column(db.String(50))
    month = db.Column(db.String(50))
    year = db.Column(db.String(50))
    start = db.Column(db.String(50))
    amount_of_time = db.Column(db.String(50))
    haircut_type = db.Column(db.String(50))
    price = db.Column(db.String(500))


@appointment_bp.route('/appointment', methods=['POST'])
@token_required
def create_appointment(current_user):
    data = request.get_json()

    creation_time = datetime.datetime.now()
    # initialize the start time of the appointment
    start_time = datetime.datetime.strptime(data['start'], '%H:%M')
    temp_time = creation_time.replace(minute=start_time.minute, hour=start_time.hour, second=0, microsecond=0,
                                      year=int(data['year']), month=int(data['month']), day=int(data['day']))
    # every time cycle is 15 min
    num_of_time_cycle = int(int(data['amount_of_time']) / 15)

    # get barber day in daybook
    my_day = DayBook.query.filter_by(barber_public_id=data['barber_public_id'], day=data['day'],
                                     month=data['month'], year=data['year']).first()
    if not my_day:
        return jsonify({'message': 'This barber not available at this day!'})

    for i in range(num_of_time_cycle):
        str1 = temp_time.strftime("%H:%M")
        updateTime(str1, my_day, True)
        temp_time = temp_time + datetime.timedelta(minutes=15)

    new_appointment = Appointment(user_public_id=current_user.public_id, barber_public_id=data['barber_public_id'],
                                  day=data['day'], month=data['month'], year=data['year'],
                                  start=data['start'], amount_of_time=data['amount_of_time'],
                                  haircut_type=data['haircut_type'], price=data['price'])
    db.session.add(new_appointment)
    db.session.commit()

    return jsonify({'message': 'New appointment created!'})


# need change !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@appointment_bp.route('/appointment', methods=['GET'])
@token_required
def get_user_appointments(current_user):
    appointments = Appointment.query.filter_by(user_public_id=current_user.public_id).all()
    output = []

    for appointment in appointments:
        appointment_data = {}
        appointment_data['user_public_id'] = appointment.user_public_id
        appointment_data['barber_public_id'] = appointment.barber_public_id
        appointment_data['start'] = appointment.start
        appointment_data['end'] = appointment.end
        appointment_data['haircut_type'] = appointment.haircut_type
        appointment_data['comments'] = appointment.comments
        output.append(appointment_data)

    return jsonify({'User appointments': output})


@appointment_bp.route('/appointment', methods=['DELETE'])
def delete_appointment():
    data = request.get_json()

    creation_time = datetime.datetime.now()
    # initialize the start time of the appointment
    start_time = datetime.datetime.strptime(data['start'], '%H:%M')
    temp_time = creation_time.replace(minute=start_time.minute, hour=start_time.hour, second=0, microsecond=0,
                                      year=int(data['year']), month=int(data['month']), day=int(data['day']))
    # every time cycle is 15 min
    num_of_time_cycle = int(int(data['amount_of_time']) / 15)

    appointment = Appointment.query.filter_by(barber_public_id=data['barber_public_id'], day=data['day'],
                                              month=data['month'], year=data['year'], start=data['start'],
                                              amount_of_time=data['amount_of_time']).first()
    if not appointment:
        return jsonify({'message': 'This barber not available!'})

    # get barber day in daybook
    my_day = DayBook.query.filter_by(barber_public_id=data['barber_public_id'], day=data['day'],
                                     month=data['month'], year=data['year']).first()
    if not my_day:
        return jsonify({'message': 'This barber not available at this day!'})

    for i in range(num_of_time_cycle):
        str1 = temp_time.strftime("%H:%M")
        updateTime(str1, my_day, False)
        temp_time = temp_time + datetime.timedelta(minutes=15)

    db.session.delete(appointment)
    db.session.commit()
    return jsonify({'message': 'The appointment has been deleted! ' + data['user_public_id']})

