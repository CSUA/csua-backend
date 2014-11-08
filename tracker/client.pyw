from urllib2 import urlopen
from sys import argv
from platform import node
from os import environ
from time import sleep
from ctypes import windll
from json import dumps
from random import randint
from hashlib import sha512
from time import time
import base64
 
CURL_STRING = "http://csua.berkeley.edu/computers/ping/{0}/{1}"
DELTA = 5

 
n=24758167959654528007156374531915464081839760935532218683689708649238085888673119L
d=23033243203809603228118865178853745404793524490245401081883537446288476045877277L

def isLogin():
  hDesktop = windll.User32.OpenDesktopA("default",0,False,0x0100)
  return windll.User32.SwitchDesktop(hDesktop)

def signature(msg):
  return pow(int(sha512(msg).hexdigest(),16) % n,d,n)

def getEnv():
  env={}
  env["delta"]=DELTA
  env["username"]=environ.get("USERNAME")
  env["host"]=node()
  env["salt"]=randint(0,21398571238905127987)
  env["timestamp"]=int(time()*1000)
  return dumps(env)

while True:
  if isLogin():
    codeText = base64.b64encode(getEnv())
    request = CURL_STRING.format(codeText,signature(codeText))
    try:
      print "Time Remaining: ", urlopen(request).read().strip()
    except:
      print "Network Error"
  sleep(5)
