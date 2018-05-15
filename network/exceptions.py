from json import JSONDecodeError


class UnexpectedResponseException(Exception):
    def __init__(self, url, res, expect):
        """
        服务器回复了和预期格式不符的数据

        :param str|unicode url: 当前尝试访问的网址
        :param request.Response res: 服务器的回复
        :param str|unicode expect: 一个用来说明期望服务器回复的数据格式的字符串
        """
        self.url = url
        self.res = res
        self.expect = expect

    def __repr__(self):
        return 'Get an unexpected response when visit url ' \
               '[{self.url}], we expect [{self.expect}], ' \
               'but the response body is [{self.res.text}]'.format(self=self)

    __str__ = __repr__


class LoginException(Exception):
    def __init__(self, error):
        self.error = error

    def __repr__(self):
        return 'Login Fail: {}'.format(self.error)

    __str__ = __repr__


MyJSONDecodeError = JSONDecodeError
