import requests
import json
import base64
import os
from pydub import AudioSegment

from config import *

class Transform:

    header = {
        'Content-Type': 'application/json'
    }

    def __init__(self):
        self.token = self.get_token()

    def get_token(self):
        data = {
            'grant_type': 'client_credentials',
            'client_id': BAIDU_API_KEY,
            'client_secret': BAIDU_SECRET_KEY
        }
        res = requests.post(BAIDU_TOKEN_URL, data=data)
        result = json.loads(res.text)
        return result['access_token']

    def get_audio_text(self, url):
        content = requests.get(url).content
        file = 'Resource/downfile.aac'
        newfile = 'Resource/downfile.wav'
        with open(file, 'wb') as f:
            f.write(content)
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
