from django.views.decorators.csrf import csrf_exempt
from slack_bolt.adapter.django import SlackRequestHandler

from .client import app

if app is not None:
    handler = SlackRequestHandler(app)
else:
    handler = None


@csrf_exempt
def events(request):
    if handler is not None:
        return handler.handle(request)
