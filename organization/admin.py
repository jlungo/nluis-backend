from django.contrib import admin
from .models import *


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'short_name', 'url', 'type', 'level', 'status', 'address')

admin.site.register(OrganizationType)
admin.site.register(Organization, OrganizationAdmin)
