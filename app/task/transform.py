import requests
import json
import base64
from pydub import AudioSegment

from .celery_config import *


class Transform:

    header = {
        'Content-Type': 'application/json'
    }

    def __init__(self):
        self.token = self.get_token()

    @staticmethod
    def get_token():
        data = {
            'grant_type': 'client_credentials',
            'client_id': BAIDU_API_KEY,
            'client_secret': BAIDU_SECRET_KEY
        }
        res = requests.post(BAIDU_TOKEN_URL, data=data)
        result = json.loads(res.text)
        return result['access_token']

    def get_audio_text(self, url):
        file = 'app/Resource/downfile.aac'
        newfile = 'app/Resource/downfile.wav'
        res = requests.get(url)
        with open(file, 'wb') as f:
            f.write(res.content)
        aac_version = AudioSegment.from_file(file)
        rate = aac_version.frame_rate
        aac_version.export(newfile, format='wav')
        with open(newfile, 'rb') as f:
            file = f.read()
            length = len(file)
            b64 = base64.b64encode(file)
        data = {
            "format": "wav",
            "rate": rate,
            "channel": 1,
            "token": self.token,
            "cuid": "test21wwqsq",
            "len": length,
            "speech": b64.decode(),
        }
        data = json.dumps(data)
        res = requests.post(BAIDU_SERVER_URL, headers=self.header, data=data)
        res = json.loads(res.text)

        return res['result'][0]

if __name__ == '__main__':
    t = Transform()
    t.get_audio_text('https://live-audio.vzuu.com/0a9d4220faed91fa7c087c97c225b5f5')