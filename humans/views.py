from django.contrib.auth.mixins import LoginRequiredMixin as LoginRequired
from django.contrib.auth import logout
from django.views.generic import FormView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from .forms import UpdateUserInfoForm
from .models import User


class LoginRequiredMixin(LoginRequired):
    login_url = reverse_lazy("account_login")
    redirect_field_name = 'next'


class UpdateSettingsView(LoginRequiredMixin, FormView):
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
        messages.info(self.request, "Settings successfully updated")
        return super().form_valid(form)


class DeleteUserView(LoginRequiredMixin, DeleteView):
    model = User
    success_url = reverse_lazy("pages_index")

    def delete(self, request, *args, **kwargs):
        logout(request)
        response = super().delete(request, *args, **kwargs)
        messages.success(request,
                         "Account deleted successfully."
                         "We hope you comeback soon.")
        return response
