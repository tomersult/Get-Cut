from flask import Blueprint
from flask import request, jsonify
from database import db
from requests.user import token_required

appointment_bp = Blueprint('appointment_api_barber', __name__)


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_public_id = db.Column(db.String(50))
    barber_public_id = db.Column(db.String(50))
    start = db.Column(db.String(50))
    end = db.Column(db.String(50))
    haircut_type = db.Column(db.String(50))
    comments = db.Column(db.String(500))


@appointment_bp.route('/appointment', methods=['POST'])
@token_required
def create_appointment(current_user):
    data = request.get_json()

    new_appointment = Appointment(user_public_id=current_user.public_id, barber_public_id=data['barber_public_id'],
                                  start=data['start'], end=data['end'], haircut_type=data['haircut_type'],
                                  comments=data['comments'])
    db.session.add(new_appointment)
    db.session.commit()

    return jsonify({'message': 'New appointment created!'})


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
    appointments = Appointment.query.filter_by(user_public_id=data['user_public_id']).all()
    for appointment in appointments:
        if (appointment.start == data['start']) & (appointment.end == data['end']) & (
                appointment.barber_public_id == data['barber_public_id']):
            db.session.delete(appointment)
            db.session.commit()
            return jsonify({'message': 'The appointment has been deleted!'})
    return jsonify({'message': 'Did not find this appointment!'}), 401
