# Create your views here.
from django.http import HttpResponse, Http404
from django.template import RequestContext, loader
from django.shortcuts import render

from hashlib import sha512
import base64
from json import loads, dumps
from datetime import datetime
from time import sleep, time
from os import path

import magic
# Python wrapper for libmagic--gets filetype

def get_resource_uri(uri):
  print(uri)
  if not path.exists(uri):
    return False
  if path.isdir(uri):
    if not path.exists(path.join(uri, "index.html")):
      return False
    else:
      return path.join(uri, "index.html")
  else:
    return uri

def serve(request, username = None, path = None):
  resource_uri = get_resource_uri("/home/{0}/public_html/{1}".format(username, path))
  if not resource_uri:
    raise Http404("Could not find the requested file")
  mime = magic.from_file(resource_uri, mime=True)
  return HttpResponse(open(resource_uri,'rb').read(), content_type=mime)
