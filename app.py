from threading import Thread

from flask import Flask
from database import db
from request.appointment import appointment_bp
from request.barber_images import barber_images_bp
from request.notification import notification_bp, check_every_user_notification, auto_func_for_notification
from request.notification_counter import notification_counter_bp
from request.user import user_bp
from request.barber import barber_bp
from request.favorites import favorite_bp
from request.barber_information import barber_information_bp
from request.barber_haircut_types import barber_haircut_bp
from request.dayBook import daybook_bp
from request.rating import rating_bp
from request.user_images import user_images_bp

app = Flask(__name__)


def create_app():
    app.config['IP'] = '0.0.0.0'
    app.config['SECRET_KEY'] = 'this_is_secret'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:04030403@localhost/users_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['BARBER_IMAGE_UPLOAD_PATH'] = '/Users/oriel/PycharmProjects/finalProject/barber_uploads'
    app.config['USER_IMAGE_UPLOAD_PATH'] = '/Users/oriel/PycharmProjects/finalProject/user_uploads/'
    app.config['BARBER_PROFILE_IMAGE_PATH'] = '/Users/oriel/PycharmProjects/finalProject/barber_profile_images/'
    app.config['ALLOWED_FORMAT'] = ['PNG', 'JPG', 'JPEG', 'GIF']
    db.init_app(app)
    app.register_blueprint(user_bp, url_prefix='')
    app.register_blueprint(barber_bp, url_prefix='')
    app.register_blueprint(favorite_bp, url_prefix='')
    app.register_blueprint(appointment_bp, url_prefix='')
    app.register_blueprint(barber_information_bp, url_prefix='')
    app.register_blueprint(barber_haircut_bp, url_prefix='')
    app.register_blueprint(daybook_bp, url_prefix='')
    app.register_blueprint(rating_bp, url_prefix='')
    app.register_blueprint(barber_images_bp, url_prefix='')
    app.register_blueprint(user_images_bp, url_prefix='')
    app.register_blueprint(notification_bp, url_prefix='')
    app.register_blueprint(notification_counter_bp, url_prefix='')
    return app


def setup_database(app):
    with app.app_context():
        db.create_all()


if __name__ == "__main__":
    app = create_app()
    setup_database(app)
    thread = Thread(target=auto_func_for_notification)
    thread.start()
    app.run(host=app.config['IP'], debug=True)

