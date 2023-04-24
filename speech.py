import requests
import os
import uuid
import settings

key = settings.azure_speech_key
region = settings.azure_speech_region

cd = os.getcwd()
sep = os.path.sep


def checkLang(lang):
    if (lang is None or len(lang) == 0):
        return "zh-CN"
    else:
        return lang


def stt(ogg_path, lang):
    url = f'https://{region}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1?language={checkLang(lang)}'

    with open(ogg_path, 'rb') as f:
        audio_data = f.read()
    os.remove(ogg_path)

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'audio/ogg; codecs=opus',
        'Ocp-Apim-Subscription-Key': key
    }
    response = requests.post(url, headers=headers, data=audio_data)

    if response.status_code == 200:
        json = response.json()
        text = json['DisplayText']
        print(json)
        return text
    else:
        print('Failed to recognize speech: ' + response.text)
        return "Failed to recognize speech"


def getTTSPath(name):
    return f"{cd}{sep}files{sep}tts{sep}{name}.mp3"


def tts(text, lang):
    vlang, vGender, vName = getVoice(checkLang(lang))
    url = f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1"
    headers = {
        'Content-Type': 'application/ssml+xml',
        'Ocp-Apim-Subscription-Key': key,
        'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3',
    }
    response = requests.post(url, headers=headers,
                             data=plainText2SsmlXml(text, lang=vlang, gender=vGender, name=vName))
    if response.status_code == 200:
        data = response.content
        name = str(uuid.uuid4())
        with open(getTTSPath(name), 'wb') as f:
            f.write(data)
            f.close()
        return name
    else:
        return "Failed to synthesize speech"


def plainText2SsmlXml(text, lang, gender, name):
    return f"<speak version='1.0' xml:lang='{lang}'><voice xml:lang='{lang}' xml:gender='{gender}' name='{name}'>{text}</voice></speak>".encode("utf-8")


def getVoice(lang):
    lang = checkLang(lang)
    if (lang == "zh-CN"):
        return (lang, "Male", "zh-CN-YunxiNeural")
    elif (lang == "en-US"):
        return (lang, "Female", "en-US-JennyMultilingualNeural")
    elif (lang == "ru-RU"):
        return (lang, "Male", "ru-RU-DmitryNeural")
    elif (lang == "de-DE"):
        return (lang, "Male", "de-DE-ConradNeural")
    elif (lang == "it-IT"):
        return (lang, "Female", "it-IT-IsabellaNeural")
    elif (lang == "fr-FR"):
        return (lang, "Male", "fr-FR-HenriNeural")
    elif (lang == "ko-KR"):
        return (lang, "Female", "ko-KR-JiMinNeural")
    elif (lang == "ja-JP"):
        return (lang, "Female", "ja-JP-NanamiNeural")
    elif (lang == "es-ES"):
        return (lang, "Male", "es-ES-ArnauNeural")
    else:
        return ("zh-CN", "Male", "zh-CN-YunxiNeural")
