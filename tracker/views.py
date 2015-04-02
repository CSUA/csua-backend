# Create your views here.
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render
from hashlib import sha512
import base64
from json import loads, dumps
from datetime import datetime
from time import sleep, time


n=24758167959654528007156374531915464081839760935532218683689708649238085888673119L
e=1792365660034190580552551249494619970913188709474773556763388672115404129751573L

userdb={}
hostdb={}
DAILY_QUOTA=3600*2
lastreset = datetime.today().day

twitchUsers = {'jaze': 'alxjaze'}

def currTimeMillis():
    return int(time()*1000)

def resetAccounts():
    global lastreset
    if datetime.today().day != lastreset:
        lastreset = datetime.today().day
        for user in userdb:
            userdb[user]["timeRemaining"] = DAILY_QUOTA

class User():
    def __init__(self, username, time, lastPing, twitchUsername):
      self.username=username
      self.time=time
      self.lastPing=lastPing
      self.twitch=twitchUsername

def getUsers():
    out = []
    for username in userdb:
        out.append(User(username, userdb[username]['timeRemaining'], userdb[username]['lastPing'], (None if username not in twitchUsers else twitchUsers[username]) ))
    return out

class Computer():
    def __init__(self, host, open, user, time):
      self.host=host
      self.open=open
      self.user=user
      self.time=time

    @property
    def twitchUser(self):
      return (None if self.user not in twitchUsers else twitchUsers[self.user])

def getComputers():
    resetAccounts()
    out = []
    for host in hostdb:
        timestamp = hostdb[host]["local_timestamp"]
        if (currTimeMillis() - timestamp) < 10000:
            out.append(Computer(host,
                                userdb[hostdb[host]["user"]]["timeRemaining"] <= 0,
                                str(hostdb[host]["user"]),
                                userdb[hostdb[host]["user"]]["timeRemaining"]))
        else:
            out.append(Computer(host,True,"N/A",-1))
    return out

def index(request):
    template = loader.get_template("computers.html")
    context = RequestContext(request, {
        'computers':getComputers(),
        'users':getUsers(),
        })
    return HttpResponse(template.render(context))

def ping(request, codeText = None, signature = None):
    #Validate signature
    if not signature.isdigit() or pow(int(signature),e,n) != int(sha512(codeText).hexdigest(),16) % n:
        return HttpResponse("Bad Request.")
    codeText = base64.b64decode(codeText)
    resetAccounts()
    data = loads(codeText)
    delta = data['delta']
    username = data['username']
    host = data['host']
    timestamp = data['timestamp']
    if host in hostdb and hostdb[host.lower()]["foreign_timestamp"] >= timestamp:
        return HttpResponse("Bad Request, stupid hacker.")
    hostdb[host.lower()] = {
        "foreign_timestamp":timestamp,
        "local_timestamp":currTimeMillis(),
        "user":username
        }
    if username not in userdb:
        userdb[username]={
            "timeRemaining":DAILY_QUOTA,
            "lastPing":currTimeMillis(),
            }
    else:
        now = currTimeMillis()
        if now - userdb[username]["lastPing"] <= 2*1000*delta:
            userdb[username]["timeRemaining"]-=int((now - userdb[username]["lastPing"])/1000)
            userdb[username]["lastPing"]=now
    return HttpResponse(str(userdb[username]["timeRemaining"]))