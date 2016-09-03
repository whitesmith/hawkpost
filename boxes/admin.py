from django.contrib import admin
from .models import Box, Membership, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at', 'expires_at')
    list_filter = ('status', 'created_at', 'expires_at')
    search_fields = ['name', 'owner__email']
    inlines = [MessageInline]


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'box', 'access', 'created_at')
    list_filter = ('access', 'created_at',)
    search_fields = ['box__name', 'user__email']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('box', 'status', 'created_at', 'sent_at')
    list_filter = ('status', 'created_at', 'sent_at')
