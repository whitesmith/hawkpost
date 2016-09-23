from django.contrib.auth.mixins import LoginRequiredMixin as LoginRequired
from django.contrib.auth import logout, authenticate
from django.views.generic import FormView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from .forms import UpdateUserInfoForm, LoginForm, SignupForm
from .models import User


class LoginRequiredMixin(LoginRequired):
    login_url = reverse_lazy("account_login")
    redirect_field_name = 'next'


class AuthMixin():
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_authenticated():
            context["login_form"] = LoginForm()
            context["signup_form"] = SignupForm()
        return context


class UpdateSettingsView(LoginRequiredMixin, FormView):
    """Lets the user update his setttings"""
    template_name = "humans/update_user_form.html"
    form_class = UpdateUserInfoForm
    success_url = reverse_lazy("humans_update")

    def get(self, request, *args, **kwargs):
        if request.GET.get('setup', None):
            msg = "To start using hawkpost," \
                  " you must add a valid public key"
            messages.error(request, msg)
        return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Settings successfully updated")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please check the invalid fields")
        return super().form_invalid(form)


class DeleteUserView(LoginRequiredMixin, DeleteView):
    model = User
    success_url = reverse_lazy("pages_index")

    def get_object(self, queryset=None):
        return self.request.user

    def delete(self, request, *args, **kwargs):
        current_pw = request.POST.get("current_password", "")
        if authenticate(username=request.user.username, password=current_pw):
            response = super().delete(request, *args, **kwargs)
            logout(request)
            messages.success(request,
                             "Account deleted successfully."
                             "We hope you comeback soon.")
            return response
        else:
            messages.error(request,
                           "In order to delete the account you must provide"
                           " the current password.")
            return self.get(request, *args, **kwargs)
