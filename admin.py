from flask import Flask
import flask_admin as admin
from flask_admin.contrib.pymongo import ModelView, filters
from jinja2 import Markup
from mongo import db
from wtforms import form, fields


# Create application
app = Flask(__name__, static_folder='Resource')

# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = '123456790'


class LiveForm(form.Form):
    message_id = fields.IntegerField('ID')
    sender = fields.StringField('Sender')
    url = fields.StringField('URL')
    content = fields.TextAreaField('Content')
    reply = fields.StringField('Reply to')
    likes = fields.IntegerField('Likes')
    type = fields.StringField('Type')
    created_at = fields.DateTimeField('Created at')


class LiveView(ModelView):
    column_list = ('sender', 'content', 'likes', 'type', 'created_at', 'image_or_audio')
    column_sortable_list = ('sender', 'likes', 'type', 'created_at')

    def _list_thumbnail(view, context, model, name):
        if model['type'] == 'image':
            if model['content'] is None:
                return Markup("尚未下载图片")
            else:
                imgurl = '/'+model['content']
                return Markup("<a href='%s' target='_blank'>查看图片</a>" % imgurl)
        elif model['type'] == 'audio':
            return Markup('<audio controls height="100" width="100">'
                          '<source src="%s" type="audio/aac" />'
                          '</audio>' % model['url'])
        else:
            return ''

    column_formatters = {
        'image_or_audio': _list_thumbnail
    }
    can_export = True
    export_types = ['xls']
    edit_modal = True
    column_searchable_list = ('content',)

    column_filters = (filters.FilterEqual('type', 'Type'),
                      filters.FilterNotEqual('type', 'Type'))
    form = LiveForm


# Flask views
@app.route('/')
def index():
    return '<a href="/admin/">Click me to get to Admin!</a>'


if __name__ == '__main__':
    # Create admin
    admin = admin.Admin(app, 'Manage Your ZhihuLive')

    # Add views
    collections = db.collection_names()
    for collect in collections:
        admin.add_view(LiveView(db[collect], collect, category='Live List'))

    # Start app
    app.run(debug=True)