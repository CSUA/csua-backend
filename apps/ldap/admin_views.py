from django import forms
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required

from .utils import (
    add_group_member,
    remove_group_members,
    get_all_groups,
    get_group_members,
    get_officers,
    get_user_gecos,
    get_user_creation_time,
    user_exists,
)

from apps.db_data.models import (
    Semester,
    PolitburoMembership,
    Politburo,
    Officer,
    Officership,
)


class LdapGroupForm(forms.Form):
    add_user = forms.CharField(label="User to add", max_length=32)
    verify_user = forms.BooleanField(
        label="Verify that username exists", initial=True, required=False
    )


class LdapUserForm(forms.Form):
    # WIP
    poop = forms.CharField(label="Poop", max_length=32)


@staff_member_required
def admin(request, groupname=None):
    if "user" in request.GET:
        return HttpResponseRedirect(
            reverse("ldap_admin_user", kwargs={"username": request.GET.get("user")})
        )
    groups = get_all_groups()
    relevant_groups = [
        "root",
        "officers",
        "prosp-officers",
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
    form = LdapGroupForm()
    group_members = get_group_members(groupname)
    if request.method == "POST":
        if groupname == "root":
            messages.error(request, "I'm sorry Dave, I'm afraid I can't do that.")

        elif "add_user" in request.POST:
            form = LdapGroupForm(request.POST)
            if form.is_valid():
                user_to_add = form.cleaned_data["add_user"]
                if not form.cleaned_data["verify_user"] or user_exists(user_to_add):
                    success, message = add_group_member(groupname, user_to_add)
                    if success:
                        messages.info(
                            request,
                            "Successfully added {0} to {1}".format(
                                user_to_add, groupname
                            ),
                        )
                        return HttpResponseRedirect(
                            reverse("ldap_admin_group", kwargs={"groupname": groupname})
                        )
                    else:
                        messages.error(request, message)
                else:
                    messages.error(
                        request, "User {0} does not exist".format(user_to_add)
                    )

        elif "do_delete" in request.POST:
            users_to_remove = [
                user[len("delete_") :]
                for user in request.POST
                if user.startswith("delete_")
            ]
            if users_to_remove:
                success, message = remove_group_members(groupname, users_to_remove)
                if success:
                    for user in users_to_remove:
                        messages.info(
                            request,
                            "Successfully removed {0} from {1}".format(user, groupname),
                        )
            return HttpResponseRedirect(
                reverse("ldap_admin_group", kwargs={"groupname": groupname})
            )

        elif "do_verify_all" in request.POST:
            invalid_usernames = []
            for username in group_members:
                if not user_exists(username):
                    invalid_usernames.append(username)
            if invalid_usernames:
                for invalid_username in invalid_usernames:
                    messages.error(
                        request, "{0} is not a valid username".format(invalid_username)
                    )
            else:
                messages.info(request, "All usernames are valid")
            return HttpResponseRedirect(
                reverse("ldap_admin_group", kwargs={"groupname": groupname})
            )
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
            messages.info(request, form.cleaned_data["poop"])
            return HttpResponseRedirect(
                reverse("ldap_admin_user", kwargs={"username": username})
            )
    else:
        form = LdapUserForm()
    gecos = get_user_gecos(username)
    creation_time = get_user_creation_time(username)
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


@staff_member_required
def admin_validate(request):
    semester = Semester.objects.get(current=True)
    roles_ldap = {}
    roles_sql = {}
    for ldap_group, position in [
        ["president"] * 2,
        ["vpindrel", "indrel"],
        ["vptech", "vp"],
        ["secretary", "treasurer"],
        ["internalevents"] * 2,
        ["externalevents"] * 2,
        ["outreach"] * 2,
    ]:
        roles_ldap[position] = get_group_members(ldap_group)
        roles_sql[position] = list(
            pbm.person.username
            for pbm in PolitburoMembership.objects.filter(
                politburo__position=position, semester=semester
            )
        )
    roles_ldap["officers"] = get_officers()
    roles_sql["officers"] = [
        o.officer.username for o in Officership.objects.filter(semester=semester)
    ]
    roles = {}
    for role in roles_ldap.keys():
        ldap = roles_ldap[role]
        sql = roles_sql[role]
        common = set(ldap) & set(sql)
        sql_only = set(sql) - set(ldap)
        ldap_only = set(ldap) - set(sql)
        roles[role] = [
            sorted(list(username_set)) for username_set in [common, sql_only, ldap_only]
        ]

    return render(request, "ldap_admin_validate.html", {"roles": roles})
