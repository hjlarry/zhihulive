import requests
import json
import base64
import os
from pydub import AudioSegment
from mongo import db


# 定义百度语音所需环境常量
BAIDU_API_KEY = 'Ud81kSVTD864enzE0dR6oMXm'
BAIDU_SECRET_KEY = 'p1PIZsLVbvBGZo0Twt3ZF1W46cep9XZq'
BAIDU_TOKEN_URL = 'https://openapi.baidu.com/oauth/2.0/token'
BAIDU_SERVER_URL = 'http://vop.baidu.com/server_api'
RATE = 8000


def get_token_for_baidu():
    data = {
        'grant_type': 'client_credentials',
        'client_id': BAIDU_API_KEY,
        'client_secret': BAIDU_SECRET_KEY
    }
    res = requests.post(BAIDU_TOKEN_URL, data=data)
    result = json.loads(res.text)
    return result['access_token']


def change_to_text_by_baidu(speech_file):
    header = {
        'Content-Type': 'application/json'
    }
    with open(speech_file, 'rb') as f:
        file = f.read()
        length = len(file)
        b64 = base64.b64encode(file)
    data = {
        "format": "wav",
        "rate": RATE,
        "channel": 1,
        "token": get_token_for_baidu(),
        "cuid": "test21wwqsq",
        "len": length,
        "speech": b64.decode(),
    }
    data = json.dumps(data)
    res = requests.post(BAIDU_SERVER_URL, headers=header, data=data)
    res = json.loads(res.text)
    return res['result'][0]


def get_audio_text(filename, url, filepath):
    content = requests.get(url).content
    file = filepath+'aac/'+filename+'.aac'
    newfile = filepath+'wav/'+filename+'.wav'
    with open(file, 'wb') as f:
        f.write(content)
    aac_version = AudioSegment.from_file(file)
    aac_version.export(newfile, format='wav')
    return change_to_text_by_baidu(newfile)


def update_text_to_mongo(collection_name):
    collection = db[collection_name]
    collection_filepath = './Resource/'+collection_name+'/audio/'
    if os.path.exists(collection_filepath):
        pass
    else:
        os.mkdir('./Resource/'+collection_name)
        os.mkdir(collection_filepath)
        os.mkdir(collection_filepath+'/aac')
        os.mkdir(collection_filepath+'/wav')
    records = collection.find({'type': 'audio', 'content': None})

    for record in records:
        text = get_audio_text(record['message_id'], record['url'], collection_filepath)
        record['content'] = text
        collection.save(record)
        print(record['message_id']+'success')


def choose_one_to_process():
    collections = db.collection_names()
    for index, collection in enumerate(collections):
        print(str(index)+':'+collection)
    id = input('请输入要处理哪个ID下的音频文件:')
    update_text_to_mongo(collections[int(id)])

choose_one_to_process()

'''
谷歌的人声识别不太精确，且没有标点符号
def change_to_text_by_google(speech_file):
    """Transcribe the given audio file asynchronously."""
    from google.cloud import speech
    from google.cloud.speech import enums
    from google.cloud.speech import types
    client = speech.SpeechClient()

    # [START migration_async_request]
    with io.open(speech_file, 'rb') as audio_file:
        content = audio_file.read()

    audio = types.RecognitionAudio(content=content)
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.FLAC,
        sample_rate_hertz=8000,
        language_code='zh-CN')

    # [START migration_async_response]
    operation = client.long_running_recognize(config, audio)
    # [END migration_async_request]

    print('Waiting for operation to complete...')
    result = operation.result(timeout=90)

    alternatives = result.results[0].alternatives
    for alternative in alternatives:
        print('Transcript: {}'.format(alternative.transcript))
        print('Confidence: {}'.format(alternative.confidence))

aac_version = AudioSegment.from_file("70e.aac", "mp4")
aac_version.export('70e.amr', format='amr')
change_to_text_by_baidu('70e.amr')
'''

