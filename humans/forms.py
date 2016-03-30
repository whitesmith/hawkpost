from django.forms import ModelForm
from .models import User


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

    def clean(self):
        if self.cleaned_data.get("public_key", ""):
            # Validate the public key
            pass

        if self.cleaned_data.get("fingerprint", ""):
            # Check if the key from the URL matches the fingerprint provided
            pass

        return
