import threading
import openai
import settings

kp1 = [settings.openai_org, settings.openai_key]


kps = [kp1]


def rollKey():
    kp = kps[0]
    openai.organization = kp[0]
    openai.api_key = kp[1]


def chat(context, maxContextCount=9):
    if (len(context) > maxContextCount):
        context.pop(1)
    rollKey()
    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=context
    )
    content = res["choices"][0]["message"]["content"]
    response = {"role": "assistant", "content": content}
    context.append(response)
    return response


lock = threading.Lock()
contextKeeper = {}


def getContext(token):
    if (token is None or len(token) == 0):
        return
    with lock:
        if token in contextKeeper:
            return contextKeeper[token]
        else:
            ctx = []
            contextKeeper[token] = ctx
            return ctx
