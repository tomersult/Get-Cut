from flask import Blueprint
from flask import request, jsonify
from database import db
from requests.user import token_required

daybook_bp = Blueprint('appointment_api_daybook', __name__)


class DayBook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    barber_public_id = db.Column(db.String(50))
    day = db.Column(db.String(20))
    month = db.Column(db.String(20))
    year = db.Column(db.String(20))
    t7_0 = db.Column(db.Boolean, unique=False, default=True)
    t7_15 = db.Column(db.Boolean, unique=False, default=True)
    t7_30 = db.Column(db.Boolean, unique=False, default=True)
    t7_45 = db.Column(db.Boolean, unique=False, default=True)
    t8_0 = db.Column(db.Boolean, unique=False, default=True)
    t8_15 = db.Column(db.Boolean, unique=False, default=True)
    t8_30 = db.Column(db.Boolean, unique=False, default=True)
    t8_45 = db.Column(db.Boolean, unique=False, default=True)
    t9_0 = db.Column(db.Boolean, unique=False, default=True)
    t9_15 = db.Column(db.Boolean, unique=False, default=True)
    t9_30 = db.Column(db.Boolean, unique=False, default=True)
    t9_45 = db.Column(db.Boolean, unique=False, default=True)
    t10_0 = db.Column(db.Boolean, unique=False, default=True)
    t10_15 = db.Column(db.Boolean, unique=False, default=True)
    t10_30 = db.Column(db.Boolean, unique=False, default=True)
    t10_45 = db.Column(db.Boolean, unique=False, default=True)
    t11_0 = db.Column(db.Boolean, unique=False, default=True)
    t11_15 = db.Column(db.Boolean, unique=False, default=True)
    t11_30 = db.Column(db.Boolean, unique=False, default=True)
    t11_45 = db.Column(db.Boolean, unique=False, default=True)
    t12_0 = db.Column(db.Boolean, unique=False, default=True)
    t12_15 = db.Column(db.Boolean, unique=False, default=True)
    t12_30 = db.Column(db.Boolean, unique=False, default=True)
    t12_45 = db.Column(db.Boolean, unique=False, default=True)
    t13_0 = db.Column(db.Boolean, unique=False, default=True)
    t13_15 = db.Column(db.Boolean, unique=False, default=True)
    t13_30 = db.Column(db.Boolean, unique=False, default=True)
    t13_45 = db.Column(db.Boolean, unique=False, default=True)
    t14_0 = db.Column(db.Boolean, unique=False, default=True)
    t14_15 = db.Column(db.Boolean, unique=False, default=True)
    t14_30 = db.Column(db.Boolean, unique=False, default=True)
    t14_45 = db.Column(db.Boolean, unique=False, default=True)
    t15_0 = db.Column(db.Boolean, unique=False, default=True)
    t15_15 = db.Column(db.Boolean, unique=False, default=True)
    t15_30 = db.Column(db.Boolean, unique=False, default=True)
    t15_45 = db.Column(db.Boolean, unique=False, default=True)
    t16_0 = db.Column(db.Boolean, unique=False, default=True)
    t16_15 = db.Column(db.Boolean, unique=False, default=True)
    t16_30 = db.Column(db.Boolean, unique=False, default=True)
    t16_45 = db.Column(db.Boolean, unique=False, default=True)
    t17_0 = db.Column(db.Boolean, unique=False, default=True)
    t17_15 = db.Column(db.Boolean, unique=False, default=True)
    t17_30 = db.Column(db.Boolean, unique=False, default=True)
    t17_45 = db.Column(db.Boolean, unique=False, default=True)
    t18_0 = db.Column(db.Boolean, unique=False, default=True)
    t18_15 = db.Column(db.Boolean, unique=False, default=True)
    t18_30 = db.Column(db.Boolean, unique=False, default=True)
    t18_45 = db.Column(db.Boolean, unique=False, default=True)
    t19_0 = db.Column(db.Boolean, unique=False, default=True)
    t19_15 = db.Column(db.Boolean, unique=False, default=True)
    t19_30 = db.Column(db.Boolean, unique=False, default=True)
    t19_45 = db.Column(db.Boolean, unique=False, default=True)
    t20_0 = db.Column(db.Boolean, unique=False, default=True)
    t20_15 = db.Column(db.Boolean, unique=False, default=True)
    t20_30 = db.Column(db.Boolean, unique=False, default=True)
    t20_45 = db.Column(db.Boolean, unique=False, default=True)
    t21_0 = db.Column(db.Boolean, unique=False, default=True)
    t21_15 = db.Column(db.Boolean, unique=False, default=True)
    t21_30 = db.Column(db.Boolean, unique=False, default=True)
    t21_45 = db.Column(db.Boolean, unique=False, default=True)
    t22_0 = db.Column(db.Boolean, unique=False, default=True)
    t22_15 = db.Column(db.Boolean, unique=False, default=True)
    t22_30 = db.Column(db.Boolean, unique=False, default=True)
    t22_45 = db.Column(db.Boolean, unique=False, default=True)


