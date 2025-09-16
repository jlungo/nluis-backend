import autocomplete_all
from django.contrib import admin

# Register your models here.
from import_export.admin import ImportMixin, ExportActionModelAdmin

from nluis_collect.models import Category, Form, FormField, FormAnswer, TemporaryFile, Monitoring, \
    FormAnswerQuestionnaire


@admin.register(Category)
class CategoryAdmin(ImportMixin, ExportActionModelAdmin):
    list_display = ['id', 'name', 'project_type', 'flag']
    list_filter = ['project_type']


@admin.register(Form)
class FormAdmin(ImportMixin, ExportActionModelAdmin):
    list_display = ['id', 'name', 'order_no', 'is_enabled']
    list_filter = ['category']
    search_fields = ['name']


@admin.register(FormField)
class FormFieldAdmin(ImportMixin, ExportActionModelAdmin):
    list_display = ['id', 'form', 'form_field',
                    'data_type', 'placeholder', 'param_code']
    list_filter = ['form__category', 'form']
    search_fields = ['form_field', 'form']
    autocomplete_fields = ['parent', 'form']


@admin.register(FormAnswer)
class FormAnswerAdmin(ImportMixin, ExportActionModelAdmin):
    list_display = ['id', 'created_date', 'created_time',
                    'claim_no', 'project', 'form_field', 'village', 'stage']
    search_fields = ['claim_no']
    list_filter = ['project']
    date_hierarchy = 'created_date'


@admin.register(FormAnswerQuestionnaire)
class FormAnswerQuestionnaireAdmin(ImportMixin, ExportActionModelAdmin):
    list_display = ['id', 'created_date', 'created_time',
                    'claim_no', 'project', 'locality', 'village', 'file']
    list_filter = ['locality', 'locality__parent']
    date_hierarchy = 'created_date'


@admin.register(TemporaryFile)
class TemporaryFileAdmin(ImportMixin, ExportActionModelAdmin):
    list_display = ['id', 'file', 'description',
                    'created_date', 'created_time', 'created_by', 'device_id']
    list_filter = ['description', 'created_by']
    search_fields = ['file']


# @admin.register(Monitoring)
# class MonitoringAdmin(autocomplete_all.ModelAdmin):
#     list_display = ['id', 'action', 'means_of_verification',
#                     'assessment_performance', 'flag']
#     # list_filter = ['action']
#     filter_horizontal = ['form_fields']
#     # autocomplete_fields = ['action']
#     # search_fields = ['action']
