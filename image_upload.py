from flask import Blueprint, request, jsonify



app_image = Blueprint('account_api', __name__)

@app_image.route('/upload', methods=['POST'])
def upload():
    image = request.files['image']
    if image.filename == "":
        return jsonify({'message' : 'Image must have filename'})

    if not allowed_image(image.filename):
        return jsonify({'message' : 'Image format not allowed'})
    else:
        filename = secure_filename(image.filename)

    image.save(os.path.join(app.config['IMAGE_UPLOAD'],filename))

    new_image = Image(image_name=filename, path=app.config['IMAGE_UPLOAD'])

    db.session.add(new_image)
    db.session.commit()

    return jsonify({'message' : 'Image uploaded'})