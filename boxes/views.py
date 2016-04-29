from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.utils import timezone
from humans.views import LoginRequiredMixin
from django.conf import settings
from .forms import CreateBoxForm, SubmitBoxForm
from .models import Box, Membership
from .tasks import process_email


class BoxListView(LoginRequiredMixin, ListView):
    template_name = "boxes/box_list.html"

    def get_queryset(self):
        display_param = self.request.GET.get("display", "Open")
        query_filter = Box.get_status(display_param)
        return self.request.user.own_boxes.filter(
            status=query_filter).order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CreateBoxForm()
        context["domain"] = settings.SITE_DOMAIN
        context["allow_delete"] = Box.OPEN
        return context


class BoxCreateView(LoginRequiredMixin, CreateView):
    template_name = "boxes/box_create.html"
    http_method_names = [u'get', u'post']
    form_class = CreateBoxForm
    model = Box
    success_url = reverse_lazy("boxes_list")

    def dispatch(self, request, *args, **kwargs):
        # Check if user can create boxes:
        if request.user.has_setup_complete():
            return super().dispatch(request, *args, **kwargs)
        else:
            msg = "To start using hawkpost," \
                  " you must add a valid public key"
            messages.error(request, msg)
            return HttpResponseRedirect(reverse_lazy("humans_update"))

    def form_valid(self, form):
        self.object = Box(**form.cleaned_data)
        self.object.owner = self.request.user
        self.object.save()

        Membership.objects.create(access=Membership.FULL,
                                  box=self.object,
                                  user=self.request.user)

        messages.success(self.request, "Box created successfully")
        return HttpResponseRedirect(self.get_success_url())


class BoxDeleteView(LoginRequiredMixin, DeleteView):
    http_method_names = [u'post']
    success_url = reverse_lazy("boxes_list")
    model = Box

    def get_queryset(self):
        return self.request.user.own_boxes.all()

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        name = self.object.name
        if self.object.status != Box.OPEN:
            messages.error(request, "Only open boxes can be deleted")
        else:
            self.object.delete()
            msg = "Box named {} deleted successfully".format(name)
            messages.success(request, msg)
        success_url = self.get_success_url()
        return HttpResponseRedirect(success_url)


class BoxSubmitView(UpdateView):
    template_name = "boxes/box_submit.html"
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
        now = timezone.now()
        if now > self.object.expires_at:
            self.object.status = Box.EXPIRED
            self.object.save()

        owner = self.object.owner
        if self.object.status != Box.OPEN or not owner.has_setup_complete():
            return self.response_class(
                request=self.request,
                context={"box": self.object},
                template="boxes/closed.html",
                using=self.template_engine)
        else:
            return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form(data={"data": request.POST})
        if form.is_valid():
            process_email.delay(self.object.id, form.cleaned_data)
            self.object.status = Box.ONQUEUE
            self.object.save()
            return self.response_class(
                request=self.request,
                template="boxes/success.html",
                using=self.template_engine)
        else:
            msg = "The message must be encrypted before the server forwards it"
            messages.error(request, msg)
            return self.form_invalid(form)
