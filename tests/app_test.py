from app.task.crawl import *
from app.administrator.view import  zhihu_login

t = Crawl()

for obj in MyLive.objects():
    t.live_content_work(obj.id)