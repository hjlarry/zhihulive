import asyncio
import aiohttp
import os
import time
from pydub import AudioSegment

from models import objects, Live, Message
from config import LIVE_API_URL, MESSAGE_API_URL, IMAGE_FOLDER, AUDIO_FOLDER

from zhihu_oauth import ZhihuClient
from .utils import BaseWebTransfer


class Crawler(BaseWebTransfer):
    def __init__(self, max_tries=4, max_tasks=10, *, loop=None):
        super().__init__(max_tries, max_tasks, loop=loop)
        self.client = ZhihuClient()

    async def check_token(self):
        async with self.session.get(LIVE_API_URL) as resp:
            if resp.status == 401:
                if os.path.isfile('login.token'):
                    self.client.load_token('login.token')
                else:
                    self.client.login_in_terminal()
                    self.client.save_token('login.token')

    def add_url(self, url, live_id=None, zhihu_id=None):
        if url not in self.seen_urls:
            self.seen_urls.add(url)
            self.q.put_nowait((url, live_id, zhihu_id))

    async def parse_live_link(self, response):
        rs = await response.json()
        if response.status == 200:
            for live in rs['data']:
                starts_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(live['starts_at']))
                item, is_created = await objects.create_or_get(Live,
                                                               zhihu_id=live['id'],
                                                               title=live['subject'],
                                                               speaker=live['speaker']['member']['name'],
                                                               speaker_description=live['speaker']['description'],
                                                               live_description=live['description'],
                                                               outline=live['outline'],
                                                               seats_count=live['seats']['taken'],
                                                               price=live['fee']['original_price'],
                                                               liked_num=live['liked_num'],
                                                               speaker_message_count=live['speaker_message_count'],
                                                               starts_at=starts_at
                                                               )
                # 957358881807056896是关于霍金的免费live，太大了，不抓取
                if is_created and not item.zhihu_id == 957358881807056896:
                    zhihu_id = item.zhihu_id
                    self.add_url(MESSAGE_API_URL.format(zhihu_id=zhihu_id, before_id=''), live_id=item.id,
                                 zhihu_id=zhihu_id)
            if not rs['paging']['is_end']:
                self.add_url(rs['paging']['next'])

    async def parse_message_link(self, response, live_id, zhihu_id):
        rs = await response.json()
        if response.status == 200:
            for message in rs['data']:
                audio_url = message['audio']['url'] if 'audio' in message else None
                img_url = message['image']['full']['url'] if 'image' in message else None
                text = message['text'] if 'text' in message else None
                reply = ','.join(message['replies']) if 'replies' in message else None
                created_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(message['created_at']))
                item, is_created = await objects.create_or_get(Message,
                                                               zhihu_id=message['id'],
                                                               type=message['type'],
                                                               sender=message['sender']['member']['name'],
                                                               likes=message['likes']['count'],
                                                               live=live_id,
                                                               audio_url=audio_url,
                                                               img_url=img_url,
                                                               text=text,
                                                               reply=reply,
                                                               created_at=created_at
                                                               )

                if is_created and img_url:
                    item.img_path = await self.convert_local_image(img_url)
                elif is_created and audio_url:
                    item.audio_path = await self.convert_local_audio(audio_url)
                await objects.update(item)

            if rs['unload_count'] > 0:
                self.add_url(MESSAGE_API_URL.format(zhihu_id=zhihu_id, before_id=rs['data'][0]['id']), live_id=live_id,
                             zhihu_id=zhihu_id)

    async def convert_local_image(self, pic_url):
        pic_name = pic_url.split('/')[-1]
        path = os.path.join(IMAGE_FOLDER, pic_name)
        if not os.path.exists(path):
            async with self.session.get(pic_url) as resp:
                content = await resp.read()
                with open(path, 'wb') as f:
                    f.write(content)
        return path

    async def convert_local_audio(self, audio_url):
        audio_name = audio_url.split('/')[-1] + '.wav'
        path = os.path.join(AUDIO_FOLDER, audio_name)
        if not os.path.exists(path):
            async with self.session.get(audio_url) as resp:
                content = await resp.read()
                with open(path, 'wb') as f:
                    f.write(content)
                aac = AudioSegment.from_file(path)
                aac.export(path, format='wav')
        return path

    async def fetch(self, url, live_id=None, zhihu_id=None):
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
            if live_id:
                await self.parse_message_link(response, live_id, zhihu_id)
            else:
                await self.parse_live_link(response)
            print('{} has finished'.format(url))

        finally:
            response.release()

    async def work(self):
        try:
            while 1:
                url, live_id, zhihu_id = await self.q.get()
                await self.fetch(url, live_id, zhihu_id)
                self.q.task_done()
                asyncio.sleep(1)
        except asyncio.CancelledError:
            pass

    async def crawl(self):
        await self.check_token()
        self.__workers = [asyncio.Task(self.work(), loop=self.loop) for _ in range(self.max_tasks)]
        self.t0 = time.time()
        await self.q.join()
        self.add_url(LIVE_API_URL)
        await self.q.join()
        self.t1 = time.time()
        for w in self.__workers:
            w.cancel()

        await self.close()
