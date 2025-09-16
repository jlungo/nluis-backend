from django.contrib import admin

# Register your models here.
from nluis_billing.models import Fee


@admin.register(Fee)
class FeeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'project_type',
                    'currency', 'gfs_code', 'price']
