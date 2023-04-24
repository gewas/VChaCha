from flask import (Flask, render_template, request, make_response,
                   send_from_directory, send_file)
from gevent.pywsgi import WSGIServer
from gevent import monkey
monkey.patch_all()
import os
import time
import random
import speech
import subprocess
import gpt
import json
import uuid
import threading
import wc

# os.environ["http_proxy"] = "http://127.0.0.1:1080"
# os.environ["https_proxy"] = "http://127.0.0.1:1080"

cd = os.getcwd()
sep = os.path.sep
app = Flask(__name__)


def webm2ogg(webm_path):
    ogg_path = f"{cd}{sep}files{sep}stt{sep}{str(time.time_ns())+str(random.randint(100, 999))}.ogg"
    # webm2ogg
    subprocess.run(['ffmpeg', '-i', webm_path, ogg_path])
    os.remove(webm_path)
    return ogg_path


def getUUID():
    random_uuid = uuid.uuid4()
    return str(random_uuid)


@app.route('/')
def view_index():
    text = '/ pid  %d , <br> threading %s  <br> request  %d ' % (
        os.getpid(), threading.current_thread().name, id(request))
    print(text)
    return render_template('index.html')


@app.route('/chatroom')
def view_chatroom():
    text = '/chatroom pid  %d , <br> threading %s  <br> request  %d ' % (
        os.getpid(), threading.current_thread().name, id(request))
    print(text)
    return render_template('chatroom.html')

@app.route('/wordclouds')
def view_wordcloud():
    text = '/wordclouds pid  %d , <br> threading %s  <br> request  %d ' % (
        os.getpid(), threading.current_thread().name, id(request))
    print(text)
    return render_template('wordclouds.html')


@app.route('/favicon.ico')
def res_favicon():
    text = '/favicon.ico pid  %d , <br> threading %s  <br> request  %d ' % (
        os.getpid(), threading.current_thread().name, id(request))
    print(text)
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/api/wordclouds", methods=['POST'])
def api_word_cloud():
    text = '/api/wordclouds pid  %d , <br> threading %s  <br> request  %d ' % (
        os.getpid(), threading.current_thread().name, id(request))
    print(text)
    json = request.get_json()
    print(json)
    path = f"{cd}{sep}files{sep}image{sep}wordclouds-{getUUID()}.jpg"
    wc.word_cloud(json["text"], path)
    return send_file(path, mimetype='image/jpeg')


@app.route("/api/session")
def api_session():
    text = '/api/session pid  %d , <br> threading %s  <br> request  %d ' % (
        os.getpid(), threading.current_thread().name, id(request))
    print(text)
    token = request.headers.get('token')
    if token == "null" or token is None or len(token) == 0:
        token = getUUID()
    resp = make_response(json.dumps(gpt.getContext(token)))
    resp.headers['Content-Type'] = 'application/json'
    resp.headers['Cache-Control'] = 'no-cache'
    resp.headers['token'] = token
    return resp


@app.route("/static/<name>")
def res_static(name):
    text = '/static/%s pid  %d , <br> threading %s  <br> request  %d ' % (
        name, os.getpid(), threading.current_thread().name, id(request))
    print(text)
    mimetype = None
    if (str(name).endswith(".js")):
        mimetype = "application/javascript"
    elif (str(name).endswith(".css")):
        mimetype = "text/css"
    else:
        mimetype = "application/octet-stream"
    return send_file(f'{cd}{sep}static{sep}{name}', mimetype=mimetype)


@app.route("/audio/<name>")
def res_audio(name):
    text = '/audio/%s pid  %d , <br> threading %s  <br> request  %d ' % (
        name, os.getpid(), threading.current_thread().name, id(request))
    print(text)
    return send_file(speech.getTTSPath(name), mimetype='audio/mpeg')


@app.route('/api/stt', methods=['POST'])
def api_stt():
    text = '/api/stt pid  %d , <br> threading %s  <br> request  %d ' % (
        os.getpid(), threading.current_thread().name, id(request))
    print(text)
    lang = request.headers.get('speech')
    file = request.files['audio']

    def stt_internal():
        webm_path = f"{cd}{sep}tmp{sep}{str(time.time_ns())+str(random.randint(100, 999))}.webm"
        with open(webm_path, 'wb') as f:
            f.write(file.read())
        ogg_path = webm2ogg(webm_path)
        text = speech.stt(ogg_path, lang)
        return text

    text = stt_internal()

    resp = make_response(text)
    resp.headers['Content-Type'] = 'text/plain'
    return resp


@app.route("/api/chat", methods=['POST'])
def api_chat():
    text = '/api/chat pid  %d , <br> threading %s  <br> request  %d ' % (
        os.getpid(), threading.current_thread().name, id(request))
    print(text)

    token = request.headers.get('token')
    lang = request.headers.get('speech')
    data = request.get_json()

    def chat_internal():
        query = data["query"]
        context = gpt.getContext(token)
        context.append({"role": "user", "content": query})
        response = gpt.chat(context)
        print(f"response to [{query}]: {response}")
        return response

    response = chat_internal()

    resp = make_response(json.dumps(response))
    content = response["content"]
    if (lang is not None and len(lang) > 0 and len(content) <= 500):
        tts = speech.tts(content, lang)
        resp.headers['tts'] = tts
    resp.headers['token'] = token
    resp.headers['Content-Type'] = 'application/json'
    return resp


if __name__ == '__main__':
    WSGIServer(("0.0.0.0", 5000), app).serve_forever()

subprocess.run(['apt-get', 'install', '-y', 'ffmpeg'])
