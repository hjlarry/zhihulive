from .transform import Transform
from .models import LiveContent
from . import celery


@celery.task(ignore_result=True)
def transform_task(id):
    t = Transform()
    live = LiveContent.objects(id=id).first()
    try:
        content = t.get_audio_text(live.url)
    except Exception as e:
        content = str(e)

    live.content = content
    live.save()