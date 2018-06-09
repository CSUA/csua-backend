import base64
import mimetypes
from datetime import datetime
from hashlib import sha512
from json import dumps, loads
from os import path
from time import sleep, time

# Python wrapper for libmagic--gets filetype
import magic
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.template import RequestContext, loader

mimetypes.init()

def get_resource_uri(uri):
    print(uri)
    if not path.exists(uri):
        return False
    if path.isdir(uri):
        if not path.exists(path.join(uri, 'index.html')):
            return False
        else:
            return path.join(uri, 'index.html')
    else:
        return uri

def check_sanity(username, path):
    return '..' not in path

def serve(request, username=None, path=None):
    uri = '/home/{0}/public_html/{1}'.format(username, path)
    resource_uri = get_resource_uri(uri)
    if not resource_uri or not check_sanity(username, path):
        raise Http404('Could not find the requested file: {0}'.format(uri))
    mime = magic.from_file(resource_uri, mime=True)
    mime_2 = mimetypes.guess_type(resource_uri)[0]
    if mime == 'text/plain':
        # python-magic thinks js and css files are text/plain
        mime = mime_2
    with open(resource_uri, 'rb') as f:
        return HttpResponse(f.read(), content_type=mime)
