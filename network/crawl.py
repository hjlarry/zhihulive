import asyncio
import aiohttp
import os
import time
import traceback
from urllib.parse import urlparse
from pydub import AudioSegment

from models import objects, Live, Message
from config import LIVE_API_URL, MESSAGE_API_URL, IMAGE_FOLDER, AUDIO_FOLDER, EXCLUDE_LIVES, ALL_LIVES, AUDIO_SEGMENT
from config import FILE_FOLDER, VIDEO_FOLDER

from .zhihu import MyZhihuClient
from .utils import BaseWebTransfer


class Crawler(BaseWebTransfer):
    def __init__(self, max_tries=4, max_tasks=20, *, loop=None):
        super().__init__(max_tries, max_tasks, loop=loop)
        self.client = MyZhihuClient()
        self.client.auth(self)

    async def check_token(self):
        async with self.session.get(LIVE_API_URL) as resp:
            if resp.status == 401:
                self.client.refresh_token()

    def add_url(self, url, live=None):
        if url not in self.seen_urls:
            self.seen_urls.add(url)
            self.q.put_nowait((url, live))

    async def parse_live_link(self, response):
        rs = await response.json()
        if response.status == 200:
            for live in rs['data']:
                if live['id'] in EXCLUDE_LIVES:
                    continue
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
                # 是否已经完成下载
                speaker_message_count = await objects.count(Message.select().where(Message.live == item.id,
                                                                                   Message.is_played == True))
                if item.speaker_message_count == speaker_message_count:
                    continue
                self.add_url(MESSAGE_API_URL.format(zhihu_id=item.zhihu_id, before_id=''), live=item)
            if not rs['paging']['is_end']:
                self.add_url(rs['paging']['next'])

    async def parse_live_one(self, response):
        live = await response.json()
        if response.status == 200:
            if int(live['id']) in EXCLUDE_LIVES:
                return
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
            # 是否已经完成下载
            speaker_message_count = await objects.count(Message.select().where(Message.live == item.id,
                                                                               Message.is_played == True))
            if item.speaker_message_count == speaker_message_count:
                print('%s include' % item.zhihu_id)
                return
            if speaker_message_count != 0:
                print(item.zhihu_id, item.speaker_message_count, speaker_message_count)
            self.add_url(MESSAGE_API_URL.format(zhihu_id=item.zhihu_id, before_id=''), live=item)

    async def parse_message_link(self, response, live):
        rs = await response.json()
        # 是否已经完成下载
        # 有bug, 最后一页可能没有主讲人
        # speaker_message_count = await objects.count(Message.select().where(Message.live == live.id,
        #                                                                    Message.is_played == True))
        # if live.speaker_message_count == speaker_message_count:
        #     print('%s ok' % live.zhihu_id)
        #     return
        if response.status == 200:
            for message in rs['data']:
                audio_url = message['audio']['url'] if 'audio' in message else None
                # 视频
                if audio_url is None and 'video' in message:
                    audio_url = message['video']['playlist'][0]['url']
                img_url = message['image']['full']['url'] if 'image' in message else None
                # 多张图
                if img_url is None and 'multiimage' in message:
                    img_url = '|'.join([x['full']['url'] for x in message['multiimage']])
                # 文件
                if img_url is None and 'file' in message:
                    img_url = message['file']['url']
                text = message['text'] if 'text' in message else None
                is_played = True if message['sender']['role'] in ('speaker', 'cospeaker') else False
                reply = ','.join(message['replies']) if 'replies' in message else None
                created_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(message['created_at']))
                item, is_created = await objects.create_or_get(Message,
                                                               zhihu_id=message['id'],
                                                               type=message['type'],
                                                               sender=message['sender']['member']['name'],
                                                               likes=message['likes']['count'],
                                                               live=live.id,
                                                               audio_url=audio_url,
                                                               img_url=img_url,
                                                               text=text,
                                                               is_played=is_played,
                                                               reply=reply,
                                                               created_at=created_at
                                                               )

                if is_created and message['type'] in ('multiimage', 'image') and img_url:
                    item.img_path = await self.convert_local_images(img_url)
                    await objects.update(item)
                elif is_created and img_url and message['type'] == 'file':
                    item.img_path = await self.convert_local_file(img_url, message['file']['file_name'])
                    await objects.update(item)
                elif is_created and audio_url and message['type'] == 'video':
                    item.audio_path = await self.convert_local_video(audio_url, str(urlparse(audio_url).path).split('/')[-1])
                    await objects.update(item)
                elif is_created and audio_url and message['type'] == 'audio':
                    item.audio_path = await self.convert_local_audio(audio_url)
                    await objects.update(item)

            if rs['unload_count'] > 0:
                self.add_url(MESSAGE_API_URL.format(zhihu_id=live.zhihu_id, before_id=rs['data'][0]['id']), live=live)

    async def convert_local_images(self, pic_urls):
        all_path = []
        for pic_url in pic_urls.split('|'):
            pic_name = pic_url.split('/')[-1]
            path = os.path.join(IMAGE_FOLDER, pic_name)
            if not os.path.exists(path):
                async with self.session.get(pic_url) as resp:
                    content = await resp.read()
                    with open(path, 'wb') as f:
                        f.write(content)
            all_path.append(path)
        return '|'.join([str(x) for x in all_path])

    async def convert_local_file(self, url, name):
        path = os.path.join(FILE_FOLDER, name)
        if not os.path.exists(path):
            async with self.session.get(url) as resp:
                content = await resp.read()
                with open(path, 'wb') as f:
                    f.write(content)
        return path

    async def convert_local_audio(self, audio_url):
        if AUDIO_SEGMENT:
            audio_name = audio_url.split('/')[-1] + '.wav'
        else:
            audio_name = audio_url.split('/')[-1] + '.aac'
        path = os.path.join(AUDIO_FOLDER, audio_name)
        if not os.path.exists(path):
            async with self.session.get(audio_url) as resp:
                content = await resp.read()
                with open(path, 'wb') as f:
                    f.write(content)
                if AUDIO_SEGMENT:
                    aac = AudioSegment.from_file(path)
                    aac.export(path, format='wav')
        return path

    async def convert_local_video(self, video_url, name):
        path = os.path.join(VIDEO_FOLDER, name)
        if not os.path.exists(path):
            async with self.session.get(video_url) as resp:
                content = await resp.read()
                with open(path, 'wb') as f:
                    f.write(content)
        return path

    async def fetch(self, url, live=None, live_lists=None):
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
            if live:
                await self.parse_message_link(response, live)
            elif live_lists:
                await self.parse_live_one(response)
            else:
                await self.parse_live_link(response)
            print('{} has finished'.format(url))
        finally:
            response.release()

    async def work(self, live_lists=None):
        while 1:
            try:
                url, live_id = await self.q.get()
                await self.fetch(url, live_id, live_lists)
                self.q.task_done()
                self.finished_urls.add(url)
            except asyncio.CancelledError:
                pass
            except Exception as e:
                traceback.print_tb(e.__traceback__)
            asyncio.sleep(1)

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

    async def crawl_vip(self):
        await self.check_token()
        self.__workers = [asyncio.Task(self.work(live_lists=True), loop=self.loop) for _ in range(self.max_tasks)]
        self.t0 = time.time()
        await self.q.join()
        for x in ALL_LIVES:
            self.add_url('https://api.zhihu.com/lives/%s' % x)
        await self.q.join()
        self.t1 = time.time()
        for w in self.__workers:
            w.cancel()

        await self.close()
