from aiohttp import web
import aiohttp_jinja2
import jinja2
import os
import aiohttp_debugtoolbar

from models import objects, Live, Message


@aiohttp_jinja2.template('live/index.html')
async def index(request):
    items = await objects.execute(Live.select())
    data = {
        'items': items
    }
    return data


@aiohttp_jinja2.template('live/detail.html')
async def live_detail(request):
    live_id = request.match_info.get('id', 1)
    item = await objects.get(Live, id=live_id)
    data = {
        'item': item
    }
    return data


@aiohttp_jinja2.template('message/index.html')
async def message_list(request):
    live_id = request.match_info.get('id', 1)
    live = await objects.get(Live, id=live_id)
    current_page = int(request.query.get('page', 1))
    per_page = 20
    query = Message.select().where(Message.live == live_id).paginate(current_page, per_page)
    items = await objects.execute(query)
    counts = await objects.count(query, clear_limit=True)
    # 向上取整
    pages_count = (counts + per_page - 1) // per_page
    start_page = current_page - 3 if current_page > 3 else 1
    end_page = current_page + 4 if current_page < pages_count - 3 else pages_count + 1
    data = {
        'items': items,
        'live': live,
        'page': {
            'live_id': live_id,
            'counts': counts,
            'current_page': current_page,
            'pages_count': pages_count,
            'start_page': start_page,
            'end_page': end_page
        }
    }
    return data


@aiohttp_jinja2.template('message/detail.html')
async def message_detail(request):
    message_id = request.match_info.get('id', 1)
    zhihu_id = int(request.query.get('zhihu_id', 0))
    if zhihu_id:
        item = await objects.get(Message, zhihu_id=zhihu_id)
    else:
        item = await objects.get(Message, id=message_id)
    data = {
        'item': item
    }
    return data


def set_value(item, data, field):
    item.__dict__['_data'][field] = data[field] if data.get(field) else item.__dict__['_data'][field]


async def message_edit(request):
    data = await request.post()
    message_id = request.match_info.get('id', 1)
    item = await objects.get(Message, id=message_id)
    can_edit_fields = ['audio_url', 'audio_path', 'transform_result', 'img_url', 'img_path', 'sender', 'text', 'likes',
                       'created_at']
    for field in can_edit_fields:
        set_value(item, data, field)
    await objects.update(item)
    return web.HTTPFound(app.router['message_detail'].url_for(id=message_id))


async def message_delete(request):
    message_id = request.match_info.get('id')
    live_id = request.query.get('live_id', 1)
    item = await objects.get(Message, id=message_id)
    await objects.delete(item)
    return web.HTTPFound(app.router['live_content'].url_for(id=live_id))


app = web.Application()
tmpl_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'tmpl')
aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(tmpl_path))
app['static_root_url'] = '/static'
aiohttp_debugtoolbar.setup(app, intercept_redirects=False)
app.router.add_routes([web.get('/', index, name='index'),
                       web.get('/live/{id}', live_detail, name='live_detail'),
                       web.get('/live_content/{id}', message_list, name='live_content'),
                       web.get('/message/{id}', message_detail, name='message_detail'),
                       web.post('/message/{id}', message_edit, name='message_edit'),
                       web.post('/message/delete/{id}', message_delete, name='message_delete'),
                       ])

if __name__ == '__main__':
    app.router.add_static('/static', 'static')
    web.run_app(app)