@daybook_bp.route('/createDay', methods=['POST'])
@token_required
def create(current_barber):
    new_day = DayBook(barber_public_id=current_barber.public_id)
    db.session.add(new_day)
    db.session.commit()

    return jsonify({'message': 'New day created!'})


@daybook_bp.route('/getDayHours', methods=['GET'])
def get_hours():
    data = request.get_json()
    hours = DayBook.query.filter_by(barber_public_id=data['barber_public_id'], day=data['day'], month=data['month'],
                                    year=data['year']).first()
    if not hours:
        return jsonify({'message': 'This barber do not work in this day!'})

    output = check_availability(hours)
    return jsonify(output)


@daybook_bp.route('/updateTime', methods=['POST'])
@token_required
def update(current_barber):
    barber = DayBook.query.filter_by(barber_public_id=current_barber.public_id).first()
    barber.t7_0 = True
    db.session.commit()

    return jsonify({'message': 'New day created!'})


def check_availability(hours):
    output = []
    if hours.t7_0 is False:
        output.append('7:00-7:15')
    if hours.t7_15 is False:
        output.append('7:15-7:30')
    if hours.t7_30 is False:
        output.append('7:30-7:45')
    if hours.t7_45 is False:
        output.append('7:45-8:00')
    if hours.t8_0 is False:
        output.append('8:00-8:15')
    if hours.t8_15 is False:
        output.append('8:15-8:30')
    if hours.t8_30 is False:
        output.append('8:30-8:45')
    if hours.t8_45 is False:
        output.append('8:45-9:00')
    if hours.t9_0 is False:
        output.append('9:00-9:15')
    if hours.t9_15 is False:
        output.append('9:15-9:30')
    if hours.t9_30 is False:
        output.append('9:30-9:45')
    if hours.t9_45 is False:
        output.append('9:45-10:00')
    if hours.t10_0 is False:
        output.append('10:00-10:15')
    if hours.t10_15 is False:
        output.append('10:15-10:30')
    if hours.t10_30 is False:
        output.append('10:30-10:45')
    if hours.t10_45 is False:
        output.append('10:45-11:00')
    if hours.t11_0 is False:
        output.append('11:00-11:15')
    if hours.t11_15 is False:
        output.append('11:15-11:30')
    if hours.t11_30 is False:
        output.append('11:30-11:45')
    if hours.t11_45 is False:
        output.append('11:45-12:00')
    if hours.t12_0 is False:
        output.append('12:00-12:15')
    if hours.t12_15 is False:
        output.append('12:15-12:30')
    if hours.t12_30 is False:
        output.append('12:30-12:45')
    if hours.t12_45 is False:
        output.append('12:45-13:00')
    if hours.t13_0 is False:
        output.append('13:00-13:15')
    if hours.t13_15 is False:
        output.append('13:15-13:30')
    if hours.t13_30 is False:
        output.append('13:30-13:45')
    if hours.t13_45 is False:
        output.append('13:45-14:00')
    if hours.t14_0 is False:
        output.append('14:00-14:15')
    if hours.t14_15 is False:
        output.append('14:15-14:30')
    if hours.t14_30 is False:
        output.append('14:30-14:45')
    if hours.t14_45 is False:
        output.append('14:45-15:00')
    if hours.t15_0 is False:
        output.append('15:00-15:15')
    if hours.t15_15 is False:
        output.append('15:15-15:30')
    if hours.t15_30 is False:
        output.append('15:30-15:45')
    if hours.t15_45 is False:
        output.append('15:45-16:00')
    if hours.t16_0 is False:
        output.append('16:00-16:15')
    if hours.t16_15 is False:
        output.append('16:15-16:30')
    if hours.t16_30 is False:
        output.append('16:30-16:45')
    if hours.t16_45 is False:
        output.append('16:45-17:00')
    if hours.t17_0 is False:
        output.append('17:00-17:15')
    if hours.t17_15 is False:
        output.append('17:15-17:30')
    if hours.t17_30 is False:
        output.append('17:30-17:45')
    if hours.t17_45 is False:
        output.append('17:45-18:00')
    if hours.t18_0 is False:
        output.append('18:00-18:15')
    if hours.t18_15 is False:
        output.append('18:15-18:30')
    if hours.t18_30 is False:
        output.append('18:30-18:45')
    if hours.t18_45 is False:
        output.append('18:45-19:00')
    if hours.t19_0 is False:
        output.append('19:00-19:15')
    if hours.t19_15 is False:
        output.append('19:15-19:30')
    if hours.t19_30 is False:
        output.append('19:30-19:45')
    if hours.t19_45 is False:
        output.append('19:45-20:00')
    if hours.t20_0 is False:
        output.append('20:00-20:15')
    if hours.t20_15 is False:
        output.append('20:15-20:30')
    if hours.t20_30 is False:
        output.append('20:30-20:45')
    if hours.t20_45 is False:
        output.append('20:45-21:00')
    if hours.t21_0 is False:
        output.append('21:00-21:15')
    if hours.t21_15 is False:
        output.append('21:15-21:30')
    if hours.t21_30 is False:
        output.append('21:30-21:45')
    if hours.t21_45 is False:
        output.append('21:45-22:00')
    if hours.t22_0 is False:
        output.append('22:00-22:15')
    if hours.t22_15 is False:
        output.append('22:15-22:30')
    if hours.t22_30 is False:
        output.append('22:30-22:45')
    if hours.t22_45 is False:
        output.append('22:45-23:00')
    return output


