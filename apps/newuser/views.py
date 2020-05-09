from os import mkdir, system
import pathlib
import logging

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.contrib import messages

from apps.ldap.utils import create_new_user, validate_officer
from .forms import NewUserForm

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


def valid_password(password):
    """
  The password must be at least nine characters long. Also, it must include characters from 
  two of the three following categories:
  -alphabetical
  -numerical
  -punctuation/other
  """
    punctuation = set("""!@#$%^&*()_+|~-=\`{}[]:";'<>?,./""")
    alpha = False
    num = False
    punct = False

    if len(password) < 9:
        return False

    for character in password:
        if character.isalpha():
            alpha = True
        if character.isdigit():
            num = True
        if character in punctuation:
            punct = True
    return (alpha + num + punct) >= 2
