from django.forms import ModelForm
from .models import Box


class CreateBoxForm(ModelForm):
    class Meta:
        model = Box
        fields = ["name", "description", "expires_at"]
