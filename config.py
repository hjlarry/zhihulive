import os

API_VERSION = '3.0.42'
APP_VERSION = '3.28.0'
APP_BUILD = 'release'
UUID = 'AJDA7XkI9glLBWc85sk-nJ_6F0jqALu4AlY='
UA = 'osee2unifiedRelease/3.28.0 (iPhone; iOS 10.2; Scale/2.00)'
APP_ZA = 'OS=iOS&Release=10.2&Model=iPhone8,1&VersionName=3.28.0&VersionCode=558&Width=750&Height='
CLIENT_ID = '8d5227e0aaaa4797a763ac64e0c3b8'
APP_SECRET = b'ecbefbf6b17e47ecb9035107866380'

TOKEN_FILE = 'token.json'
CAPTCHA_FILE = 'capture.jpg'
HERE = os.path.abspath(os.path.dirname(__file__))
DOWNLOAD_FOLDER = os.path.join(HERE, 'download')
IMAGE_FOLDER = os.path.join(DOWNLOAD_FOLDER, 'images')
AUDIO_FOLDER = os.path.join(DOWNLOAD_FOLDER, 'audios')
FILE_FOLDER = os.path.join(DOWNLOAD_FOLDER, 'file')
VIDEO_FOLDER = os.path.join(DOWNLOAD_FOLDER, 'video')

LOCAL_SERVER_HOST = '127.0.0.1'
LOCAL_SERVER_PORT = 8000

WEB_SERVER_HOST = '0.0.0.0'
WEB_SERVER_PORT = 8080

LOCAL_BASE_URL = 'http://{}:{}/'.format(LOCAL_SERVER_HOST, LOCAL_SERVER_PORT)
LOCAL_AUDIO_BASE_URL = LOCAL_BASE_URL + 'download/audios/'
LOCAL_IMG_BASE_URL = LOCAL_BASE_URL + 'download/images/'
LOCAL_FILE_BASE_URL = LOCAL_BASE_URL + 'download/file/'
LOCAL_VIDEO_BASE_URL = LOCAL_BASE_URL + 'download/video/'

for x in [DOWNLOAD_FOLDER, IMAGE_FOLDER, AUDIO_FOLDER, FILE_FOLDER, VIDEO_FOLDER]:
    if not os.path.exists(x):
        os.mkdir(x)

ZHIHU_API_ROOT = 'https://api.zhihu.com'
LOGIN_URL = ZHIHU_API_ROOT + '/sign_in'
CAPTCHA_URL = ZHIHU_API_ROOT + '/captcha'

LIVE_API_URL = 'https://api.zhihu.com/people/self/lives'
MESSAGE_API_URL = 'https://api.zhihu.com/lives/{zhihu_id}/messages?chronology=desc&before_id={before_id}'


BAIDU_API_KEY = 'Ud81kSVTD864enzE0dR6oMXm'
BAIDU_SECRET_KEY = 'p1PIZsLVbvBGZo0Twt3ZF1W46cep9XZq'
BAIDU_TOKEN_URL = 'https://openapi.baidu.com/oauth/2.0/token'
BAIDU_SERVER_URL = 'http://vop.baidu.com/server_api'

DB_HOST = '192.168.56.128'
DB_PORT = 60610
DB_NAME = 'zhihu'
DB_USER = 'zhihu'
DB_PASS = 'password'


with open(os.path.join(HERE, 'live_all.txt'), 'r', encoding='utf-8') as file:
    ALL_LIVES = [int(str(line).split(' ')[0]) for line in file.readlines()]

with open(os.path.join(HERE, 'big_live.txt'), 'r', encoding='utf-8') as file:
    EXCLUDE_LIVES = [int(str(line.split(' ')[0])) for line in file.readlines()]

# with open(os.path.join(HERE, 'live_all.txt'), 'r', encoding='utf-8') as file:
#     for x in file.readlines():
#         if int(x.split(' ')[1]) - int(x.split(' ')[2]) > 5:
#             print(x)


AUDIO_SEGMENT = False

try:
    from pydub import AudioSegment
    aac = AudioSegment.from_file(os.path.join(HERE, '00007bc50d1921b184e325ff0afc0961.aac'))
    aac.export(os.path.join(HERE, '00007bc50d1921b184e325ff0afc0961.wav'), format='wav')
    AUDIO_SEGMENT = True
except FileNotFoundError:
    print('未找到ffmpeg, 禁用acc转换为wav')
