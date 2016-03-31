from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from .forms import CreateBoxForm, SubmitBoxForm
from .models import Box, Membership


class BoxListView(ListView):
    template_name = "boxes/boxlist.html"

    def get_queryset(self):
        return self.request.user.own_boxes.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CreateBoxForm()
        print(self.object_list)
        print(self.request.user.boxes.all())
        return context


class BoxCreateView(CreateView):
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


class BoxDeleteView(DeleteView):
    http_method_names = [u'post']
    success_url = reverse_lazy("boxes_list")
    model = Box

    def get_queryset(self):
        return self.request.user.own_boxes.all()


class BoxSubmitView(UpdateView):
    template_name = "boxes/boxsubmit.html"
    form_class = SubmitBoxForm
    model = Box

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class()

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        try:
            return queryset.get(uuid=self.kwargs.get("box_uuid"))
        except ValueError:
            raise ObjectDoesNotExist("Not Found. Double check your URL")
