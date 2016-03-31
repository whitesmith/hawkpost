from django.forms import ModelForm, Form, CharField, Textarea
from .models import Box


class CreateBoxForm(ModelForm):
    class Meta:
        model = Box
        fields = ["name", "description", "expires_at"]


class SubmitBoxForm(Form):
    message = CharField(widget=Textarea)
