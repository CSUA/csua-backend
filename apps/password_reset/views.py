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

#import .ldap_bindings
#from forms import PasswordResetForm

REDIRECT = "csua.berkeley.edu"

class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.profile.email_confirmed = True
            user.save()
            login(request, user)
            return redirect('profile')
        else:
            # invalid link
            return render(request, 'registration/invalid.html')

class PasswordResetForm(forms.Form):
    username = forms.CharField(label="Username")
    email = forms.CharField(label="Berkeley Email Address")

def PasswordResetView(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        print("1", form)
        username = form.cleaned_data["username"]
        email = form.cleaned_data["email"]
        """
        if valid_username_email(username, email):
            send_mail
            (
                'CSUA Account Password Reset Link',
                'Reset Your password at this link:', # TODO: make link
                'django@csua.berkeley.edu',
                email,
                True
            )
            return redirect(REDIRECT)
        else:
            return redirect(REDIRECT)
        """
    else:
        form = PasswordResetForm()
        url = urls.urlpatterns[2]
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
