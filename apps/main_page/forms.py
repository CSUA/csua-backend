from django import forms
from django.core.exceptions import ValidationError


class LoginForm(forms.Form):
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
    officer_username = forms.CharField(label="Officer Username")
    officer_password = forms.CharField(
        widget=forms.PasswordInput(), label="Officer Password"
    )
    agree_rules = forms.BooleanField(required=True)
