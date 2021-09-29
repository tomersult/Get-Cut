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

    time = data['time']
    time = time.split('-')[0]
    haircuts_types_all_row = data['type']
    if not haircuts_types_all_row:
        return jsonify({'message': 'Need to choose haircut type!'})
    haircuts_string = haircuts_types_all_row[0]['name']
    for i in range(1, len(haircuts_types_all_row)):
        haircuts_string += ','
        haircuts_string += haircuts_types_all_row[i]['name']
    # initialize the start time of the appointment
    start_time = datetime.datetime.strptime(time, '%H:%M')
    temp_time = creation_time.replace(minute=start_time.minute, hour=start_time.hour, second=0, microsecond=0,
                                      year=int(data['year']), month=int(data['month']), day=int(data['day']))
    # every time cycle is 15 min
    num_of_time_cycle = int(int(data['amountOfTime']) / 15)

    # get barber day in daybook
    my_day = DayBook.query.filter_by(barber_public_id=data['barberId'], day=data['day'],
                                     month=data['month'], year=data['year']).first()
    if not my_day:
        return jsonify({'message': 'This barber not available at this day!'})

    for i in range(num_of_time_cycle):
        str1 = temp_time.strftime("%H:%M")
        updateTime(str1, my_day, True)
        temp_time = temp_time + datetime.timedelta(minutes=15)

    # type
    new_appointment = Appointment(user_public_id=data['user_public_id'], barber_public_id=data['barberId'],
                                  day=data['day'], month=data['month'], year=data['year'],
                                  start=data['time'], amount_of_time=data['amountOfTime'],
                                  haircut_type=haircuts_string, price=data['price'], gender=data['gender'])
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
        time_for_date_time = appointment.start
        time_for_date_time = time_for_date_time.split('-')[0]
        hours_for_date_time = time_for_date_time.split(':')[0]
        minutes_for_date_time = time_for_date_time.split(':')[1]
        haircut_type = appointment.haircut_type.split(',')
        barber = Barber.query.filter_by(public_id=appointment.barber_public_id).first()
        barber_name = barber.barber_name
        appointment_data = {}
        date = {}
        day = datetime.datetime(int(appointment.year), int(appointment.month), int(appointment.day),
                                int(hours_for_date_time), int(minutes_for_date_time))
        appointment_data['date_time'] = day
        date['day'] = appointment.day
        date['month'] = appointment.month
        date['year'] = appointment.year
        appointment_data['price'] = appointment.price
        appointment_data['amountOfTime'] = appointment.amount_of_time
        appointment_data['time'] = appointment.start
        appointment_data['date'] = date
        appointment_data['gender'] = appointment.gender
        appointment_data['barberId'] = appointment.barber_public_id
        appointment_data['type'] = haircut_type
        appointment_data['barberName'] = barber_name
        appointment_data['appointmentId'] = appointment.id
        present = datetime.datetime.now()
        if day < present:
            past_appointments.append(appointment_data)
        else:
            future_appointments.append(appointment_data)
    past_appointments.sort(key=lambda item:item['date_time'], reverse=False)
    future_appointments.sort(key=lambda item: item['date_time'], reverse=False)
    output["past"] = past_appointments
    output['future'] = future_appointments

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
    appointment_id = int(request.args.get('appointment_id'))
    appointment = db.session.query(Appointment).get(appointment_id)
    if not appointment:
        return jsonify({'message': 'This barber not available!'})

    creation_time = datetime.datetime.now()

    start_time_string = appointment.start
    start_time_string = start_time_string.split('-')[0]

    # initialize the start time of the appointment
    start_time = datetime.datetime.strptime(start_time_string, '%H:%M')
    temp_time = creation_time.replace(minute=start_time.minute, hour=start_time.hour, second=0, microsecond=0,
                                      year=int(appointment.year), month=int(appointment.month), day=int(appointment.day))
    # every time cycle is 15 min
    num_of_time_cycle = int(int(appointment.amount_of_time) / 15)

    # get barber day in daybook
    my_day = DayBook.query.filter_by(barber_public_id=appointment.barber_public_id, day=appointment.day,
                                     month=appointment.month, year=appointment.year).first()
    if not my_day:
        return jsonify({'message': 'This barber not available at this day!'})

    for i in range(num_of_time_cycle):
        str1 = temp_time.strftime("%H:%M")
        updateTime(str1, my_day, False)
        temp_time = temp_time + datetime.timedelta(minutes=15)

    db.session.delete(appointment)
    db.session.commit()
    return jsonify({'message': 'The appointment has been deleted! ' + 'User public id:' + appointment.user_public_id})

