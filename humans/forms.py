from django.forms import ModelForm
from django import forms
from allauth.account.forms import LoginForm as BaseLoginForm
from allauth.account.forms import SignupForm as BaseSignupForm
from .models import User
from .utils import key_state

import requests


class UpdateUserInfoForm(ModelForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "organization",
            "keyserver_url",
            "public_key",
            "fingerprint",
            "server_signed",
            "timezone"
        ]
        widgets = {
            'keyserver_url': forms.TextInput(attrs={'placeholder': 'https://example.com/key.asc'})
        }

    def __init__(self, *args, **kwargs):
        self.pub_key = None
        return super().__init__(*args, **kwargs)

    def clean_public_key(self):
        # Validate the public key
        if self.pub_key:
            pub_key = self.pub_key
        else:
            pub_key = self.cleaned_data.get("public_key", "")

        if pub_key:
            fingerprint, state = key_state(pub_key)
            # Check if has valid format
            if state == "invalid":
                self.add_error('public_key', "This key is not valid")
            # Check if it is not expired
            elif state == "revoked":
                self.add_error('public_key', "This key is revoked")
            # Check if is was not revoked
            elif state == "expired":
                self.add_error('public_key', "This key is expired")
        return pub_key

    def clean_fingerprint(self):
        # Fingerprint provided must match with one provided
        pub_key = self.cleaned_data.get("public_key", "")
        fingerprint = self.cleaned_data.get("fingerprint", "")
        fingerprint = fingerprint.replace(" ", "")
        if pub_key:
            key_fingerprint, state = key_state(pub_key)
            if fingerprint != key_fingerprint:
                self.add_error('fingerprint', "Fingerprint does not match")
        return fingerprint

    def clean_keyserver_url(self):
        url = self.cleaned_data.get("keyserver_url", "")
        if url:
            try:
                res = requests.get(url)
            except:
                self.add_error("keyserver_url",
                               "Could not access the specified url")
            begin = res.text.find("-----BEGIN PGP PUBLIC KEY BLOCK-----")
            end = res.text.find("-----END PGP PUBLIC KEY BLOCK-----")
            if 200 <= res.status_code < 300 and begin >= 0 and end > begin:
                self.pub_key = res.text[begin:end + 34]
            else:
                self.add_error("keyserver_url",
                               "This url does not have a pgp key")
        return url


class LoginForm(BaseLoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['login'].widget.attrs["placeholder"] = ""
        self.fields['password'].widget.attrs["placeholder"] = ""


class SignupForm(BaseSignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs["placeholder"] = ""
        self.fields['password1'].widget.attrs["placeholder"] = ""
        self.fields['password2'].widget.attrs["placeholder"] = ""
