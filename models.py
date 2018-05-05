import peewee
import peewee_async
import config

database = peewee_async.MySQLDatabase(host=config.DB_HOST, database=config.DB_NAME, password=config.DB_PASS,
                                      user=config.DB_USER, charset='utf8')


class BaseModel(peewee.Model):
    class Meta:
        database = database


class Live(BaseModel):
    live_id = peewee.BigIntegerField(unique=True, help_text='从知乎读取的ID')
    title = peewee.CharField(null=True)
    speaker = peewee.CharField(null=True)
    speaker_description = peewee.TextField(null=True)
    live_description = peewee.TextField(null=True)
    outline = peewee.TextField(null=True)
    seats_count = peewee.IntegerField(null=True)
    price = peewee.IntegerField(null=True)
    liked_num = peewee.IntegerField(null=True)
    speaker_message_count = peewee.IntegerField(null=True)
    created_at = peewee.DateTimeField(null=True)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Live({title})>'.format(title=self.title)


class Message(BaseModel):
    message_id = peewee.BigIntegerField(unique=True, help_text='从知乎读取的ID')
    url = peewee.CharField()
    sender = peewee.CharField()
    content = peewee.TextField()
    reply = peewee.TextField()
    likes = peewee.IntegerField()
    type = peewee.CharField()
    live = peewee.ForeignKeyField(Live)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Message({message_id})>'.format(message_id=self.message_id)


def create_table():
    # Look, sync code is working!
    with database.allow_sync():
        Live.create_table(True)
        Message.create_table(True)


# Create async models manager:
database.set_allow_sync(False)
objects = peewee_async.Manager(database)

if __name__ == '__main__':
    create_table()
