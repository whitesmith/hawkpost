from django.forms import ModelForm, Form, CharField, Textarea
from .models import Box
from django.utils import timezone


class CreateBoxForm(ModelForm):
    class Meta:
        model = Box
        fields = ["name", "description", "expires_at"]

    def clean_expires_at(self):
        # Validate the expiration date
        expires_at = self.cleaned_data.get("expires_at", "")
        current_tz = timezone.get_current_timezone()
        if expires_at:
            # Check if the expiration date is a past date
            if timezone.localtime(timezone.now(), current_tz) > expires_at:
                self.add_error('expires_at', "The date must be on the future.")
        return expires_at


class SubmitBoxForm(Form):
    message = CharField(widget=Textarea)

    def clean_message(self):
        # Quick check if the message really came encrypted
        message = self.cleaned_data.get("message")
        lines = message.split("\r\n")

        begin = "-----BEGIN PGP MESSAGE-----"
        end = "-----END PGP MESSAGE-----"

        try:
            if lines[0] != begin or lines[-1] != end:
                self.add_error("message", "Invalid PGP message")
        except IndexError:
            self.add_error("message", "Invalid PGP message")
        return message
