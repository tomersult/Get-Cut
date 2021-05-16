import os
from flask import Blueprint, request, jsonify,current_app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from database import db


app_image = Blueprint('account_api', __name__)


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String(80))
    path = db.Column(db.String(80))


def allowed_image(filename):
    if not '.' in filename:
        return False

    ext = filename.rsplit('.', 1)[1]

    if ext.upper() in current_app.config['ALLOWED_FORMAT']:
        return True
    else:
        return False


@app_image.route('/upload', methods=['POST'])
def upload():
    image_req = request.files['image']
    if image_req.filename == "":
        return jsonify({'message' : 'Image must have filename'})

    if not allowed_image(image_req.filename):
        return jsonify({'message' : 'Image format not allowed'})
    else:
        filename = secure_filename(image_req.filename)

    image_req.save(os.path.join(current_app.config['IMAGE_UPLOAD_PATH'],filename))

    current_app.config['IMAGE_UPLOAD_PATH']

    new_image = Image(image_name=filename, path=current_app.config['IMAGE_UPLOAD_PATH'])

    db.session.add(new_image)
    db.session.commit()

    return jsonify({'message' : 'Image uploaded'})

@app_image.route("/test",methods=['GET'])
def hello():
    return "Hello World!"