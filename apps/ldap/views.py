from django.http import HttpResponse
from django.shortcuts import render
from ldap3.utils.conv import escape_filter_chars

from .utils import get_group_members, get_root, get_user_gecos, get_user_groups


def group(request, groupname=None):
    groupname = escape_filter_chars(groupname)
    resp = "\n".join(get_group_members(groupname))
    return HttpResponse(resp, content_type="text/plain")


def user(request, username=None):
    username = escape_filter_chars(username)
    resp = get_user_gecos(username)
    return HttpResponse(resp, content_type="text/plain")


def user_groups(request, username=None):
    username = escape_filter_chars(username)
    resp = "\n".join(get_user_groups(username))
    return HttpResponse(resp, content_type="text/plain")
