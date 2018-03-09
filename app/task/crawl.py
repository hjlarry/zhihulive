import json
import os
from datetime import datetime

from zhihu_oauth import ZhihuClient

from .celery_model import MyLive, LiveContent
from .celery_config import *


class Crawl:
    """
    A crawl obj with zhihu token.
    """
    def __init__(self, token=None):
        self.client = ZhihuClient()
        self.token = token or 'app/Resource/user.token'
        self.login_with_token()

    def login_with_token(self):
        """
        无法判断是否token有效
        :return: None
        """
        if os.path.isfile(self.token):
            self.client.load_token(self.token)

    def get_live_list(self):
        """
        获取当前用户购买过的所有live
        :return:
        """
        lives = self.client.me().lives
        return lives

    @staticmethod
    def save_live_list(livedata):
        """
        构建DB对象存储
        :param livedata:
        :return:
        """
        new_live = MyLive(live_id=livedata.id,
                          title=livedata.title,
                          speaker=livedata.speaker.name,
                          speaker_description=livedata.speaker.description,
                          live_description=livedata.description,
                          seats_count=livedata.seat_taken,
                          price=livedata.fee)
        new_live.save()

    def live_list_work(self):
        """

        :return:
        """
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

    def live_content_work(self, _id):
        live = MyLive.objects(id=_id).first()
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


if __name__ == '__main__':
    t = Crawl()
    # t.live_content_work('5a4dcf1c41a69a3097e30ccb')
    print(t.get_live_list())
