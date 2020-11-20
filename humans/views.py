from django.contrib.auth.mixins import LoginRequiredMixin as LoginRequired
from django.contrib.auth import logout, authenticate
from django.contrib.auth import update_session_auth_hash
from django.views.generic import FormView, DeleteView
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.conf import settings
from .forms import UpdateUserInfoForm, LoginForm, SignupForm
from .models import User
from .utils import request_ip_address


class LoginRequiredMixin(LoginRequired):
    login_url = reverse_lazy("account_login")
    redirect_field_name = 'next'


class AuthMixin():
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_authenticated:
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
            msg = _('To start using hawkpost, you must add a valid public key')
            messages.error(request, msg)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data(**kwargs)
        context["key_changes"] = user.keychanges.order_by('-created_at')[:20]
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.request.user
        return kwargs

    def form_valid(self, form):
        ip = request_ip_address(self.request)
        agent = self.request.META.get('HTTP_USER_AGENT')
        form.save(ip=ip, agent=agent)
        if form.change_password:
            update_session_auth_hash(self.request, form.instance)
        messages.success(self.request, _('Settings successfully updated'))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _('Please check the invalid fields'))
        return super().form_invalid(form)


class DeleteUserView(LoginRequiredMixin, DeleteView):
    model = User
    success_url = reverse_lazy("pages_index")

    def get_object(self, queryset=None):
        return self.request.user

    def delete(self, request, *args, **kwargs):
        current_pw = request.POST.get("current_password", "")
        if not request.user.has_usable_password() or authenticate(
                username=request.user.username, password=current_pw, request=request):
            response = super().delete(request, *args, **kwargs)
            logout(request)
            messages.success(request,
                             _('Account deleted successfully.'
                               ' We hope you comeback soon.'))
            return response
        else:
            messages.error(request,
                           _('In order to delete the account you must provide'
                             ' the current password.'))
            return self.get(request, *args, **kwargs)
