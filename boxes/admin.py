from django.contrib import admin
from .models import Box, Membership


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at', 'expires_at')


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'box', 'access', 'created_at')
