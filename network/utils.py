import hashlib
import hmac
import time
import json
import requests
import asyncio
import aiohttp

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


class BaseWebTransfer:
    def __init__(self, max_tries=4, max_tasks=10, *, loop=None):

        self.loop = loop or asyncio.get_event_loop()
        self.max_tries = max_tries
        self.max_tasks = max_tasks
        self.q = asyncio.Queue(loop=self.loop)

        self.headers = {}
        self._session = None
        self.seen_urls = set()
        self.finished_urls = set()
        self.temp = 0

    @property
    def session(self):
        if self._session is None:
            self._session = aiohttp.ClientSession(headers=self.headers, loop=self.loop)
        return self._session

    async def close(self):
        await self.session.close()
