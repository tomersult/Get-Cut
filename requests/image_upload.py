import os
from flask import Blueprint, request, jsonify, current_app, send_file
from werkzeug.utils import secure_filename
from database import db
from requests.user import token_required

image_bp = Blueprint('account_api_image', __name__)


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String(80))
    user_public_id = db.Column(db.String(50))
    main = db.Column(db.Boolean)
    path = db.Column(db.String(80))


def allowed_image(filename):
    if not '.' in filename:
        return False

    ext = filename.rsplit('.', 1)[1]

    if ext.upper() in current_app.config['ALLOWED_FORMAT']:
        return True
    else:
        return False


@image_bp.route('/upload/<boolean>', methods=['POST'])
@token_required
def upload(current_user, boolean):
    my_bool = False
    if boolean == 'True':
        my_bool = True
    image_req = request.files['image']
    if image_req.filename == "":
        return jsonify({'message': 'Image must have filename'})

    if not allowed_image(image_req.filename):
        return jsonify({'message': 'Image format not allowed'})
    else:
        filename = secure_filename(image_req.filename)

    image_req.save(os.path.join(current_app.config['IMAGE_UPLOAD_PATH'], filename))

    current_app.config['IMAGE_UPLOAD_PATH']

    new_image = Image(image_name=filename, path=current_app.config['IMAGE_UPLOAD_PATH'],
                      user_public_id=current_user.public_id, main=my_bool)

    db.session.add(new_image)
    db.session.commit()

    return jsonify({'message': 'Image uploaded'})


@image_bp.route('/images/<image_name_req>', methods=['GET'])
def get_image(image_name_req):
    images = Image.query.all()
    for image in images:
        if image.image_name == image_name_req:
            image_path = image.path

    path = image_path + '/' + image_name_req

    return send_file(path)


@image_bp.route('/images', methods=['GET'])
@token_required
def get_image_by_user_id(current_user):
    images = Image.query.all()
    output = []
    for image in images:
        if image.user_public_id == current_user.public_id:
            image_data = {}
            image_data['image_name'] = image.image_name
            image_data['path'] = image.path
            image_data['user_public_id'] = image.user_public_id
            image_data['main'] = image.main
            output.append(image_data)

    return jsonify({'images': output})
