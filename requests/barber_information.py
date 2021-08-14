from flask import Blueprint
from flask import request, jsonify
from database import db
from requests.user import token_required
from requests.dayBook import DayBook, updateTime
import datetime

barber_information_bp = Blueprint('account_api_barber_information', __name__)


class BarberInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    barber_public_id = db.Column(db.String(50))
    phone_num = db.Column(db.String(20))
    address = db.Column(db.String(100))
    days_for_daybook = db.Column(db.Integer)


class OpenHours(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    barber_public_id = db.Column(db.String(50))
    monday_open = db.Column(db.String(50))
    tuesday_open = db.Column(db.String(50))
    wednesday_open = db.Column(db.String(50))
    thursday_open = db.Column(db.String(50))
    friday_open = db.Column(db.String(50))
    saturday_open = db.Column(db.String(50))
    sunday_open = db.Column(db.String(50))
    monday_close = db.Column(db.String(50))
    tuesday_close = db.Column(db.String(50))
    wednesday_close = db.Column(db.String(50))
    thursday_close = db.Column(db.String(50))
    friday_close = db.Column(db.String(50))
    saturday_close = db.Column(db.String(50))
    sunday_close = db.Column(db.String(50))


@barber_information_bp.route('/addBarberInfo', methods=['POST'])
@token_required
def create_info(current_barber):
    data = request.get_json()

    # initialize barber information
    new_barber_info = BarberInfo(barber_public_id=current_barber.public_id, phone_num=data[0]['phone_num'],
                                 address=data[3]['address'], days_for_daybook=data[4]['days_for_daybook'])
    db.session.add(new_barber_info)
    db.session.commit()

    # initialize barber open hours
    a = ','.join(data[1]['open_hour'][1])
    new_barber_open_hours = OpenHours(barber_public_id=current_barber.public_id,
                                      monday_open=toString(data[1]['open_hour'][0]),
                                      tuesday_open=toString(data[1]['open_hour'][1]),
                                      wednesday_open=toString(data[1]['open_hour'][2]),
                                      thursday_open=toString(data[1]['open_hour'][3]),
                                      friday_open=toString(data[1]['open_hour'][4]),
                                      saturday_open=toString(data[1]['open_hour'][5]),
                                      sunday_open=toString(data[1]['open_hour'][6]),
                                      monday_close=toString(data[2]['close_hour'][0]),
                                      tuesday_close=toString(data[2]['close_hour'][1]),
                                      wednesday_close=toString(data[2]['close_hour'][2]),
                                      thursday_close=toString(data[2]['close_hour'][3]),
                                      friday_close=toString(data[2]['close_hour'][4]),
                                      saturday_close=toString(data[2]['close_hour'][5]),
                                      sunday_close=toString(data[2]['close_hour'][6]))
    db.session.add(new_barber_open_hours)
    db.session.commit()

    creation_time = datetime.datetime.now()
    day = creation_time.weekday()
    temp_time = creation_time + datetime.timedelta(hours=24)
    open_hour = data[1]['open_hour']
    close_hour = data[2]['close_hour']
    # create week
    for i in range(data[4]['days_for_daybook']):
        new_day = DayBook(barber_public_id=current_barber.public_id, day=(temp_time.day + i), month=temp_time.month,
                          year=temp_time.year)
        db.session.add(new_day)
        # create one day
        length = 0
        place = ((i + day + 1) % 7)
        if open_hour[place] != None:
            length = len(open_hour[place])

        for j in range(length):
            open1 = datetime.datetime.strptime(open_hour[place][j], '%H:%M')
            temp_time = temp_time.replace(minute=open1.minute, hour=open1.hour, second=0, microsecond=0)
            end = datetime.datetime.strptime(close_hour[place][j], '%H:%M')
            end_time = temp_time.replace(minute=end.minute, hour=end.hour, second=0, microsecond=0)
            while temp_time != end_time:
                str1 = temp_time.strftime("%H:%M")
                updateTime(str1, new_day, False)
                temp_time = temp_time + datetime.timedelta(minutes=15)

    return jsonify({'message': 'Information saved !'})


# change !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@barber_information_bp.route('/getBarberInfo', methods=['GET'])
@token_required
def get_barber_info(current_barber):
    barbers = BarberInfo.query.all()
    output = []

    for barber in barbers:
        if barber.barber_public_id == current_barber.public_id:
            barber_data = {}
            barber_data['barber_public_id'] = barber.barber_public_id
            barber_data['phone_num'] = barber.phone_num
            barber_data['open_hour'] = barber.open_hour
            barber_data['close_hour'] = barber.close_hour
            barber_data['address'] = barber.address
            output.append(barber_data)
            break

    return jsonify({'barber info:': output})


def toString(list1):
    if list1 is not None:
        return ','.join(list1)
    else:
        return None
