from django import forms
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required

from .utils import (
    add_group_member,
    remove_group_members,
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
    relevant_groups = [
        "root",
        "officers",
        "excomm",
        "president",
        "vptech",
        "vpindrel",
        "outreach",
        "externalevents",
        "internalevents",
        "secretary",
    ]
    return render(
        request,
        "ldap_admin.html",
        {"groups": groups, "relevant_groups": relevant_groups},
    )


@staff_member_required
def admin_group(request, groupname=None):
    group_members = get_group_members(groupname)
    if request.method == "POST":
        if groupname == "root":
            messages.error(request, "I'm sorry Dave, I'm afraid I can't do that.")
        elif "add_user" in request.POST:
            form = LdapGroupForm(request.POST)
            if form.is_valid():
                success, message = add_group_member(
                    groupname, form.cleaned_data["add_user"]
                )
                if not success:
                    messages.error(request, message)
        elif "do_delete" in request.POST:
            users_to_remove = [
                user[len("delete_") :]
                for user in request.POST
                if user.startswith("delete_")
            ]
            if users_to_remove:
                success, message = remove_group_members(groupname, users_to_remove)
        return HttpResponseRedirect(
            reverse("ldap_admin_group", kwargs={"groupname": groupname})
        )

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