def updateTime(str, day_book, bool1):
    if str == "7:00" or str == "07:00":
        day_book.t7_0 = bool1
        db.session.commit()
    if str == "7:15" or str == "07:15":
        day_book.t7_15 = bool1
        db.session.commit()
    if str == "7:30" or str == "07:30":
        day_book.t7_30 = bool1
        db.session.commit()
    if str == "7:45" or str == "07:45":
        day_book.t7_45 = bool1
        db.session.commit()
    if str == "8:00" or str == "08:00":
        day_book.t8_0 = bool1
        db.session.commit()
    if str == "8:15" or str == "08:15":
        day_book.t8_15 = bool1
        db.session.commit()
    if str == "8:30" or str == "08:30":
        day_book.t8_30 = bool1
        db.session.commit()
    if str == "8:45" or str == "08:45":
        day_book.t8_45 = bool1
        db.session.commit()
    if str == "9:00" or str == "09:00":
        day_book.t9_0 = bool1
        db.session.commit()
    if str == "9:15" or str == "09:15":
        day_book.t9_15 = bool1
        db.session.commit()
    if str == "9:30" or str == "09:30":
        day_book.t9_30 = bool1
        db.session.commit()
    if str == "9:45" or str == "09:45":
        day_book.t9_45 = bool1
        db.session.commit()
    if str == "10:00":
        day_book.t10_0 = bool1
        db.session.commit()
    if str == "10:15":
        day_book.t10_15 = bool1
        db.session.commit()
    if str == "10:30":
        day_book.t10_30 = bool1
        db.session.commit()
    if str == "10:45":
        day_book.t10_45 = bool1
        db.session.commit()
    if str == "11:00":
        day_book.t11_0 = bool1
        db.session.commit()
    if str == "11:15":
        day_book.t11_15 = bool1
        db.session.commit()
    if str == "11:30":
        day_book.t11_30 = bool1
        db.session.commit()
    if str == "11:45":
        day_book.t11_45 = bool1
        db.session.commit()
    if str == "12:00":
        day_book.t12_0 = bool1
        db.session.commit()
    if str == "12:15":
        day_book.t12_15 = bool1
        db.session.commit()
    if str == "12:30":
        day_book.t12_30 = bool1
        db.session.commit()
    if str == "12:45":
        day_book.t12_45 = bool1
        db.session.commit()
    if str == "13:00":
        day_book.t13_0 = bool1
        db.session.commit()
    if str == "13:15":
        day_book.t13_15 = bool1
        db.session.commit()
    if str == "13:30":
        day_book.t13_30 = bool1
        db.session.commit()
    if str == "13:45":
        day_book.t13_45 = bool1
        db.session.commit()
    if str == "14:00":
        day_book.t14_0 = bool1
        db.session.commit()
    if str == "14:15":
        day_book.t14_15 = bool1
        db.session.commit()
    if str == "14:30":
        day_book.t14_30 = bool1
        db.session.commit()
    if str == "14:45":
        day_book.t14_45 = bool1
        db.session.commit()
    if str == "15:00":
        day_book.t15_0 = bool1
        db.session.commit()
    if str == "15:15":
        day_book.t15_15 = bool1
        db.session.commit()
    if str == "15:30":
        day_book.t15_30 = bool1
        db.session.commit()
    if str == "15:45":
        day_book.t15_45 = bool1
        db.session.commit()
    if str == "16:00":
        day_book.t16_0 = bool1
        db.session.commit()
    if str == "16:15":
        day_book.t16_15 = bool1
        db.session.commit()
    if str == "16:30":
        day_book.t16_30 = bool1
        db.session.commit()
    if str == "16:45":
        day_book.t16_45 = bool1
        db.session.commit()
    if str == "17:00":
        day_book.t17_0 = bool1
        db.session.commit()
    if str == "17:15":
        day_book.t17_15 = bool1
        db.session.commit()
    if str == "17:30":
        day_book.t17_30 = bool1
        db.session.commit()
    if str == "17:45":
        day_book.t17_45 = bool1
        db.session.commit()
    if str == "18:00":
        day_book.t18_0 = bool1
        db.session.commit()
    if str == "18:15":
        day_book.t18_15 = bool1
        db.session.commit()
    if str == "18:30":
        day_book.t18_30 = bool1
        db.session.commit()
    if str == "18:45":
        day_book.t18_45 = bool1
        db.session.commit()
    if str == "19:00":
        day_book.t19_0 = bool1
        db.session.commit()
    if str == "19:15":
        day_book.t19_15 = bool1
        db.session.commit()
    if str == "19:30":
        day_book.t19_30 = bool1
        db.session.commit()
    if str == "19:45":
        day_book.t19_45 = bool1
        db.session.commit()
    if str == "20:00":
        day_book.t20_0 = bool1
        db.session.commit()
    if str == "20:15":
        day_book.t20_15 = bool1
        db.session.commit()
    if str == "20:30":
        day_book.t20_30 = bool1
        db.session.commit()
    if str == "20:45":
        day_book.t20_45 = bool1
        db.session.commit()
    if str == "21:00":
        day_book.t21_0 = bool1
        db.session.commit()
    if str == "21:15":
        day_book.t21_15 = bool1
        db.session.commit()
    if str == "21:30":
        day_book.t21_30 = bool1
        db.session.commit()
    if str == "21:45":
        day_book.t21_45 = bool1
        db.session.commit()
    if str == "22:00":
        day_book.t22_0 = bool1
        db.session.commit()
    if str == "22:15":
        day_book.t22_15 = bool1
        db.session.commit()
    if str == "22:30":
        day_book.t22_30 = bool1
        db.session.commit()
    if str == "22:45":
        day_book.t22_45 = bool1
        db.session.commit()
