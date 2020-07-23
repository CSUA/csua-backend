from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.contrib import messages
# this is for testing purposes
from django.test import override_settings
from django import forms
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse
from django.utils.html import strip_tags
from django.template import Context
from django.template.loader import render_to_string

from .tokens import account_activation_token
from apps.ldap.utils import change_password, get_user_email, user_exists
from apps.newuser.utils import valid_password

REDIRECT = "/"

class RequestPasswordResetForm(forms.Form):
    username = forms.CharField(label="Username")


class PasswordResetForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(), label='Enter password')
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label='Confirm password')


class PasswordResetView(View):
    def post(self, request, uid, token):
        print("hoi")
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data["password"]
            confirm_password = form.cleaned_data["confirm_password"]
            #success = change_password(user, password)
            if password != confirm_password:
                print("the passwords don't match")
            if not valid_password(password):
                print("this is an invalid password")
            else:
                print("i changed the password")
        #print(success)
        return redirect(REDIRECT)

    def get(self, request, uid, token):
        print(uid, token)
        if not user_exists(uid):
            user = None
        else:
            user = uid

        # getting here just need to get back the pass
        if user is not None and account_activation_token.check_token(user, token):
            form = PasswordResetForm()
            context = {'form': form, 'uid': uid, 'token': token}
            return render(request, "resetpasswordconfirm.html", context)
        else:
            # invalid link
            #return render(request, "")
            print('invalid link')
            return redirect(REDIRECT)


def get_html_email(username, email, token):
    return render_to_string(
            "password_reset_email.html",
            {
                "uid": username,
                "email": email,
                "token": token,
            }
        )

# Override setting for testing purposes
@override_settings(EMAIL_BACKEND='django.core.mail.backends.filebased.EmailBackend', \
        EMAIL_FILE_PATH='test-messages')
def RequestPasswordResetView(request):
    if request.method == 'POST':
        form = RequestPasswordResetForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            token = account_activation_token.make_token(username)
            user_email = get_user_email(username)
            html_message = get_html_email(username, user_email, token)
            #print(account_activation_token.secret)
            if user_email is not None:
                send_mail(
                    subject="CSUA Account Password Reset Link",
                    message=strip_tags(html_message),
                    html_message=html_message,
                    from_email="django@csua.berkeley.edu",
                    recipient_list=[user_email],
                    # fail_silently=True,
                )
                return redirect(reverse("request-reset-password"))
            else:
                return redirect(reverse("request-reset-password"))
        else:
            pass  # form failure
    else:
        form = RequestPasswordResetForm()

    return render(request, "requestpasswordreset.html", {"form": form})
