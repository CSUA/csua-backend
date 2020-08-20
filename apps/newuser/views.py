import shlex
import pathlib
import logging
import subprocess

from django.shortcuts import render
from django.contrib import messages
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.views.decorators.debug import sensitive_variables, sensitive_post_parameters

from .forms import NewUserForm, RemoteEmailRequestForm, NewUserFormOfficerVerified
from .tokens import newuser_token_generator

from apps.ldap.utils import create_new_user, delete_user, validate_officer, email_exists

usernameWhitelist = set(".-_")
emailWhitelist = set("@+").union(usernameWhitelist)
logger = logging.getLogger(__name__)

newuser_script = pathlib.Path(__file__).parent.absolute() / "config_newuser"


@sensitive_post_parameters("password", "officer_password")
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
            messages.error(request, "Form is invalid!")
    else:
        form = NewUserFormOfficerVerified()
        context = {"form": form, "remote": False}

    return render(request, "newuser.html", context)


@sensitive_post_parameters("password")
def remote_newuser(request, email, token):
    if newuser_token_generator.check_token(email, token):
        if request.method == "POST":
            form = NewUserForm(request.POST)
            if form.is_valid():
                form_email = form.cleaned_data["email"]
                if form_email == email:
                    return _make_newuser(
                        request,
                        form,
                        {"email": email, "form": form, "token": token, "remote": True},
                    )
                else:
                    messages.error(request, "You must use the same email, try again")
                    data = form.cleaned_data
                    data["email"] = email
                    form = NewUserForm(initial=data)
        else:
            form = NewUserForm(initial={"email": email})
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
    """Creates a new user in LDAP and runs config_newuser
    if config_newuser fails, the user account is deleted to prevent the user
    account from being in limbo."""
    enroll_jobs = "true" if form.cleaned_data["enroll_jobs"] else "false"
    success, uid = create_new_user(
        form.cleaned_data["username"],
        form.cleaned_data["full_name"],
        form.cleaned_data["email"],
        form.cleaned_data["student_id"],
        form.cleaned_data["password"],
    )
    email = shlex.quote(form.cleaned_data["email"])
    username = shlex.quote(form.cleaned_data["username"])
    if success:
        config_newuser_process = subprocess.run(
            ["sudo", str(newuser_script), username, email, str(uid), enroll_jobs],
            shell=True,
        )
        if config_newuser_process.returncode == 0:
            logger.info(f"New user created: {username}")
            return render(request, "create_success.html")
        else:
            messages.error(
                request,
                "Failed to run config_newuser. Please contact #website on slack for assistance.",
            )
            if delete_user(form.cleaned_data["username"]):
                logger.error(
                    f"Failed to run config_newuser. Username: {username} Email: {email}"
                )
            else:
                logger.error(
                    f"Failed to run config_newuser and failed to delete user. Username: {username} Email: {email}"
                )
    else:
        if uid == -1:
            logger.error(
                f"Failed to bind as newuser. Username: {username} Email: {email}"
            )
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
