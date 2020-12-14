from django.views.decorators.csrf import csrf_exempt
from slack_bolt.adapter.django import SlackRequestHandler

from .client import app

handler = SlackRequestHandler(app)


@csrf_exempt
def events(request):
    return handler.handle(request)
