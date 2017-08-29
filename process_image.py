import requests
import os
from mongo import db


def get_image(filename, url, filepath):
    content = requests.get(url).content
    file = filepath + filename + '.png'
    with open(file, 'wb') as f:
        f.write(content)


def download_image(collection_name):
    collection = db[collection_name]
    collection_filepath = './Resource/'+collection_name+'/image/'
    if os.path.exists(collection_filepath):
        pass
    else:
        os.mkdir('./Resource/'+collection_name)
        os.mkdir(collection_filepath)
    records = collection.find({'type': 'image', 'content': None})

    for record in records:
        get_image(record['message_id'], record['url'], collection_filepath)
        record['content'] = collection_filepath+record['message_id']+'.png'
        collection.save(record)
        print(record['message_id']+'success')

download_image('733368182634479616')