import hashlib
import hmac
import time
import json
import requests

from config import APP_SECRET, BAIDU_API_KEY, BAIDU_SECRET_KEY, BAIDU_TOKEN_URL


def gen_signature(data):
    data['timestamp'] = str(int(time.time()))

    params = ''.join([
        data['grant_type'],
        data['client_id'],
        data['source'],
        data['timestamp'],
    ])

    data['signature'] = hmac.new(
        APP_SECRET, params.encode('utf-8'), hashlib.sha1).hexdigest()


def get_baidu_token():
    data = {
        'grant_type': 'client_credentials',
        'client_id': BAIDU_API_KEY,
        'client_secret': BAIDU_SECRET_KEY
    }
    res = requests.post(BAIDU_TOKEN_URL, data=data)
    result = json.loads(res.text)
    return result['access_token']
