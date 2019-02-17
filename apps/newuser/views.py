from os import mkdir, system

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.contrib import messages

from . import ldap_bindings
from .forms import NewUserForm

usernameWhitelist = set(".-_")
emailWhitelist = set("@+").union(usernameWhitelist)


def index(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            if ldap_bindings.ValidateOfficer(
                form.cleaned_data["officer_username"],
                form.cleaned_data["officer_password"],
            ):
                enroll_jobs = "true" if form.cleaned_data["enroll_jobs"] else "false"
                status, uid = ldap_bindings.NewUser(
                    form.cleaned_data["username"],
                    form.cleaned_data["full_name"],
                    form.cleaned_data["email"],
                    form.cleaned_data["student_id"],
                    form.cleaned_data["password"],
                )
                print("UID:{0}".format(uid))
                if not status:
                    return render(
                        request,
                        "create_failure.html",
                        {"error": "Your username is already taken."},
                    )
                else:
                    system(
                        "sudo /webserver/CSUA-backend/newuser/config_newuser {0} {1} {2} {3}".format(
                            form.cleaned_data["username"],
                            form.cleaned_data["email"],
                            uid,
                            form.cleaned_data["enroll_jobs"],
                        )
                    )
                    return render(request, "create_success.html")
            else:
                messages.error()
        else:
            return render(request, "newuser.html", {"form": form})
    else:
        form = NewUserForm()

    return render(request, "newuser.html", {"form": form})


def validUsername(username):
    """
  This helper function takes in a string (the username) and checks if it has whitelisted characters. 
  If there's a character that is not whitelisted, it is not a valid username. In other words, the 
  username must be composed of whitelisted characters. 
  """
    for character in username:
        if not character.isalnum() and character not in usernameWhitelist:
            return False
    return True


def validEmail(email):
    """
  Similar to validUsername, but for emails!
  """
    for character in email:
        if not character.isalnum() and character not in emailWhitelist:
            return False
    return True


def validPassword(password):
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
