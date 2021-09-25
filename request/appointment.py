from flask import Blueprint
from flask import request, jsonify
from database import db
from request.barber import barber_token_required, Barber
from request.user import token_required
import datetime
from request.dayBook import DayBook, updateTime, appointment_amount_of_time

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
    gender = db.Column(db.String(50))


@appointment_bp.route('/appointment', methods=['POST'])
def create_appointment():
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

    new_appointment = Appointment(user_public_id=data['user_public_id'], barber_public_id=data['barber_public_id'],
                                  day=data['day'], month=data['month'], year=data['year'],
                                  start=data['start'], amount_of_time=data['amount_of_time'],
                                  haircut_type=data['haircut_type'], price=data['price'], gender=data['gender'])
    db.session.add(new_appointment)
    db.session.commit()

    return jsonify({'message': 'New appointment created!'})


# delete after check
@appointment_bp.route('/appointment', methods=['GET'])
@token_required
def get_user_appointments(current_user):
    appointments = Appointment.query.filter_by(user_public_id=current_user.public_id).all()
    output = {}
    past_appointments = []
    future_appointments = []

    for appointment in appointments:
        end_time = appointment_amount_of_time(appointment.start, appointment.amount_of_time)
        barber = Barber.query.filter_by(public_id=appointment.barber_public_id).first()
        barber_name = barber.barber_name
        appointment_data = {}
        date = {}
        date['day'] = appointment.day
        date['month'] = appointment.month
        date['year'] = appointment.year
        appointment_data['price'] = appointment.price
        appointment_data['amountOfTime'] = appointment.amount_of_time
        appointment_data['time'] = appointment.start + '-' + end_time
        appointment_data['date'] = date
        appointment_data['gender'] = appointment.gender
        appointment_data['barberId'] = appointment.barber_public_id
        appointment_data['type'] = appointment.haircut_type
        appointment_data['barberName'] = barber_name
        present = datetime.datetime.now()
        day = datetime.datetime(int(appointment.year), int(appointment.month), int(appointment.day))
        if day < present:
            past_appointments.append(appointment_data)
        else:
            future_appointments.append(appointment_data)
    output["Past"] = past_appointments
    output['Future'] = future_appointments

    return jsonify(output)


# add to postman
@appointment_bp.route('/pastAppointment', methods=['GET'])
@token_required
def get_user_past_appointments(current_user):
    appointments = Appointment.query.filter_by(user_public_id=current_user.public_id).all()
    output = []
    for appointment in appointments:
        present = datetime.datetime.now()
        day = datetime.datetime(int(appointment.year), int(appointment.month), int(appointment.day))
        if day < present:
            end_time = appointment_amount_of_time(appointment.start, appointment.amount_of_time)
            barber = Barber.query.filter_by(public_id=appointment.barber_public_id).first()
            barber_name = barber.barber_name
            appointment_data = {}
            date = {}
            date['day'] = appointment.day
            date['month'] = appointment.month
            date['year'] = appointment.year
            appointment_data['price'] = appointment.price
            appointment_data['amountOfTime'] = appointment.amount_of_time
            appointment_data['time'] = appointment.start + '-' + end_time
            appointment_data['date'] = date
            appointment_data['gender'] = appointment.gender
            appointment_data['barberId'] = appointment.barber_public_id
            appointment_data['type'] = appointment.haircut_type
            appointment_data['barberName'] = barber_name
            output.append(appointment_data)

    return jsonify(output)


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
                                              amount_of_time=data['amount_of_time'], gender=data['gender']).first()
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
    return jsonify({'message': 'The appointment has been deleted! ' + 'User public id:' + data['user_public_id']})

