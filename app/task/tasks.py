from .transform import Transform
from .crawl import Crawl
from .celery_model import LiveContent
from . import celery


@celery.task(ignore_result=True)
def transform_task(id):
    t = Transform()
    live = LiveContent.objects(id=id).first()
    try:
        content = t.get_audio_text(live.url)
    except Exception as e:
        print(e)
        raise

    live.content = content
    live.save()


@celery.task(ignore_result=True)
def crawl_live_list():
    c = Crawl()
    try:
        c.login_with_token()
        c.live_list_work()
    except Exception as e:
        print(e)


@celery.task(ignore_result=True)
def crawl_live(id):
    c = Crawl()
    try:
        c.login_with_token()
        c.live_content_work(id)
    except Exception as e:
        print(e)