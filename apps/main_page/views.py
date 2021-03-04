from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.template import TemplateDoesNotExist
from django.views.generic.base import TemplateView
from ldap3 import Connection
from ldap3.utils.conv import escape_filter_chars

from apps.ldap.utils import get_user_groups, get_user_realname


def profile(request, username=None):
    if not username:
        if request.user.is_authenticated:
            username = request.user.username
        else:
            raise Http404("No such user!")
    groups = get_user_groups(username)
    realname = get_user_realname(username)
    return render(
        request,
        "profile.html",
        {"username": username, "groups": groups, "realname": realname},
    )
