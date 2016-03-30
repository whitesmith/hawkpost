from django.views.generic import FormView
from django.core.urlresolvers import reverse_lazy
from .forms import UpdateUserInfoForm


class UpdateSettingsView(FormView):
    """Lets the user update his setttings"""
    template_name = "humans/update_user_form.html"
    form_class = UpdateUserInfoForm
    success_url = reverse_lazy("humans_update")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
