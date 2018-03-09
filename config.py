import os


class Config:
    SECRET_KEY = 'flask+mongoengine=<3'
    BABEL_DEFAULT_LOCALE = 'zh_CN'
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    MONGODB_SETTINGS = {
        'db': os.environ.get('DATABASE_DB', 'zhihulive'),
        'host': os.environ.get('DATABASE_HOST', '127.0.0.1'),
        'port': int(os.environ.get('DATABASE_PORT', 27017)),
        'connect': False
    }


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
