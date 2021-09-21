from flask import Blueprint
from flask import request, jsonify
from database import db
from requests.barber import barber_token_required
from requests.user import token_required
from requests.dayBook import DayBook, updateTime
import datetime

barber_information_bp = Blueprint('account_api_barber_information', __name__)


class BarberInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    barber_public_id = db.Column(db.String(50))
    phone_num = db.Column(db.String(20))
    location = db.Column(db.String(100))
    sentence = db.Column(db.String(500))
    headline = db.Column(db.String(50))


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
@barber_token_required
def create_info(current_barber):
    data = request.get_json()

    # initialize barber information
    new_barber_info = BarberInfo(barber_public_id=current_barber.public_id, phone_num=data[0]['phone_num'],
                                 location=data[3]['location'], sentence=data[4]['sentence']
                                 , headline=data[5]['headline'])
    db.session.add(new_barber_info)
    db.session.commit()

    # initialize barber open hours
    a = ','.join(data[1]['open_hour'][1])
    new_barber_open_hours = OpenHours(barber_public_id=current_barber.public_id,
                                      sunday_open=toString(data[1]['open_hour'][0]),
                                      monday_open=toString(data[1]['open_hour'][1]),
                                      tuesday_open=toString(data[1]['open_hour'][2]),
                                      wednesday_open=toString(data[1]['open_hour'][3]),
                                      thursday_open=toString(data[1]['open_hour'][4]),
                                      friday_open=toString(data[1]['open_hour'][5]),
                                      saturday_open=toString(data[1]['open_hour'][6]),
                                      sunday_close=toString(data[2]['close_hour'][0]),
                                      monday_close=toString(data[2]['close_hour'][1]),
                                      tuesday_close=toString(data[2]['close_hour'][2]),
                                      wednesday_close=toString(data[2]['close_hour'][3]),
                                      thursday_close=toString(data[2]['close_hour'][4]),
                                      friday_close=toString(data[2]['close_hour'][5]),
                                      saturday_close=toString(data[2]['close_hour'][6]))
    db.session.add(new_barber_open_hours)
    db.session.commit()

    creation_time = datetime.datetime.now()
    day = creation_time.weekday()
    temp_time = creation_time + datetime.timedelta(hours=24)
    open_hour = data[1]['open_hour']
    close_hour = data[2]['close_hour']
    # create days in daybook (the barber chose how much)
    for i in range(14):
        new_day = DayBook(barber_public_id=current_barber.public_id, day=(temp_time.day + i), month=temp_time.month,
                          year=temp_time.year)
        db.session.add(new_day)
        db.session.commit()
        # create one day
        length = 0
        place = ((i + day + 2) % 7)
        if open_hour[place] is not None:
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


@barber_information_bp.route('/getBarberInfo', methods=['GET'])
@barber_token_required
def get_barber_info(current_barber):
    barber = BarberInfo.query.filter_by(barber_public_id=current_barber.public_id).first()
    if not barber:
        return jsonify({'message': 'This barber did not fill information yet!'})

    all_open_hours = OpenHours.query.filter_by(barber_public_id=current_barber.public_id).first()
    open_hours, close_hours = string_to_list(all_open_hours)

    summary = {}
    barber_data = {}
    barber_data['phone_num'] = barber.phone_num
    barber_data['open_hour'] = open_hours
    barber_data['close_hour'] = close_hours
    summary['sentence'] = barber.sentence
    summary['headline'] = barber.headline
    barber_data['summary'] = summary
    barber_data['location'] = barber.location

    return jsonify(barber_data)


@barber_information_bp.route('/daybookPlusDay', methods=['PUT'])
# every day we open one more day for each barber
def daybook_plus_day():
    data = request.get_json()
    creation_time = datetime.datetime.now()
    barbers = BarberInfo.query.all()
    if not barbers:
        return jsonify({'message': 'There is no barber yet!'})

    for barber in barbers:
        open_hours = OpenHours.query.filter_by(barber_public_id=barber.barber_public_id).first()
        # the number of the day in open_hours table
        open_day_num = ((((datetime.datetime.now().weekday() + barber.days_for_daybook) % 7) + 1) % 7)
        close_day_num = open_day_num + 7
        my_day_time = creation_time + datetime.timedelta(days=barber.days_for_daybook + 1)
        new_day = DayBook(barber_public_id=barber.barber_public_id,
                          day=str(creation_time.day + barber.days_for_daybook + 1),
                          month=my_day_time.month,
                          year=my_day_time.year)
        db.session.add(new_day)

        my_day_open_hours, my_day_close_hours = get_my_day_open_hours(open_day_num, open_hours)
        if my_day_open_hours is not None:
            length = len(my_day_open_hours)

        for j in range(length):
            open1 = datetime.datetime.strptime(my_day_open_hours[j], '%H:%M')
            my_day_time = my_day_time.replace(minute=open1.minute, hour=open1.hour, second=0, microsecond=0)
            end = datetime.datetime.strptime(my_day_close_hours[j], '%H:%M')
            end_time = my_day_time.replace(minute=end.minute, hour=end.hour, second=0, microsecond=0)
            while my_day_time != end_time:
                str1 = my_day_time.strftime("%H:%M")
                updateTime(str1, new_day, False)
                my_day_time = my_day_time + datetime.timedelta(minutes=15)

    return jsonify({'message': 'new day has been added to all barbers'})


def toString(list1):
    if list1 is not None:
        return ','.join(list1)
    else:
        return None


def string_to_list(all_open_hours):
    open_hours = [my_split(all_open_hours.monday_open), my_split(all_open_hours.tuesday_open),
                  my_split(all_open_hours.wednesday_open), my_split(all_open_hours.thursday_open),
                  my_split(all_open_hours.friday_open), my_split(all_open_hours.saturday_open),
                  my_split(all_open_hours.sunday_open)]
    close_hours = [my_split(all_open_hours.monday_close), my_split(all_open_hours.tuesday_close),
                   my_split(all_open_hours.wednesday_close), my_split(all_open_hours.thursday_close),
                   my_split(all_open_hours.friday_close), my_split(all_open_hours.saturday_close),
                   my_split(all_open_hours.sunday_close)]
    return open_hours, close_hours


def my_split(str1):
    if str1 is not None:
        return str1.split(',')
    else:
        return None


def get_my_day_open_hours(day_num, open_hours):
    if day_num == 0:
        my_day_open = open_hours.monday_open
        my_day_close = open_hours.monday_close
    if day_num == 1:
        my_day_open = open_hours.tuesday_open
        my_day_close = open_hours.tuesday_close
    if day_num == 2:
        my_day_open = open_hours.wednesday_open
        my_day_close = open_hours.wednesday_close
    if day_num == 3:
        my_day_open = open_hours.thursday_open
        my_day_close = open_hours.thursday_close
    if day_num == 4:
        my_day_open = open_hours.friday_open
        my_day_close = open_hours.friday_close
    if day_num == 5:
        my_day_open = open_hours.saturday_open
        my_day_close = open_hours.saturday_close
    if day_num == 6:
        my_day_open = open_hours.sunday_open
        my_day_close = open_hours.sunday_close

    return my_split(my_day_open), my_split(my_day_close)
