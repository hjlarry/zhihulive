from aiohttp import web
import aiohttp_jinja2
import jinja2
import os

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
async def message_index(request):
    live_id = request.match_info.get('id', 1)
    current_page = int(request.query.get('page', 1))
    per_page = 20
    query = Message.select().where(Message.live == live_id).paginate(current_page, per_page)
    items = await objects.execute(query)
    for item in items:
        if item.type == 'audio' and item.is_transform:
            item.text = item.transform_result
    counts = await objects.count(query, clear_limit=True)
    # 向上取整
    pages_count = (counts + per_page - 1) // per_page
    start_page = current_page - 3 if current_page > 3 else 1
    end_page = current_page + 4 if current_page < pages_count - 3 else pages_count + 1
    data = {
        'items': items,
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


app = web.Application()
tmpl_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'tmpl')
aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(tmpl_path))
app['static_root_url'] = '/static'
app.router.add_static('/static', 'static')
app.router.add_routes([web.get('/', index, name='index'),
                       web.get('/live/{id}', live_detail, name='live_detail'),
                       web.get('/live_content/{id}', message_index, name='live_content'),
                       ])

if __name__ == '__main__':
    web.run_app(app)
