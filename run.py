from app import create_app, celery
from flask_script import Manager

my_app = create_app('default')
my_app.app_context().push()
manager = Manager(my_app)


if __name__ == '__main__':

    # Start app
    manager.run()


