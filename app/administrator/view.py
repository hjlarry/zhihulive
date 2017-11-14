from jinja2 import Markup
from flask_admin.contrib.mongoengine import ModelView
from flask_admin.model.template import EndpointLinkRowAction
from flask_admin.contrib.mongoengine.filters import ReferenceObjectIdFilter
from flask_admin import expose, BaseView
from flask import request, redirect, url_for, flash

from ..models import LiveContent, MyLive
from ..crawl import Crawl
from .. import admin
from .. import celery


def _get_live_title_option():
    options = []
    for object in MyLive.objects():
        options.append((str(object.id), object.title))
    return tuple(options)


class LiveContentView(ModelView):
    column_list = ('sender', 'content', 'likes', 'type', 'created_at', 'image_or_audio')
    column_labels = dict(sender='作者', content='内容', likes='顶', type='类型', created_at='时间', image_or_audio='语音播放')
    column_sortable_list = ('sender', 'likes', 'type', 'created_at')
    column_editable_list = ['content']
    column_searchable_list = ('content',)
    column_filters = (ReferenceObjectIdFilter(column=LiveContent.live_title, name='live_title', options=_get_live_title_option()),'type')

    def _list_thumbnail(view, context, model, name):
        if model['type'] == 'image':
            imgurl = str(model['id'])+'.png'
            return Markup("<a href='%s' target='_blank'>查看图片</a>" % url_for('static', filename=imgurl))
        elif model['type'] == 'audio':
            return Markup('<audio controls height="100" width="100">'
                          '<source src="%s" type="audio/aac" />'
                          '</audio>' % model['url'])
        else:
            return ''


    column_formatters = {
        'image_or_audio': _list_thumbnail
    }
    can_edit = True
    edit_modal = True
    can_export = True
    export_types = ['xls']
    column_extra_row_actions = [
        EndpointLinkRowAction(
            'glyphicon glyphicon-transfer',
            'tools.transform',
        )
    ]


class MyLiveView(ModelView):
    column_list = ('speaker', 'title', 'live_description', 'seats_count', 'price')
    column_labels = dict(speaker='作者', title='标题', live_description='描述', seats_count='售出', price='价格')
    column_sortable_list = ('speaker', 'seats_count', 'price')
    column_editable_list = ['title']
    can_create = False
    inline_models = (LiveContent,)

    def _format_price(view, context, model, name):
        price = int(model['price'])/100
        return Markup("￥{}".format(price))

    column_formatters = {
        'price': _format_price
    }
    column_extra_row_actions = [
        EndpointLinkRowAction(
            'glyphicon glyphicon-download',
            'tools.crawl',
        ),
        EndpointLinkRowAction(
            'glyphicon glyphicon-transfer',
            'tools.transform_live',
        )
    ]


class MyAdminIndexView(BaseView):
    @expose('/')
    def main(self):
        return self.render('admin/main.html')

    @expose('/transform/<id>')
    def transform(self, id):
        live = LiveContent.objects(id=id).first()
        if live.url is '':
            flash('请选择音频文件进行转化', category='error')
            return redirect('/admin/livecontent')
        celery.send_task('app.tasks.transform_task', args=(id,))
        flash('已加入转换队列')
        return redirect('/admin/livecontent')

    @expose('/transform_live/<id>')
    def transform_live(self, id):
        lives = LiveContent.objects(live_title=id)
        for live in lives:
            if live.type == 'audio' and not live.content:
                celery.send_task('app.tasks.transform_task', args=(str(live.id),))
        flash('该live已加入转换队列')
        return redirect('/admin/mylive')

    @expose('/zhihulogin', methods=['POST'])
    def zhihu_login(self):
        global current
        # g.current = Crawl()
        current = Crawl()
        username = request.form['username']
        password = request.form['password']
        current.login(username, password)
        flash('登录成功')
        return redirect('/admin/tools', code=302)

    @expose('/crawl_live_list')
    def crawl_live_list(self):
        try:
            current.live_list_work()
        except Exception as e:
            return e
        else:
            return redirect('admin/livecontent')

    @expose('/crawl_live/<id>')
    def crawl(self, id):
        try:
            current.live_content_work(id)
        except Exception as e:
            return e
        else:
            flash('抓取成功')
            return redirect('admin/livecontent')





admin.add_view(MyLiveView(MyLive, name='我的LIVE'))
admin.add_view(LiveContentView(LiveContent, name='LIVE内容'))
admin.add_view(MyAdminIndexView(name='Other',endpoint='tools'))

