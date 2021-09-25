from flask import Blueprint, request, jsonify, current_app
from database import db
import base64
from PIL import Image
import io

from request.user import token_required

user_images_bp = Blueprint('account_api_user_images', __name__)


class UserImages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String(80))
    user_public_id = db.Column(db.String(50))
    description = db.Column(db.String(250))


def allowed_image(filename):
    if not '.' in filename:
        return False

    ext = filename.rsplit('.', 1)[1]

    if ext.upper() in current_app.config['ALLOWED_FORMAT']:
        return True
    else:
        return False


@user_images_bp.route('/userImage', methods=['POST'])
@token_required
def add_image(current_user):
    data = request.get_json()
    file_name = current_user.public_id + '.jpeg'
    images = UserImages.query.all()
    for one_image in images:
        if one_image.user_public_id == current_user.public_id:
            image = base64.b64decode(str(data['image']))
            image_path = (current_app.config['USER_IMAGE_UPLOAD_PATH'] + file_name)
            img = Image.open(io.BytesIO(image))
            img.save(image_path, 'jpeg')
            one_image.image_name = file_name
            db.session.commit()
            return jsonify({'message': 'Profile image has been changed!'})
    if not allowed_image(file_name):
        return jsonify({'message': 'Image format not allowed'})

    image = base64.b64decode(str(data['image']))
    image_path = (current_app.config['USER_IMAGE_UPLOAD_PATH'] + file_name)
    img = Image.open(io.BytesIO(image))
    img.save(image_path, 'jpeg')

    new_user_image = UserImages(user_public_id=current_user.public_id, image_name=file_name,
                                description=data['description'])
    db.session.add(new_user_image)
    db.session.commit()
    return jsonify({'message': 'New image added!'})


@user_images_bp.route('/userImage', methods=['GET'])
@token_required
def get_user_profile_images(current_user):
    image = UserImages.query.filter_by(user_public_id=current_user.public_id).first()
    if not image:
        return jsonify({'message': 'This user still not upload an image!'})

    output = []
    with open(current_app.config['USER_IMAGE_UPLOAD_PATH'] + image.image_name, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    image_data = {}
    image_data['image'] = str(encoded_string)
    image_data['description'] = image.description
    output.append(image_data)
    return jsonify(output)
