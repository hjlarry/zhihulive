from flask import Flask, redirect, request, g, render_template

from flask_debugtoolbar import DebugToolbarExtension
from flask_babelex import Babel
from flask_mongoengine import MongoEngine
from flask_admin import Admin
from flask_script import Manager


# from crawl import Crawl
# from admin_index_view import MyAdminIndexView

db = MongoEngine()
admin = Admin(name='Manage Your ZhihuLive', template_mode='bootstrap3')
babel = Babel()

def create_app():
    app = Flask(__name__, static_folder='Resource')

    app.config.from_object(__name__)
    app.config['MONGODB_SETTINGS'] = {'DB': 'zhihulive'}
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'flask+mongoengine=<3'
    app.debug = True
    app.config['DEBUG_TB_PANELS'] = (
        'flask_debugtoolbar.panels.versions.VersionDebugPanel',
        'flask_debugtoolbar.panels.timer.TimerDebugPanel',
        'flask_debugtoolbar.panels.headers.HeaderDebugPanel',
        'flask_debugtoolbar.panels.request_vars.RequestVarsDebugPanel',
        'flask_debugtoolbar.panels.template.TemplateDebugPanel',
        'flask_debugtoolbar.panels.logger.LoggingPanel',
        'flask_mongoengine.panels.MongoDebugPanel'
    )
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    app.config['BABEL_DEFAULT_LOCALE'] = 'zh_CN'

    db.init_app(app)
    babel.init_app(app)
    admin.init_app(app)

    from administrator import admin_blueprint
    app.register_blueprint(admin_blueprint)


    return app
# administrator = Admin(app, 'Manage Your ZhihuLive', index_view=MyAdminIndexView(), template_mode='bootstrap3')





# Flask administrator
# @app.route('/')
# def index():
#     return redirect('/administrator/', code=302)


# @app.route('/zhihulogin', methods=['POST'])
# def zhihu_login():
#     global current
#     # g.current = Crawl()
#     current = Crawl()
#     username = request.form['username']
#     password = request.form['password']
#     current.login(username, password)
#     return redirect('/administrator/main', code=302)


# @app.route('/crawl_live_list')
# def crawl_live_list():
#     try:
#         current.live_list_work()
#     except Exception as e:
#         return e
#     else:
#         return 'SUCCESS'
#
#
# @app.route('/administrator/crawl_live/<id>')
# def crawl(id):
#     try:
#         current.live_content_work(id)
#     except Exception as e:
#         return e
#     else:
#         return 'SUCCESS'

manager = Manager(create_app())


if __name__ == '__main__':

    # Start app
    manager.run()

