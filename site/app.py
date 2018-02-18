import os
from flask import Flask
from flask.sessions import SessionInterface
from beaker.middleware import SessionMiddleware
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy_session import flask_scoped_session


session_opts = {
    'session.type': 'ext:memcached',
    'session.url': '127.0.0.1:11211',
    'session.data_dir': './cache',
}


class BeakerSessionInterface(SessionInterface):
    def open_session(self, app, request):
        session = request.environ['beaker.session']
        return session

    def save_session(self, app, session, response):
        session.save()


def index_work_db():
    from models import Table, Column


# # application factory, see: http://flask.pocoo.org/docs/patterns/appfactories/
# def create_app(config_filename):
#     app = Flask(__name__)
#     app.config.from_object(config_filename)
#
#     # app.wsgi_app = SessionMiddleware(app.wsgi_app, session_opts)
#     # app.session_interface = BeakerSessionInterface()
#     # SQLAlchemy
#     db = SQLAlchemy(app)
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#
#     # import blueprints
#     from pages.views import pages_app
#
#     # register blueprints
#     app.register_blueprint(pages_app)
#
#     return app, db

app = Flask(__name__)
try:
    app_settings = os.environ['APP_SETTINGS']
except KeyError:
    app_settings = 'settings.DevelopmentConfig'
app.config.from_object(app_settings)

# Backer session
if int(os.environ.get('RUN_MIGRATION', 0)) == 0:
    app.wsgi_app = SessionMiddleware(app.wsgi_app, session_opts)
    app.session_interface = BeakerSessionInterface()

# SQLAlchemy
db = SQLAlchemy(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

index_work_db()

# import & register blueprints
from pages.views import pages_app
app.register_blueprint(pages_app)

# engine = create_engine("postgresql://luckyreportuser:luckyreportuser@localhost/luckyreport")
# session_factory = sessionmaker(bind=engine)
# session = flask_scoped_session(session_factory, app)


if __name__ == "__main__":
    app.run()
