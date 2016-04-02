from django.forms import ModelForm
from django.conf import settings
from .models import User
import requests


class UpdateUserInfoForm(ModelForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "organization",
            "public_key",
            "fingerprint",
            "keyserver_url",
        ]

    def clean_public_key(self):
        # Validate the public key
        pub_key = self.cleaned_data.get("public_key", "")
        if pub_key:
            # Check if has valid format
            result = settings.GPG_OBJ.import_keys(pub_key)
            if result.results[0]['fingerprint'] is None:
                self.add_error('public_key', "This key is not valid")
            # Check if it is not expired TODO
            # Check if is was not revoked TODO
        return pub_key

    def clean_fingerprint(self):
        # Fingerprint provided must match with one provided
        pub_key = self.cleaned_data.get("public_key", "")
        fingerprint = self.cleaned_data.get("fingerprint", "")
        fingerprint = fingerprint.replace(" ", "")
        if pub_key:
            result = settings.GPG_OBJ.import_keys(pub_key).results[0]
            if fingerprint != result["fingerprint"]:
                self.add_error('fingerprint', "Fingerprint does not match")
        return fingerprint

    def clean(self):
        cleaned_data = super().clean()
        url = cleaned_data.get("keyserver_url", "")
        if url:
            try:
                res = requests.get(url)
            except:
                self.add_error("keyserver_url",
                               "Could not access the specified url")
            begin = res.text.find("-----BEGIN PGP PUBLIC KEY BLOCK-----")
            end = res.text.find("-----END PGP PUBLIC KEY BLOCK-----")
            if (200 <= res.status_code < 300) and begin and end:
                cleaned_data["public_key"] = res.text[begin:end+34]
            else:
                self.add_error("keyserver_url",
                               "This url does not have a pgp key")
        return cleaned_data
