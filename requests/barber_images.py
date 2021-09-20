from requests.barber import barber_token_required
from flask import Blueprint, request, jsonify, current_app
from database import db
import base64
from PIL import Image
import io

barber_images_bp = Blueprint('account_api_barber_images', __name__)


class BarberImages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String(80))
    barber_public_id = db.Column(db.String(50))
    description = db.Column(db.String(250))
    profile = db.Column(db.Boolean, unique=False, default=False)


def allowed_image(filename):
    if not '.' in filename:
        return False

    ext = filename.rsplit('.', 1)[1]

    if ext.upper() in current_app.config['ALLOWED_FORMAT']:
        return True
    else:
        return False


@barber_images_bp.route('/barberImages', methods=['POST'])
@barber_token_required
def add_image(current_barber):
    data = request.get_json()
    file_name = data['image_name']
    images = BarberImages.query.all()
    for one_image in images:
        if one_image.image_name == file_name:
            return jsonify({'message': 'Change image name !'})
    if not allowed_image(file_name):
        return jsonify({'message': 'Image format not allowed'})

    image = base64.b64decode(str(data['image']))
    image_path = (current_app.config['BARBER_IMAGE_UPLOAD_PATH'] + file_name)
    img = Image.open(io.BytesIO(image))
    img.save(image_path, 'jpeg')

    new_barber_image = BarberImages(barber_public_id=current_barber.public_id, image_name=file_name,
                                    description=data['description'], profile=data['profile'])
    db.session.add(new_barber_image)
    db.session.commit()
    return jsonify({'message': 'New image added!'})


@barber_images_bp.route('/barberImages', methods=['GET'])
@barber_token_required
def get_all_barber_images(current_barber):
    images = BarberImages.query.filter_by(barber_public_id=current_barber.public_id).all()
    if not images:
        return jsonify({'message': 'This barber still not upload an image!'})

    output = []
    for one_image in images:
        with open(current_app.config['BARBER_IMAGE_UPLOAD_PATH'] + one_image.image_name, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
        image_data = {}
        image_data['image'] = str(encoded_string)
        image_data['description'] = one_image.description
        image_data['profile'] = one_image.profile
        image_data['image_name'] = one_image.image_name
        output.append(image_data)
    return jsonify(output)


