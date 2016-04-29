from django.forms import ModelForm, Form, CharField, Textarea
from .models import Box


class CreateBoxForm(ModelForm):
    class Meta:
        model = Box
        fields = ["name", "description", "expires_at"]


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
