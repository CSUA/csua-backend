from django import forms
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse

from .tokens import account_activation_token
from apps.ldap.utils import change_password, get_user_email
from apps.newuser.utils import valid_password


class RequestPasswordResetForm(forms.Form):
    username = forms.CharField(label="Username")


class PasswordResetForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super(PasswordResetForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if not valid_password(password):
            raise forms.ValidationError("Password is not valid!")

        elif password != confirm_password:
            raise forms.ValidationError("Passwords do not match!")


class PasswordResetView(View):
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
            return render(request, "registration/invalid.html")


def RequestPasswordResetView(request):
    if request.method == "POST":
        form = RequestPasswordResetForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            user_email = get_user_email(username)
            if user_email is not None:
                send_mail(
                    subject="CSUA Account Password Reset Link",
                    message="If you did not request this, please disregard this email\n"
                    "Reset Your password at this link:",  # TODO: make link
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

    return render(request, "resetpassword.html", {"form": form})
