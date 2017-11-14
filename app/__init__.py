from flask import Flask, redirect
from flask_babelex import Babel
from flask_mongoengine import MongoEngine
from flask_admin import Admin
from config import config
from celery import Celery

db = MongoEngine()
babel = Babel()
admin = Admin(name='Manage Your ZhihuLive', template_mode='bootstrap3')
celery = Celery('celery', broker='redis://127.0.0.1:6379/10', include=['app.tasks'])



def create_app(config_name):
    app = Flask(__name__, static_folder='Resource')
    app.config.from_object(config[config_name])

    db.init_app(app)
    babel.init_app(app)
    admin.init_app(app)
    celery.conf.update(app.config)


    @app.route('/')
    def index():
        return redirect('/admin/', code=302)

    from .administrator import admin_blueprint
    app.register_blueprint(admin_blueprint)

    return app




