from zhihu_oauth import ZhihuClient
from zhihu_oauth.oauth import ZhihuOAuth
import os


class MyZhihuClient:
    def __init__(self):
        self.client = ZhihuClient()
        if os.path.isfile('login.token'):
            self.client.load_token('login.token')
        else:
            self.client.login_in_terminal()
            self.client.save_token('login.token')
        self.auth = ZhihuOAuth(self.client._token)

    def refresh_token(self):
        self.client.login_in_terminal()
        self.client.save_token('login.token')
        self.auth = ZhihuOAuth(self.client._token)
