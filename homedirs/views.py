# Create your views here.
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render
from hashlib import sha512
import base64
from json import loads, dumps
from datetime import datetime
from time import sleep, time
from os import path

def get_resource_uri(uri):
  print uri
  if not path.exists(uri):
    return False
  if path.isdir(uri):
    if not path.exists(path.join(uri,"index.html")):
      return False
    else:
      return path.join(uri,"index.html")
  else:
    return uri

def serve(request, username = None, path = None):
  resource_uri = get_resource_uri("/home/{0}/public_html/{1}".format(username, path))
  if resource_uri:
    return HttpResponse(open(resource_uri).read())
  else:
    #raise Http404
    return HttpResponse("404 Not Found. Sorry for the inconvenience, but private static websites are currently unavailable.")
