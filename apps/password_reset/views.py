from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.contrib.auth import login
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.views import View
from django import forms
from . import urls

from .tokens import account_activation_token
from apps import ldap

#import .ldap_bindings
#from forms import PasswordResetForm

REDIRECT = "csua.berkeley.edu"

class RequestPasswordResetForm(forms.Form):
    username = forms.CharField(label="Username")

class PasswordResetForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super(PasswordResetForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError(
                    "Passwords do not match!"
                    )

class ActivateAccountView(View):
    def get(self, request, username, token):
        if not ldap.utils.user_exists(username):
            user = None
        else:
            user = username

        if user is not None and account_activation_token.check_token(user, token):
            form = PasswordResetForm(data=request.POST)
            password = form.cleaned_data["password"]
            success = ldap.utils.change_password(user, password)
            print(success)
            return redirect(REDIRECT)
        else:
            # invalid link
            return render(request, 'registration/invalid.html')


def RequestPasswordResetView(request):
    if request.method == "POST":
        form = RequestPasswordResetForm(request.POST)
        print("1", form)
        username = form.cleaned_data["username"]
        email = ldap.utils.get_user_email(username)
        if email is not None:
            send_mail
            (
                'CSUA Account Password Reset Link',
                'If you did not request this, please disregard this email',
                'Reset Your password at this link:', # TODO: make link
                'django@csua.berkeley.edu',
                email,
                True
            )
            return redirect(REDIRECT)
        else:
            return redirect(REDIRECT)
    else:
        form = RequestPasswordResetForm()
        #url = urls.urlpatterns[2]
        print("2")
        print(account_activation_token)
        #print("2", form)

    return render(request, "simple_page.html", {"form": form})

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
