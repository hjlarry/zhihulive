import os


class Config:
    SECRET_KEY = 'flask+mongoengine=<3'
    BABEL_DEFAULT_LOCALE = 'zh_CN'
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    @staticmethod
    def init_app(app):
        pass


REDIS_URL = 'redis://'+ os.environ.get('REDIS_HOST', '127.0.0.1') \
            + ':' + os.environ.get('REDIS_PORT', '6739') + '/' + os.environ.get('REDIS_DB', '10')


class DevelopmentConfig(Config):
    DEBUG = True
    MONGODB_SETTINGS = {
        'db': os.environ.get('DATABASE_DB', 'danery'),
        'host': os.environ.get('DATABASE_HOST', '127.0.0.1'),
        'port': int(os.environ.get('DATABASE_PORT', 27017)),
        'connect': False
    }
    # REDIS_CONF = {
    #     'host': '127.0.0.1',
    #     'password': 'root',
    #     'port': 6379,
    #     'broker_db': 10,
    #     'backend_db': 10
    # }
    CELERY_IMPORTS = ('app.tasks',)
    BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    CELERY_TIMEZONE = 'Asia/Shanghai'
    CELERY_ENABLE_UTC = True
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TASK_RESULT_EXPIRES = 60 * 60 * 4
    CELERY_ACCEPT_CONTENT = ['json']


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


LOGIN_URL = 'https://www.zhihu.com/#signin'
MYLIVE_URL = 'https://api.zhihu.com/people/self/lives'
LIVECONTENT_URL = 'https://api.zhihu.com/lives/{}/messages?chronology=desc&before_id={}'


BAIDU_API_KEY = 'Ud81kSVTD864enzE0dR6oMXm'
BAIDU_SECRET_KEY = 'p1PIZsLVbvBGZo0Twt3ZF1W46cep9XZq'
BAIDU_TOKEN_URL = 'https://openapi.baidu.com/oauth/2.0/token'
BAIDU_SERVER_URL = 'http://vop.baidu.com/server_api'

