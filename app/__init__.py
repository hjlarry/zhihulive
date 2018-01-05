from flask import Flask, redirect
from flask_babelex import Babel
from flask_mongoengine import MongoEngine
from flask_admin import Admin
from flask_debugtoolbar import DebugToolbarExtension
from config import config, REDIS_URL
from celery import Celery

from redis import Redis
redis = Redis(host='redis-server', port=6379, db=5)


db = MongoEngine()
babel = Babel()
debugbar = DebugToolbarExtension()
admin = Admin(name='Manage Your ZhihuLive', template_mode='bootstrap3')
celery = Celery('celery', broker=REDIS_URL, include=['app.tasks'])



def create_app(config_name):
    app = Flask(__name__, static_folder='Resource')
    app.config.from_object(config[config_name])

    db.init_app(app)
    babel.init_app(app)
    admin.init_app(app)
    debugbar.init_app(app)
    celery.conf.update(app.config)


    @app.route('/')
    def index():
        return redirect('/admin/', code=302)

    @app.route('/redis')
    def hello():
        redis.incr('hits')
        redis.set('jajaja', '1111')
        return 'Hello World! I have been seen %s times.' % redis.get('hits')

    from .administrator import admin_blueprint
    app.register_blueprint(admin_blueprint)

    return app




