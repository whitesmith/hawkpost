from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from humans.views import LoginRequiredMixin
from humans.utils import key_state
from django.conf import settings
from .forms import CreateBoxForm, SubmitBoxForm
from .models import Box, Membership
from .tasks import process_email

from braces.views import JSONResponseMixin


class BoxListView(LoginRequiredMixin, ListView):
    template_name = "boxes/box_list.html"
    page_kwarg = 'page'
    paginate_by = 15

    def get_queryset(self):
        display_param = self.request.GET.get("display", "Open")
        query_filter = Box.get_status(display_param)
        own_boxes = self.request.user.own_boxes
        return own_boxes.filter(status=query_filter).order_by(
            "-created_at").prefetch_related("messages")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CreateBoxForm()
        context["domain"] = settings.SITE_DOMAIN
        context["display_status"] = self.request.GET.get("display", "Open")
        context["new_box"] = self.request.GET.get("new_box", "")
        context["allow_actions"] = Box.OPEN
        return context


class BoxCreateView(JSONResponseMixin, LoginRequiredMixin, CreateView):
    template_name = "boxes/box_create.html"
    http_method_names = [u'post']
    form_class = CreateBoxForm
    model = Box
    success_url = reverse_lazy("boxes_list")

    def dispatch(self, request, *args, **kwargs):
        # Check if user can create boxes:
        user = request.user
        if user.is_authenticated and not user.has_setup_complete():
            url = reverse_lazy("humans_update") + "?setup=1"
            return self.render_to_response({"location": url})

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = Box(**form.cleaned_data)
        self.object.owner = self.request.user
        self.object.save()

        Membership.objects.create(access=Membership.FULL,
                                  box=self.object,
                                  user=self.request.user)

        messages.success(self.request, _('Box created successfully'))
        url = self.get_success_url() + "?new_box={}".format(self.object.uuid)
        return self.render_to_response({"location": url})

    def render_to_response(self, context, **response_kwargs):
        json_context = context
        status = 200
        if context.get('form', None):
            json_context = {
                "form_errors": context["form"].errors
            }
            status = 400

        return self.render_json_response(json_context, status=status)


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
            messages.error(request, _('Only open boxes can be deleted'))
        else:
            self.object.delete()
            msg = _('Box named {} deleted successfully').format(name)
            messages.success(request, msg)
        success_url = self.get_success_url()
        return HttpResponseRedirect(success_url)


class BoxCloseView(LoginRequiredMixin, UpdateView):
    http_method_names = [u'post']
    success_url = reverse_lazy("boxes_list")
    model = Box

    def get_queryset(self):
        return self.request.user.own_boxes.all()

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.status != Box.OPEN:
            messages.error(request, _('Only open boxes can be closed'))
        else:
            self.object.status = Box.CLOSED
            self.object.save()
            msg = _('Box {} was closed').format(self.object.name)
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
        except (ValueError, Box.DoesNotExist):
            raise Http404(_('Not Found. Double check your URL'))

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        owner = self.object.owner
        fingerprint, *state = key_state(owner.public_key)
        now = timezone.now()
        if self.object.expires_at and now > self.object.expires_at:
            self.object.status = Box.EXPIRED
            self.object.save()

        not_open = self.object.status != Box.OPEN
        not_complete = not owner.has_setup_complete()
        not_valid = state[0] != 'valid'
        if not_open or not_complete or not_valid:
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
            cleaned_data = form.cleaned_data
            message = self.object.messages.create()

            # Mark box as done
            if self.object.messages.count() >= self.object.max_messages:
                self.object.status = Box.DONE
                self.object.save()

            add_user_email = cleaned_data.get("add_reply_to", False)
            if request.user.is_authenticated and add_user_email:
                user_email = request.user.email
            else:
                user_email = None

            # Schedule e-mail
            process_email.delay(
                message.id, form.cleaned_data, sent_by=user_email
            )

            return self.response_class(
                request=self.request,
                template="boxes/success.html",
                using=self.template_engine)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
            return self.form_invalid(form)
