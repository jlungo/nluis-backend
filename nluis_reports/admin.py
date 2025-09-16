from django.contrib import admin

# Register your models here.


from nluis_reports.models import (
    Report
)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'endpoint', 'filter']
