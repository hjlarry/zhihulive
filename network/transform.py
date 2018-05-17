import asyncio
import aiohttp
import time
import base64
import json
from pydub import AudioSegment

from models import objects, Message
from config import BAIDU_SERVER_URL

from .utils import get_baidu_token


class Transformer:
    def __init__(self, max_tries=4, max_tasks=10, *, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self.max_tries = max_tries
        self.max_tasks = max_tasks
        self.q = asyncio.Queue(loop=self.loop)

        self.headers = {'Content-Type': 'application/json'}
        self._session = None
        self.token = get_baidu_token()
        self.seen_urls = set()

    @property
    def session(self):
        if self._session is None:
            self._session = aiohttp.ClientSession(headers=self.headers, loop=self.loop)
        return self._session

    async def close(self):
        await self.session.close()

    async def add_queue(self):
        items = await objects.execute(Message.select().where((Message.type == 'audio') & (Message.is_transform == False)))
        for item in items:
            self.q.put_nowait((item.id, item.audio_path))

    async def transmit(self, message_id, audio_file):
        tries = 0
        with open(audio_file, 'rb') as f:
            file = f.read()
            length = len(file)
            b64 = base64.b64encode(file)
        file = AudioSegment.from_file(audio_file)
        rate = file.frame_rate
        data = {
            "format": "wav",
            "rate": rate,
            "channel": 1,
            "token": self.token,
            "cuid": "anewversion",
            "len": length,
            "speech": b64.decode(),
        }
        data = json.dumps(data)
        while tries < self.max_tries:
            try:
                response = await self.session.post(BAIDU_SERVER_URL, data=data, allow_redirects=False, headers=self.headers)
                break
            except aiohttp.ClientError as client_error:
                print(client_error)
            tries += 1
        else:
            return

        try:
            await self.parse_result(response, message_id)
            print('{} has finished'.format(message_id))

        finally:
            response.release()

    async def parse_result(self, response, message_id):
        rs = await response.json()
        if response.status == 200:
            message = await objects.get(Message, id=message_id)
            message.transform_result = rs['result'][0]
            message.is_transform = True
            await objects.update(message)

    async def work(self):
        try:
            while 1:
                message_id, audio_file = await self.q.get()
                await self.transmit(message_id, audio_file)
                self.q.task_done()
                asyncio.sleep(1)
        except asyncio.CancelledError:
            pass

    async def transform(self):
        self.__workers = [asyncio.Task(self.work(), loop=self.loop) for _ in range(self.max_tasks)]
        self.t0 = time.time()
        await self.q.join()
        await self.add_queue()
        await self.q.join()
        self.t1 = time.time()
        for w in self.__workers:
            w.cancel()

        await self.close()
