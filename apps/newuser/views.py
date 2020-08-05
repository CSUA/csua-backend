from os import mkdir
import pathlib
import logging
import subprocess

from django.test import override_settings
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.urls import reverse
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.views import View
from django.template.loader import render_to_string

from .forms import NewUserForm, RemoteEmailRequestForm, NewUserFormOfficerVerified
from .utils import valid_password
from .tokens import newuser_token_generator

from apps.ldap.utils import create_new_user, validate_officer, email_exists

usernameWhitelist = set(".-_")
emailWhitelist = set("@+").union(usernameWhitelist)
logger = logging.getLogger(__name__)

newuser_script = pathlib.Path(__file__).parent.absolute() / "config_newuser"


def index(request):
    if request.method == "POST":
        form = NewUserFormOfficerVerified(request.POST)
        context = {"form": form, "remote": False}
        if form.is_valid():
            if validate_officer(
                form.cleaned_data["officer_username"],
                form.cleaned_data["officer_password"],
            ):
                return _make_newuser(request, form, context)
            else:
                messages.error(request, "Officer credentials are incorrect!")
        else:
            messages.error(
                request, "Form is invalid! Please contact #website for assistance."
            )
    else:
        form = NewUserFormOfficerVerified()
        context = {"form": form, "remote": False}

    return render(request, "newuser.html", context)


def remote_newuser(request, email, token):
    if newuser_token_generator.check_token(email, token):
        if request.method == "POST":
            form = NewUserForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data["email"]
                return _make_newuser(
                    request,
                    form,
                    {"email": email, "form": form, "token": token, "remote": True},
                )
        else:
            form = NewUserForm()
        return render(
            request,
            "newuser.html",
            {"email": email, "form": form, "token": token, "remote": True},
        )
    else:
        messages.error(
            request,
            "Token is invalid! Either the token and email don't match or you've waited too long to open the link.",
        )
        return render(request, "newuser.html", {"remote": True, "form": None})


def _make_newuser(request, form, context):
    """Creates a new user in LDAP and runs config_newuser"""
    enroll_jobs = "true" if form.cleaned_data["enroll_jobs"] else "false"
    success, uid = create_new_user(
        form.cleaned_data["username"],
        form.cleaned_data["full_name"],
        form.cleaned_data["email"],
        form.cleaned_data["student_id"],
        form.cleaned_data["password"],
    )
    if success:
        exit_code = subprocess.call(
            [
                "sudo",
                newuser_script,
                form.cleaned_data["username"],
                form.cleaned_data["email"],
                uid,
                enroll_jobs,
            ]
        ).returncode
        if exit_code == 0:
            logger.info("New user created: {0}".format(uid))
            return render(request, "create_success.html")
        else:
            messages.error(
                request,
                "Account created, but failed to run config_newuser. Please contact #website for assistance.",
            )
            logger.error("Account created, but failed to run config_newuser.")
            # TODO: delete user to roll back the newuser operation.
    else:
        if uid == -1:
            messages.error(
                request,
                "Internal error, failed to bind as newuser. Please report this to #website.",
            )
        else:
            messages.error(request, "Your username is already taken.")

    return render(request, "newuser.html", context)


def request_remote_newuser(request):
    """Sends an email to the user with a link to newuser-remote"""
    if request.method == "POST":
        form = RemoteEmailRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            token = newuser_token_generator.make_token(email)
            html_message = render_to_string(
                "newuser_email.html", {"email": email, "token": token}
            )
            if not email_exists(email):
                if email.endswith("@berkeley.edu"):
                    send_mail(
                        subject="CSUA New User Creation Link",
                        message=strip_tags(html_message),
                        html_message=html_message,
                        from_email="django@csua.berkeley.edu",
                        recipient_list=[email],
                    )
                    messages.info(request, "Email sent!")
                else:
                    messages.error(
                        request,
                        "Email must be @berkeley.edu. If please contact us if this is an issue.",
                    )
            else:
                messages.error(request, "Email exists in system!")
    else:
        form = RemoteEmailRequestForm()
    return render(request, "newuserremoterequest.html", {"form": form})
