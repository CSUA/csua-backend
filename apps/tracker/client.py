from urllib.request import urlopen, URLError
from sys import argv
from platform import node
from os import environ
from time import sleep
from json import dumps
from random import randint
from hashlib import sha512
from time import time
import base64

try:
    from ctypes import windll
except ImportError:
    pass

DEBUG = True
if DEBUG:
    CURL_STRING = "http://localhost:8000/computers/ping/{0}/{1}"
else:
    CURL_STRING = "http://csua.berkeley.edu/computers/ping/{0}/{1}"
DELTA = 5


n = 24758167959654528007156374531915464081839760935532218683689708649238085888673119
d = 23033243203809603228118865178853745404793524490245401081883537446288476045877277


def isLogin():
    # https://msdn.microsoft.com/en-us/library/windows/desktop/ms684303(v=vs.85).aspx
    hDesktop = windll.User32.OpenDesktopW("default", 0, False, 0x0100)
    return windll.User32.SwitchDesktop(hDesktop)


def signature(msg):
    return pow(int(sha512(msg.encode()).hexdigest(), 16) % n, d, n)


def getEnv():
    env = {}
    env["delta"] = DELTA
    env["username"] = environ.get("USERNAME")
    env["host"] = node()
    env["salt"] = randint(0, 21398571238905127987)
    env["timestamp"] = int(time() * 1000)
    return env


def get_code_text(env):
    env_json = dumps(env)
    return base64.b64encode(env_json.encode("utf-8")).decode("utf-8")


def get_request_url(env):
    codeText = get_code_text(env)
    return CURL_STRING.format(codeText, signature(codeText))


def ping(request_url):
    return urlopen(request_url).read().strip()


if __name__ == "__main__":
    while True:
        if isLogin():
            env = getEnv()
            request_url = get_request_url(env)
            try:
                print("Time Remaining: ", ping(request_url))
            except URLError as e:
                print("Network Error: " + str(e))
        sleep(5)
