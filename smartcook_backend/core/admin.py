from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# signup
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("userid", "username", "email", "is_staff", "is_active")
    search_fields = ("userid", "username", "email")
    ordering = ("userid",)

    fieldsets = (
        (None, {"fields": ("userid", "username", "email", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("userid", "username", "email", "password1", "password2", "is_staff", "is_active")}
        ),
    )
