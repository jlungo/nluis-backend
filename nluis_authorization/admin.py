from django.contrib import admin

# Register your models here.
from django.contrib.admin.models import LogEntry

from nluis_authorization.models import Station, AppUser, Menu, GroupMenu


@admin.register(LogEntry)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'action_time', 'user', 'content_type',
                    'object_id', 'action_flag', 'change_message']


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description', 'parent_id',
                    'created_date', 'created_time', 'created_by']
    search_fields = ['name']
    date_hierarchy = 'created_date'
    list_filter = ['created_by']


@admin.register(AppUser)
class AppUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'user_id', 'phone',
                    'middle_name', 'station', 'created_date']
    list_filter = ['station', 'user']
    search_fields = ['user']


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'icon', 'screen_code', 'order']


@admin.register(GroupMenu)
class GroupMenuAdmin(admin.ModelAdmin):
    list_display = ['id', 'group']
    filter_horizontal = ['menu']
