from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.core.mail import EmailMessage
from django.conf import settings
from humans.views import LoginRequiredMixin
from .forms import CreateBoxForm, SubmitBoxForm
from .models import Box, Membership


class BoxListView(LoginRequiredMixin, ListView):
    template_name = "boxes/boxlist.html"

    def get_queryset(self):
        return self.request.user.own_boxes.filter(closed=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CreateBoxForm()
        return context


class BoxCreateView(LoginRequiredMixin, CreateView):
    http_method_names = [u'post']
    form_class = CreateBoxForm
    model = Box
    success_url = reverse_lazy("boxes_list")

    def form_valid(self, form):
        self.object = Box(**form.cleaned_data)
        self.object.owner = self.request.user
        self.object.save()

        Membership.objects.create(access=Membership.FULL,
                                  box=self.object,
                                  user=self.request.user)

        messages.info(self.request, "Box created successfully")
        return HttpResponseRedirect(self.get_success_url())


class BoxDeleteView(LoginRequiredMixin, DeleteView):
    http_method_names = [u'post']
    success_url = reverse_lazy("boxes_list")
    model = Box

    def get_queryset(self):
        return self.request.user.own_boxes.all()


class BoxSubmitView(UpdateView):
    template_name = "boxes/boxsubmit.html"
    form_class = SubmitBoxForm
    model = Box
    success_url = reverse_lazy("boxes_show")

    def get_form(self, form_class=None, data=None):
        if form_class is None:
            form_class = self.get_form_class()
        if data is None:
            data = {}
        return form_class(**data)

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        try:
            q = queryset.select_related('owner').prefetch_related('recipients')
            return q.get(uuid=self.kwargs.get("box_uuid"))
        except ValueError:
            raise ObjectDoesNotExist("Not Found. Double check your URL")

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.closed:
            return self.response_class(
                request=self.request,
                template="boxes/closed.html",
                using=self.template_engine)
        else:
            return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form(data={"data": request.POST})
        if form.is_valid():
            self.process_email(form.cleaned_data)
            self.object.closed = True
            self.object.save()
            return self.response_class(
                request=self.request,
                template="boxes/success.html",
                using=self.template_engine)
        else:
            return self.form_invalid(form)

    def process_email(self, data):
        subject = "New submission to your box: {}".format(self.object.name)
        # TODO SignMessage Here
        email = EmailMessage(subject, data["message"],
                             settings.DEFAULT_FROM_EMAIL,
                             [self.object.owner.email])
        email.send()
