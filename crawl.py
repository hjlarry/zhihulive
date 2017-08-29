import requests
from PIL import Image
import json
from datetime import datetime
from mongo import db
from selenium import webdriver
from time import sleep

session = requests.session()
LOGIN_URL = 'https://www.zhihu.com/signin#signin'
MYLIVE_URL = 'https://api.zhihu.com/people/self/lives'

'''
使用模拟浏览器,输入邮箱密码登录的方式去获取cookie，发现登录验证码很难正确的输入，所以采用二维码登录的方式


    
def get_cookie(username, password):
    # browser = webdriver.PhantomJS(service_args=["--remote-debugger-port=9000"])
    browser = webdriver.Chrome('./chromedriver')
    browser.get(LOGIN_URL)
    password_login_button = browser.find_element_by_class_name('signin-switch-password')
    password_login_button.click()
    account = browser.find_element_by_name('account')
    account.send_keys(username)
    pwd = browser.find_element_by_name('password')
    pwd.send_keys(password)
    submmit = browser.find_element_by_class_name('submit')
    submmit.click()
    captcha = browser.find_element_by_class_name('Captcha-image')
    if captcha:
        sleep(2)
        get_captcha(captcha, browser)
    submmit.click()
    while browser.current_url == LOGIN_URL:
        sleep(2)
        get_captcha(captcha, browser)
        submmit.click()
        sleep(1)
        print(browser.current_url)
    cookies = browser.get_cookies()
    cookies_dict = {}
    for cookie in cookies:
        if 'name' in cookie and 'value' in cookie:
            cookies_dict[cookie['name']] = cookie['value']
    print(cookies_dict)
    return cookies_dict
    sleep(300)


def get_captcha(captcha, browser):
    browser.save_screenshot('captcha.png')
    im = Image.open('captcha.png')
    im.save('screenshot.png')
    im.show()
    ids = input('请输入第几个文字是倒立的,逗号分隔')
    im.close()
    ids = ids.split(',')
    for id in ids:
        action = ActionChains(browser)
        action.move_to_element_with_offset(captcha, 15 + 20 * (int(id) - 1), 15)
        action.click()
        action.perform()
'''


Headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Connection': 'keep-alive',
    'Host': 'account.zhihu.com',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6)  Chrome/60.0.3112.101 Safari/537.36'
}


def login_to_get_cookie():
    browser = webdriver.PhantomJS(service_args=["--remote-debugger-port=9000"])
    browser.get(LOGIN_URL)
    browser.implicitly_wait(5)
    qr_code = browser.find_element_by_class_name('qrcode-signin-img')
    content = requests.get(qr_code.get_attribute('src'), headers=Headers).content
    with open('qrcode.png', 'wb') as f:
        f.write(content)
    im = Image.open('qrcode.png')
    im.show()
    input('请使用知乎手机客户端扫描二维码,登录后按回车键继续')
    im.close()
    sleep(2)
    cookies = browser.get_cookies()
    cookies_str = ''
    for cookie in cookies:
        if 'name' in cookie and 'value' in cookie:
            cookies_str = cookies_str + cookie['name'] + '=' + cookie['value'] + ';'
    return cookies_str


# 先看本地的cookie文件，避免每次都去登录获取cookie
def read_cookie_file():
    with open('cookie.txt', 'r+', encoding='utf-8') as f:
        content = f.read()
        if content == '':
            content = login_to_get_cookie()
            f.write(content)
        return content

Headers2 = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Host': 'api.zhihu.com',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Cookie': read_cookie_file()

}


def get_live(live_id, live_subject, before_id=''):
    live_url = 'https://api.zhihu.com/lives/'+live_id+'/messages?chronology=desc&before_id='+before_id
    session.headers.update({'x-test': 'true'})
    res = session.get(live_url, headers=Headers2)
    res = json.loads(res.text)
    collection = db[live_subject]
    for r in res['data']:

        if r['type'] == 'text':
            content = r['text']
            url = None
        elif r['type'] == 'audio':
            content = None
            url = r['audio']['url']
        elif r['type'] == 'image':
            content = None
            url = r['image']['full']['url']
        else:
            content = 'some type have not check'
            url = None

        if 'replies' in r:
            reply = r['replies']
        else:
            reply = None

        data = {
            'message_id': r['id'],
            'sender': r['sender']['member']['name'],
            'type': r['type'],
            'content': content,
            'url': url,
            'reply': reply,
            'likes': r['likes']['count'],
            'created_at': datetime.fromtimestamp((r['created_at']))
        }

        collection.insert(data)

    if res['unload_count'] > 0:
        return get_live(live_id, live_subject, res['data'][0]['id'])
    else:
        print('success')


def get_live_list():
    res = session.get(MYLIVE_URL, headers=Headers2)
    res = json.loads(res.text)
    livelist = []
    livedict = {}
    for index, r in enumerate(res['data']):
        print(str(index)+':'+r['subject'])
        livelist.append(r['id'])
        livedict[r['id']] = r['subject']
    id = input('请输入要抓取的ID:')
    live_id = livelist[int(id)]
    live_subject = livedict[live_id]
    get_live(live_id, live_subject)

get_live_list()





