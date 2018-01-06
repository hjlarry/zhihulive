import os


LOGIN_URL = 'https://www.zhihu.com/#signin'
MYLIVE_URL = 'https://api.zhihu.com/people/self/lives'
LIVECONTENT_URL = 'https://api.zhihu.com/lives/{}/messages?chronology=desc&before_id={}'


BAIDU_API_KEY = 'Ud81kSVTD864enzE0dR6oMXm'
BAIDU_SECRET_KEY = 'p1PIZsLVbvBGZo0Twt3ZF1W46cep9XZq'
BAIDU_TOKEN_URL = 'https://openapi.baidu.com/oauth/2.0/token'
BAIDU_SERVER_URL = 'http://vop.baidu.com/server_api'


# REDIS_URL = 'redis://'+ os.environ.get('REDIS_HOST', '127.0.0.1') \
#             + ':' + os.environ.get('REDIS_PORT', '6739') + '/' + os.environ.get('REDIS_DB', '10')

REDIS_URL = 'redis://127.0.0.1:6379/2'

CELERY_IMPORTS = ('app.task.tasks',)
BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERY_ENABLE_UTC = True
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_RESULT_EXPIRES = 60 * 60 * 4
CELERY_ACCEPT_CONTENT = ['json']