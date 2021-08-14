from flask import Flask
from database import db
from requests.appointment import appointment_bp
from requests.image_upload import image_bp
from requests.user import user_bp
from requests.barber import barber_bp
from requests.favorites import favorite_bp
from requests.barber_information import barber_information_bp
from requests.barber_haircut_types import barber_haircut_bp
from requests.dayBook import daybook_bp

app = Flask(__name__)


def create_app():
    app.config['IP'] = '127.0.0.1'
    app.config['SECRET_KEY'] = 'this_is_secret'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:1234@localhost/users_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['IMAGE_UPLOAD_PATH'] = 'C:/Users/tomer/PycharmProjects/finalProject/uploads'
    app.config['ALLOWED_FORMAT'] = ['PNG', 'JPG', 'JPEG', 'GIF']
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:1234@localhost/users_db'
    db.init_app(app)
    app.register_blueprint(image_bp, url_prefix='')
    app.register_blueprint(user_bp, url_prefix='')
    app.register_blueprint(barber_bp, url_prefix='')
    app.register_blueprint(favorite_bp, url_prefix='')
    app.register_blueprint(appointment_bp, url_prefix='')
    app.register_blueprint(barber_information_bp, url_prefix='')
    app.register_blueprint(barber_haircut_bp, url_prefix='')
    app.register_blueprint(daybook_bp, url_prefix='')
    return app


def setup_database(app):
    with app.app_context():
        db.create_all()


if __name__ == "__main__":
    app = create_app()
    setup_database(app)
    app.run(host=app.config['IP'], debug=True)
