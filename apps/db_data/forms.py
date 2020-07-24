from django import forms

from .constants import OH_CHOICES
from apps.ldap.utils import user_exists


class OfficerCreationForm(forms.Form):
    username = forms.CharField(max_length=32)
    photo = forms.ImageField(label="Photo 1", required=False)
    photo_url = forms.CharField(label="Photo 1 URL", required=False)
    photo2 = forms.ImageField(label="Photo 2", required=False)
    photo2_url = forms.CharField(label="Photo 2 URL", required=False)
    blurb = forms.CharField(widget=forms.Textarea, max_length=255, required=False)
    office_hours = forms.ChoiceField(
        label="Office Hour", choices=([("", "")] + OH_CHOICES), required=False
    )
    officer_since = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}), required=False
    )

    def clean(self):
        cleaned_data = super().clean()
        if (not cleaned_data.get("photo")) + (not cleaned_data.get("photo_url")) == 0:
            raise forms.ValidationError(
                "Please specify up to one of 'Photo 1' or 'Photo 1 URL'"
            )
        if (not cleaned_data.get("photo2")) + (not cleaned_data.get("photo2_url")) == 0:
            raise forms.ValidationError(
                "Please specify up to one of 'Photo 2' or 'Photo 2 URL'"
            )
        username = cleaned_data.get("username")
        if not user_exists(username):
            raise forms.ValidationError(f"User {username} is not in LDAP")
        return cleaned_data
