from django.contrib import admin
from .models import Box, Membership, Message


class MessageInline(admin.TabularInline):
    model = Message


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at', 'expires_at')
    inlines = [MessageInline]


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'box', 'access', 'created_at')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('box', 'status', 'created_at', 'sent_at')
