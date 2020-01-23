from django import forms
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.admin.views.decorators import staff_member_required

from .utils import (
    get_all_groups,
    get_group_members,
    get_user_gecos,
    get_user_creation_time,
)


class LdapGroupForm(forms.Form):
    add_user = forms.CharField(label="User to add", max_length=32)


class LdapUserForm(forms.Form):
    poop = forms.CharField(label="Poop", max_length=32)


@staff_member_required
def admin(request, groupname=None):
    groups = get_all_groups()
    return render(request, "ldap_admin.html", {"groups": groups})


@staff_member_required
def admin_group(request, groupname=None):
    if request.method == "POST":
        form = LdapGroupForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(
                reverse("ldap_admin_group", kwargs={"groupname": groupname})
            )
    else:
        group_members = get_group_members(groupname)
        form = LdapGroupForm()
    return render(
        request,
        "ldap_admin_group.html",
        {"form": form, "groupname": groupname, "members": group_members},
    )


@staff_member_required
def admin_user(request, username=None):
    if request.method == "POST":
        form = LdapUserForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(
                reverse("ldap_admin_group", kwargs={"groupname": groupname})
            )
    else:
        gecos = get_user_gecos(username)
        creation_time = get_user_creation_time(username)
        form = LdapUserForm()
    return render(
        request,
        "ldap_admin_user.html",
        {
            "form": form,
            "username": username,
            "gecos": gecos,
            "creation_time": creation_time,
        },
    )
