import peewee
import peewee_async
import config
from itertools import chain

database = peewee_async.MySQLDatabase(host=config.DB_HOST, database=config.DB_NAME, password=config.DB_PASS,
                                      user=config.DB_USER, charset='utf8mb4')


class BaseModel(peewee.Model):
    class Meta:
        database = database


class Live(BaseModel):
    zhihu_id = peewee.BigIntegerField(unique=True)
    title = peewee.CharField(null=True)
    speaker = peewee.CharField(null=True)
    speaker_description = peewee.TextField(null=True)
    live_description = peewee.TextField(null=True)
    outline = peewee.TextField(null=True)
    seats_count = peewee.IntegerField(null=True)
    price = peewee.IntegerField(null=True)
    liked_num = peewee.IntegerField(null=True)
    speaker_message_count = peewee.IntegerField(null=True)
    starts_at = peewee.DateTimeField(null=True)

    def __repr__(self):
        return '<Live({title})>'.format(title=self.title)


class Message(BaseModel):
    zhihu_id = peewee.BigIntegerField(unique=True)
    audio_url = peewee.CharField(null=True)
    audio_path = peewee.CharField(null=True)
    img_url = peewee.CharField(null=True)
    img_path = peewee.CharField(null=True)
    sender = peewee.CharField(null=True)
    text = peewee.TextField(null=True)
    reply = peewee.TextField(null=True)
    likes = peewee.IntegerField(null=True)
    type = peewee.CharField(null=True)
    created_at = peewee.DateTimeField(null=True)
    live = peewee.ForeignKeyField(Live, null=True)
    is_transform = peewee.BooleanField(default=False)
    is_played = peewee.BooleanField(default=False)
    is_deleted = peewee.BooleanField(default=False)
    transform_result = peewee.TextField(null=True)

    def __repr__(self):
        return '<Message({message_id})>'.format(message_id=self.zhihu_id)


def create_table():
    with database.allow_sync():
        Live.create_table(True)
        Message.create_table(True)


def drop_table():
    with database.allow_sync():
        Live.drop_table(True)
        Message.drop_table(True)


# Create async models manager:
database.set_allow_sync(False)
objects = peewee_async.Manager(database)


async def clean_data():
    all_message = await objects.execute(Message.select().where(Message.reply.is_null(False)))
    all_message = [[int(x) for x in str(v.reply).split(',')] for v in all_message]
    all_message = list(chain(*all_message))
    all_message = [all_message[i:i + 100] for i in range(0, len(all_message), 100)]
    async with objects.atomic():
        for k, v in enumerate(all_message):
            await objects.execute(Message.update(is_deleted=True).where(Message.zhihu_id.in_(v)))

if __name__ == '__main__':
    create_table()
