from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(DefaultUserAdmin):
    pass
