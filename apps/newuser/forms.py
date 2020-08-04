from django import forms
from django.core.exceptions import ValidationError

usernameWhitelist = set(".-_")


def validate_username_chars(value):
    if not all(c.isalnum() or c in usernameWhitelist for c in value):
        raise ValidationError(
            "Username must consist of alphanumeric characters and ., -, or _"
        )


def validate_username_in_use(value):
    # TODO: check if username is in use by making a simple ldap query.
    pass


class RemoteEmailRequestForm(forms.Form):
    email = forms.CharField(label="Email")


class NewUserRemoteForm(forms.Form):
    full_name = forms.CharField(label="Full Name")
    student_id = forms.IntegerField(
        label="Student ID", min_value=100000, max_value=10000000000
    )
    email = forms.EmailField()
    username = forms.CharField(
        validators=[validate_username_chars, validate_username_in_use]
    )
    password = forms.CharField(widget=forms.PasswordInput())
    enroll_jobs = forms.BooleanField(required=False)
    agree_rules = forms.BooleanField(required=True)


class NewUserForm(NewUserRemoteForm):
    officer_username = forms.CharField(label="Officer Username")
    officer_password = forms.CharField(
        widget=forms.PasswordInput(), label="Officer Password"
    )
