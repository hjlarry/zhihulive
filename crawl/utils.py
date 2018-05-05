import hashlib
import hmac
import time

from config import APP_SECRET


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