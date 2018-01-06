from flask import Flask, redirect
from flask_babelex import Babel
from flask_mongoengine import MongoEngine
from flask_admin import Admin
from flask_debugtoolbar import DebugToolbarExtension
from config import config


db = MongoEngine()
babel = Babel()
debugbar = DebugToolbarExtension()
admin = Admin(name='Manage Your ZhihuLive', template_mode='bootstrap3')




def create_app(config_name):
    app = Flask(__name__, static_folder='Resource')
    app.config.from_object(config[config_name])

    db.init_app(app)
    babel.init_app(app)
    admin.init_app(app)
    debugbar.init_app(app)

    @app.route('/')
    def index():
        return redirect('/admin/', code=302)

    from .administrator import admin_blueprint
    app.register_blueprint(admin_blueprint)

    return app




