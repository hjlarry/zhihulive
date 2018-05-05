import asyncio
import aiohttp
import os
import time

from crawl.client import ZhihuClient
from models import objects, Live

LIVE_API_URL = 'https://api.zhihu.com/people/self/lives'
MESSAGE_API_URL = 'https://api.zhihu.com/lives/{live_id}/messages?chronology=desc&before_id={before_id}'
IMAGE_FOLDER = 'static/images/zhihu'


class Crawler:
    def __init__(self, max_redirect=10, max_tries=4, max_tasks=10, *, loop=None):

        self.loop = loop or asyncio.get_event_loop()
        self.max_redirect = max_redirect
        self.max_tries = max_tries
        self.max_tasks = max_tasks
        self.q = asyncio.Queue(loop=self.loop)

        self.headers = {}
        self.client = ZhihuClient()
        self.client.auth(self)
        self._session = None
        self.seen_urls = set()

    @property
    def session(self):
        if self._session is None:
            self._session = aiohttp.ClientSession(headers=self.headers, loop=self.loop)
        return self._session

    async def close(self):
        await self.session.close()

    async def check_token(self):
        async with self.session.get(LIVE_API_URL) as resp:
            if resp.status == 401:
                self.client.refresh_token()

    async def parse_live_link(self, response):
        rs = await response.json()
        if response.status == 200:
            for live in rs['data']:
                created_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(live['created_at']))
                item, is_created = await objects.create_or_get(Live,
                                                               live_id=live['id'],
                                                               title=live['subject'],
                                                               speaker=live['speaker']['member']['name'],
                                                               speaker_description=live['speaker']['description'],
                                                               live_description=live['description'],
                                                               outline=live['outline'],
                                                               seats_count=live['seats']['taken'],
                                                               price=live['fee']['original_price'],
                                                               liked_num=live['liked_num'],
                                                               speaker_message_count=live['speaker_message_count'],
                                                               created_at=created_at
                                                               )
                if is_created:
                    self.add_message_url(item)
            if not rs['paging']['is_end']:
                return rs['paging']['next']

    async def parse_message_link(self, response):
        pass

    async def work(self):
        try:
            while 1:
                url, max_redirect = await self.q.get()
                await self.fetch(url, max_redirect)
                self.q.task_done()
                asyncio.sleep(1)
        except asyncio.CancelledError:
            pass

    def add_url(self, url, max_redirect=None):
        if max_redirect is None:
            max_redirect = self.max_redirect
        if url not in self.seen_urls:
            self.seen_urls.add(url)
            self.q.put_nowait((url, max_redirect))

    def add_message_url(self, item):
        print(item.live_id)

    async def fetch(self, url, max_redirect):
        tries = 0
        while tries < self.max_tries:
            try:
                response = await self.session.get(url, allow_redirects=False)
                break
            except aiohttp.ClientError as client_error:
                print(client_error)
            tries += 1
        else:
            return

        try:
            parse_fn = self.parse_live_link if 'self' in url else self.parse_message_link
            next_url = await parse_fn(response)
            print('{} has finished'.format(url))
            if next_url is not None:
                self.add_url(next_url, max_redirect)
        finally:
            response.release()

    async def convert_local_image(self, pic):
        pic_name = pic.split('/')[-1]
        path = os.path.join(IMAGE_FOLDER, pic_name)
        if not os.path.exists(path):
            async with self.session.get(pic) as resp:
                content = await resp.read()
                with open(path, 'wb') as f:
                    f.write(content)
        return path

    async def crawl(self):
        await self.check_token()
        self.__workers = [asyncio.Task(self.work(), loop=self.loop)
                          for _ in range(self.max_tasks)]
        self.t0 = time.time()
        await self.q.join()
        self.add_url(LIVE_API_URL)
        await self.q.join()
        self.t1 = time.time()
        for w in self.__workers:
            w.cancel()

        await self.close()
