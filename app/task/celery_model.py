from mongoengine import connect, Document, IntField, StringField, DateTimeField, ReferenceField
import datetime

connect('danery')


class MyLive(Document):
    live_id = IntField()
    title = StringField()
    speaker = StringField()
    speaker_description = StringField()
    live_description = StringField()
    seats_count = IntField()
    price = IntField()

    def __unicode__(self):
        return self.title


class LiveContent(Document):
    message_id = IntField()
    sender = StringField()
    url = StringField()
    content = StringField()
    reply = StringField()
    likes = IntField()
    type = StringField()
    created_at = DateTimeField(default=datetime.datetime.now)
    live_title = ReferenceField(MyLive, required=False)


if __name__ == '__main__':
    for a in MyLive.objects:
        print(a)