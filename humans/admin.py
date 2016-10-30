from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from .models import User, Notification
from .tasks import enqueue_email_notifications


@admin.register(User)
class UserAdmin(DefaultUserAdmin):
    list_display = ('username',
                    'email',
                    "first_name",
                    "last_name",
                    "is_staff",
                    "has_public_key",
                    "has_keyserver_url")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fieldsets += ((_('Key options'), {
            'classes': ('collapse',),
            'fields': ('fingerprint', 'keyserver_url', 'public_key'),
        }),)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('subject',
                    'sent_at',
                    'send_to')
    list_filter = ('send_to', 'sent_at')

    fields = ["subject", "body", "send_to"]
    search_fields = ['subject', 'body']

    actions = ["send_notification", "delete_selected"]

    def delete_model(self, request, obj):
        if obj.sent_at:
            msg = _('Cannot delete "{}", the notification was already sent')
            messages.error(request, msg.format(obj.subject))
        else:
            obj.delete()

    def delete_selected(self, request, queryset):
        queryset.filter(sent_at=None).delete()
        msg = _('Removed all unsent notifications in selection')
        messages.success(request, msg)

    def send_notification(self, request, queryset):
        queryset = queryset.filter(sent_at=None)
        for notification in queryset:
            send_to = notification.send_to.id if notification.send_to else None
            enqueue_email_notifications.delay(notification.id,
                                              send_to)
        queryset.update(sent_at=timezone.now())
        messages.success(request, _('All notifications enqueued for sending'))

    send_notification.short_description = _('Send selected notifications')
    delete_selected.short_description = _('Delete selected notifications')


admin.site.site_header = _('HawkPost Administration')
admin.site.site_title = _('HawkPost Admin')
admin.site.index_title = _('Project Models')
