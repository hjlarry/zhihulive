
import datetime
from . import db


class MyLive(db.Document):
    live_id = db.IntField()
    title = db.StringField()
    speaker = db.StringField()
    speaker_description = db.StringField()
    live_description = db.StringField()
    seats_count = db.IntField()
    price = db.IntField()

    def __unicode__(self):
        return self.title


class LiveContent(db.Document):
    message_id = db.IntField()
    sender = db.StringField()
    url = db.StringField()
    content = db.StringField()
    reply = db.StringField()
    likes = db.IntField()
    type = db.StringField()
    created_at = db.DateTimeField(default=datetime.datetime.now)
    live_title = db.ReferenceField(MyLive, required=False)