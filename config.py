class Config:
    SECRET_KEY = 'flask+mongoengine=<3'
    BABEL_DEFAULT_LOCALE = 'zh_CN'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    MONGODB_SETTINGS = {
        'db': 'zhihulive',
        'host': '127.0.0.1',
        'port': 27017,
        'connect': False
    }
    REDIS_CONF = {
        'host': '127.0.0.1',
        'password': 'root',
        'port': 6379,
        'broker_db': 10,
        'backend_db': 10
    }
    CELERY_IMPORTS = ('app.tasks',)
    BROKER_URL = 'redis://127.0.0.1:6379/10'
    CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/10'
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

