from flask import Blueprint
from flask import request, jsonify
from database import db
from requests.user import token_required

barber_haircut_bp = Blueprint('account_api_barber_haircut', __name__)


class BarberHairCut(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    barber_public_id = db.Column(db.String(50))
    name = db.Column(db.String(50))
    time = db.Column(db.String(20))
    price = db.Column(db.String(20))
    sex = db.Column(db.String(20))


@barber_haircut_bp.route('/addHairCut', methods=['POST'])
@token_required
def create(current_barber):
    data = request.get_json()
    new_barber_haircut = BarberHairCut(barber_public_id=current_barber.public_id, name=data['name'],
                                       time=data['time'], price=data['price'], sex=data['sex'])
    db.session.add(new_barber_haircut)
    db.session.commit()

    return jsonify({'message': 'Haircut saved !'})


@barber_haircut_bp.route('/getMaleHairCut', methods=['GET'])
@token_required
def get_male_haircut(current_barber):
    haircuts = BarberHairCut.query.all()
    output = []

    for haircut in haircuts:
        if current_barber.public_id == haircut.barber_public_id:
            if haircut.sex == "male":
                haircuts = {}
                haircuts['barber_public_id'] = haircut.barber_public_id
                haircuts['name'] = haircut.name
                haircuts['time'] = haircut.time
                haircuts['price'] = haircut.price
                haircuts['sex'] = haircut.sex
                output.append(haircuts)

    return jsonify(output)


@barber_haircut_bp.route('/getFemaleHairCut', methods=['GET'])
@token_required
def get_female_haircut(current_barber):
    haircuts = BarberHairCut.query.all()
    output = []

    for haircut in haircuts:
        if current_barber.public_id == haircut.barber_public_id:
            if haircut.sex == "female":
                haircuts = {}
                haircuts['barber_public_id'] = haircut.barber_public_id
                haircuts['name'] = haircut.name
                haircuts['time'] = haircut.time
                haircuts['price'] = haircut.price
                haircuts['sex'] = haircut.sex
                output.append(haircuts)

    return jsonify(output)


@barber_haircut_bp.route('/getAllHairCut', methods=['GET'])
@token_required
def get_all_haircut(current_barber):
    haircuts = BarberHairCut.query.filter_by(barber_public_id=current_barber.public_id).all()
    male_output = []
    female_output = []

    for haircut in haircuts:
        if current_barber.public_id == haircut.barber_public_id:
            if haircut.sex == 'male':
                haircuts = {}
                haircuts['barber_public_id'] = haircut.barber_public_id
                haircuts['name'] = haircut.name
                haircuts['time'] = haircut.time
                haircuts['price'] = haircut.price
                male_output.append(haircuts)
            if haircut.sex == 'female':
                haircuts = {}
                haircuts['barber_public_id'] = haircut.barber_public_id
                haircuts['name'] = haircut.name
                haircuts['time'] = haircut.time
                haircuts['price'] = haircut.price
                female_output.append(haircuts)

    return jsonify({'male': male_output}, {'female': female_output})


@barber_haircut_bp.route('/deleteHaircut', methods=['DELETE'])
@token_required
def delete_barber(current_barber):
    data = request.get_json()
    haircuts = BarberHairCut.query.filter_by(barber_public_id=current_barber.public_id, name=data['name']).all()
    for haircut in haircuts:
        db.session.delete(haircut)
        db.session.commit()

    return jsonify({'message': 'The haircut has been deleted!'})