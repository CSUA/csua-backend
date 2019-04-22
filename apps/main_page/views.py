from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.http import HttpResponse, Http404
from django.template import TemplateDoesNotExist

from ldap3 import Connection
from ldap3.utils.conv import escape_filter_chars

LDAP_URL = "ldaps://ldap.csua.berkeley.edu"


def profile(request, username=None):
	if not username:
		if request.user.is_authenticated:
			username = request.user.username
		else:
			raise Http404("No such user!")
	with Connection(LDAP_URL) as c:
		c.search(
			"ou=People,dc=csua,dc=berkeley,dc=edu",
			"(uid={})".format(escape_filter_chars(username)),
			attributes="gecos"
		)
		if len(c.entries) == 0:
			raise Http404("No such user!")

		realname = str(c.entries[0].gecos).split(",", 1)[0]
		c.search(
			"ou=Group,dc=csua,dc=berkeley,dc=edu",
			"(memberUid={})".format(escape_filter_chars(username)),
			attributes="cn"
		)
		groups = [str(entry.cn) for entry in c.entries]

	return render(
		request,
		"profile.html", 
		{"username": username, "groups": groups, "realname": realname}
	)