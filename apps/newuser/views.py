from os import mkdir, system
import pathlib
import logging
import re

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

from apps.ldap.utils import create_new_user, validate_officer
from .forms import NewUserForm, RemoteEmailRequestForm, NewUserRemoteForm
from .utils import valid_password
from .tokens import newuser_token_generator

usernameWhitelist = set(".-_")
emailWhitelist = set("@+").union(usernameWhitelist)
logger = logging.getLogger(__name__)

newuser_script = pathlib.Path(__file__).parent.absolute() / "config_newuser"


def index(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            if valid_password(form.cleaned_data["password"]):
                if validate_officer(
                    form.cleaned_data["officer_username"],
                    form.cleaned_data["officer_password"],
                ):
                    enroll_jobs = (
                        "true" if form.cleaned_data["enroll_jobs"] else "false"
                    )
                    success, uid = create_new_user(
                        form.cleaned_data["username"],
                        form.cleaned_data["full_name"],
                        form.cleaned_data["email"],
                        form.cleaned_data["student_id"],
                        form.cleaned_data["password"],
                    )
                    if success:
                        exit_code = system(
                            f"sudo {newuser_script}"
                            " {form.cleaned_data['username']}"
                            " {form.cleaned_data['email']}"
                            " {uid}"
                            " {form.cleaned_data['enroll_jobs']}"
                        )
                        if exit_code == 0:
                            logger.info("New user created: {0}".format(uid))
                            return render(request, "create_success.html")
                        else:
                            messages.error(
                                request,
                                "Account created, but failed to run config_newuser. Please contact #website for assistance.",
                            )
                            logger.error(
                                "Account created, but failed to run config_newuser."
                            )
                            # TODO: delete user to roll back the newuser operation.
                    else:
                        if uid == -1:
                            messages.error(
                                request,
                                "Internal error, failed to bind as newuser. Please report this to #website.",
                            )
                        else:
                            messages.error(request, "Your username is already taken.")
                else:
                    messages.error(request, "Incorrect officer credentials.")
            else:
                messages.error(request, "Password must meet requirements.")
        else:
            messages.error(request, "Form is invalid.")
    else:
        form = NewUserForm()

    return render(request, "newuser.html", {"form": form})


class RemoteCreateNewUserView(View):
    def post(self, request, token):
        form = NewUserRemoteForm(request.POST)
        if form.is_valid():
            if valid_password(form.cleaned_data["password"]):
                enroll_jobs = "true" if form.cleaned_data["enroll_jobs"] else "false"
                success, uid = create_new_user(
                    form.cleaned_data["username"],
                    form.cleaned_data["full_name"],
                    form.cleaned_data["email"],
                    form.cleaned_data["student_id"],
                    form.cleaned_data["password"],
                )
                if success:
                    exit_code = system(
                        f"sudo {newuser_script}"
                        " {form.cleaned_data['username']}"
                        " {form.cleaned_data['email']}"
                        " {uid}"
                        " {form.cleaned_data['enroll_jobs']}"
                    )
                    if exit_code == 0:
                        logger.info("New user created: {0}".format(uid))
                        return render(request, "create_success.html")
                    else:
                        messages.error(
                            request,
                            "Account created, but failed to run config_newuser. Please contact #website for assistance.",
                        )
                        logger.error(
                            "Account created, but failed to run config_newuser."
                        )
                else:
                    if uid == -1:
                        messages.error(
                            request,
                            "Internal error, failed to bind as newuser. Please report this to #website.",
                        )
                    else:
                        messages.error(request, "Your username is already taken.")
            else:
                messages.error(request, "Password must meet requirements.")
        else:
            messages.error(request, "Form is invalid.")
            context = {"form": form, "token": token}
            return render(request, "newuserremote.html", context)

    def get(self, request, token):
        form = NewUserRemoteForm()
        context = {"form": form, "token": token}
        return render(request, "newuserremote.html", context)


def get_html_message(email, token):
    return render_to_string("newuser_email.html", {"email": email, "token": token})


# This is for when the newuser is remote
@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.filebased.EmailBackend",
    EMAIL_FILE_PATH="test_messages",
)
def remote_newuser(request):
    if request.method == "POST":
        form = RemoteEmailRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            token = newuser_token_generator.make_token(email)
            html_message = get_html_message(email, token)
            if valid_berkeley_email(email):
                send_mail(
                    subject="CSUA New User Creation Link",
                    message=strip_tags(html_message),
                    html_message=html_message,
                    from_email="django@csua.berkeley.edu",
                    recipient_list=[email],
                )
                return redirect(reverse("remote"))
            else:
                return redirect(reverse("remote"))
    else:
        form = RemoteEmailRequestForm()
        return render(request, "newuserremoterequest.html", {"form": form})


def valid_berkeley_email(email: str):
    regex = "^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"
    if not re.search(regex, email):
        return False
    if email.split("@", 1)[1] != "berkeley.edu":
        return False
    return True
