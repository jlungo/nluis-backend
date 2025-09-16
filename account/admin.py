from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UserAdminCreationForm, UserAdminChangeForm
from django.contrib.auth.models import Permission
from django.contrib import admin
from .models import *


class ModuleAdmin(admin.ModelAdmin):
    list_display = ("id", "slug", "name")
    search_fields = ("name",)


class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'alias')
    search_fields = ('name',)


class UserRolePermissionAdmin(admin.ModelAdmin):
    fields = ('user_role', 'module', 'group')
    list_display = ('id', 'module', 'user_role', 'group', 'created_at', 'updated_at')

class PermissionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "codename", "content_type")
    search_fields = ("name", "codename")


class UserAdmin(BaseUserAdmin):
    """Admin config for custom User model"""

    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    # Fields shown in the admin list view
    list_display = (
        "id",
        "email",
        "first_name",
        "last_name",
        "phone",
        "gender",
        "user_type",
        "organization",
        "role",
        "is_verified",
        "is_active",
        "is_staff",
        "is_admin",
        "login_attempt",
    )
    list_filter = (
        "user_type",
        "gender",
        "organization",
        "role",
        "is_verified",
        "is_active",
        "is_staff",
        "is_admin",
    )

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal Info",
            {"fields": ("first_name", "last_name", "phone", "gender")},
        ),
        (
            "Organization & Role",
            {"fields": ("user_type", "organization", "role")},
        ),
        (
            "Permissions",
            {"fields": ("is_verified", "is_active", "is_staff", "is_admin", "is_superuser", "groups", "user_permissions")},
        ),
        ("Login Info", {"fields": ("login_attempt", "last_login")}),
    )

    # Fields for user creation form
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "gender",
                    "user_type",
                    "organization",
                    "role",
                    "phone",
                    "password1",
                    "password2",
                    "is_verified",
                    "is_active",
                    "is_staff",
                    "is_admin",
                ),
            },
        ),
    )

    search_fields = ("email", "first_name", "last_name", "phone")
    ordering = ("email",)
    filter_horizontal = ("groups", "user_permissions")


admin.site.register(Permission, PermissionAdmin)
admin.site.register(Module, ModuleAdmin)
admin.site.register(UserRole, UserRoleAdmin)
admin.site.register(UserRolePermission, UserRolePermissionAdmin)
admin.site.register(User, UserAdmin)
