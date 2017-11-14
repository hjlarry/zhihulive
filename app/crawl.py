from __future__ import unicode_literals, print_function
import json
from datetime import datetime
import os
from zhihu_oauth import ZhihuClient
from zhihu_oauth.exception import NeedCaptchaException

from .models import MyLive, LiveContent
from config import *

class Crawl:
    def __init__(self):
        self.client = ZhihuClient()

    def login(self, username, password):
        if os.path.isfile('app/Resource/'+username+'.token'):
            self.client.load_token('app/Resource/'+username+'.token')
        else:
            try:
                self.client.login(username, password)
            except NeedCaptchaException:
                # 保存验证码并提示输入，重新登录
                with open('a.gif', 'wb') as f:
                    f.write(self.client.get_captcha())
                captcha = input('please input captcha:')
                self.client.login(username, password, captcha)
            self.client.save_token('app/Resource/'+username+'.token')

    def get_live_list(self):
        lives = self.client.me().lives
        return lives

    @staticmethod
    def save_live_list(livedata):
        new_live = MyLive(live_id=livedata.id,
                          title=livedata.title,
                          speaker=livedata.speaker.name,
                          speaker_description=livedata.speaker.description,
                          live_description=livedata.description,
                          seats_count=livedata.seat_taken,
                          price=livedata.fee)
        new_live.save()

    def live_list_work(self):
        for live in self.get_live_list():
            exist = MyLive.objects(live_id=live.id)
            if not exist:
                self.save_live_list(live)

    def get_live_content(self, live_id, before_id=''):
        res = self.client._session.get(LIVECONTENT_URL.format(live_id, before_id))
        data = json.loads(res.content)
        return data

    def save_live_content_image(self, id, url):
        content = self.client._session.get(url).content
        file = 'app/Resource/' + str(id) + '.png'
        with open(file, 'wb') as f:
            f.write(content)

    @staticmethod
    def save_live_content(live_id, livedata):
        for r in livedata['data']:
            exist = LiveContent.objects(message_id=r['id'])
            if exist:
                continue

            if r['type'] == 'audio':
                url = r['audio']['url']
            elif r['type'] == 'image':
                url = r['image']['full']['url']

            else:
                url = ''
            content = r['text'] if 'text' in r else ''
            reply = ','.join(r['replies']) if 'replies' in r else ''

            new_live_content = LiveContent(message_id=int(r['id']),
                                           sender=r['sender']['member']['name'],
                                           type=r['type'],
                                           content=content,
                                           url=url,
                                           reply=reply,
                                           likes=r['likes']['count'],
                                           created_at=datetime.fromtimestamp((r['created_at'])),
                                           live_title=live_id
                                           )
            new_live_content.save()

    def live_content_work(self, id):
        live = MyLive.objects(id=id).first()
        # 使用知乎的live的ID值传入获取详情
        data = self.get_live_content(live.live_id)
        while data['unload_count'] > 0:
            # 存储时使用mongo的ID值传入
            self.save_live_content(live.id, data)
            data = self.get_live_content(live.live_id, data['data'][0]['id'])
        else:
            print('success')

        image_contents = LiveContent.objects(live_title=live.id, type='image')
        for item in image_contents:
            self.save_live_content_image(item.id, item.url)














