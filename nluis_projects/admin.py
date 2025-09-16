from django.contrib import admin


# Register your models here.
from import_export.admin import ExportActionModelAdmin, ImportMixin

from nluis_projects.models import *
from nluis_spatial.models import Beacon


# @admin.register(ProjectStatus)
# class ProjectStatusAdmin(admin.ModelAdmin):
#     list_display = ['id', 'code', 'name']


@admin.register(ProjectType)
class ProjectTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'code', 'duration',
                    'duration_alert',]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', ]
    filter_horizontal = ['funders']
    search_fields = ['name']


@admin.register(ProjectHistory)
class ProjectHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'remarks', 'project',
                     'screen_code', 'action']
    list_filter = ['action', 'project', 'screen_code']


@admin.register(ProjectSignatory)
class ProjectSignatoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'project', 'first_name', 'middle_name', 'last_name', 'designation', 'signature', 'phone',
                    'locality']
    list_filter = ['locality']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['id', 'locality', 'document_type', 'description']
    list_filter = ['project']


@admin.register(MultiMedia)
class MultiMediaAdmin(admin.ModelAdmin):
    list_display = ['id']




@admin.register(Beacon)
class BeaconAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_filter = ['project']






@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'professional', 'project']
    list_filter = ['project', 'user']
    search_fields = ['user', 'project']


@admin.register(TeamMemberHistory)
class TeamMemberHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'professional', 'project', 'created_date', 'created_time',
                    'change_date', 'change_time']
    list_filter = ['project', 'user']
    search_fields = ['user', 'project']


@admin.register(Remark)
class RemarkAdmin(admin.ModelAdmin):
    list_display = ['id', 'description', 'action']
    list_filter = ['action']




@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'project_type_name']


class LocalityProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'locality', 'approval_status', 'remarks')
    search_fields = ['project__name', 'locality__name']


admin.site.register(LocalityProject, LocalityProjectAdmin)