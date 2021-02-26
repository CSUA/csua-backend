from django import forms
from django.core.exceptions import ValidationError

from .utils import valid_password
from apps.ldap.utils import user_exists

usernameWhitelist = set(".-_")


def validate_username_chars(value):
    if not all(c.isalnum() or c in usernameWhitelist for c in value):
        raise ValidationError(
            "Username must consist of alphanumeric characters and ., -, or _"
        )


def validate_username_not_in_use(value):
    if user_exists(value):
        raise ValidationError(f"Username {value} is taken")


class RemoteEmailRequestForm(forms.Form):
    email = forms.EmailField(label="Email")


class NewUserForm(forms.Form):
    full_name = forms.CharField(label="Full Name")
    student_id = forms.IntegerField(
        label="Student ID", min_value=100000, max_value=10000000000
    )
    email = forms.EmailField()
    username = forms.CharField(
        validators=[validate_username_chars, validate_username_not_in_use]
    )
    password = forms.CharField(widget=forms.PasswordInput())
    enroll_jobs = forms.BooleanField(required=False, label="Jobs@ List Opt-in")
    agree_rules = forms.BooleanField(required=True)

    def clean(self):
        form_data = super().clean()
        password = form_data.get("password")
        if not valid_password(password):
            raise ValidationError("Password must meet requirements")
        return form_data


class NewUserFormOfficerVerified(NewUserForm):
    officer_username = forms.CharField(label="Officer Username")
    officer_password = forms.CharField(
        widget=forms.PasswordInput(), label="Officer Password"
    )
