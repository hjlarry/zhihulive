# Manage Your Zhihu Live


## 介绍
这是一个管理你购买过的知乎LIVE的工具，使用场景是往往我们听过的live是语音格式，无法保存、沉淀和搜索。知乎live本身做为一个付费内容，它的内容价值较高，所以做这样的工具能帮助自己更好的管理知识。希望您能注重版权，切勿随意分享自己购买过的live。


## 使用

### 登录并抓取数据
```
python3 crawl.py
```
这里使用的是二维码登录的方式，网页直接登录的验证码不太好破解
![](ScreenShot/1.jpg)

### 处理抓取的音频文件
```
python3 process_audio.py
```
这一步是将音频文件下载下来，并通过ffmpeg转换为wav格式，然后提交给百度语音进行语音识别（您需要安装相关[ffmpeg组件](https://www.ffmpeg.org/)，并申请[百度API](http://yuyin.baidu.com/)的KEY，后续版本将改成多线程以提高效率），将识别结果写入mongo
![](ScreenShot/2.jpg)

### 处理抓取的图片
```
python3 process_image.py
```
将图片下载储存到本地

### 启动管理服务
```
python3 admin.py
```
![](ScreenShot/3.jpg)

如图中红圈所见，如果您无法正确的得到抓取结果，是由于码率没有设置成16000，live中有的主讲人用的码率是8000、有的则是16000
