from django.contrib import admin
from .models import *


class ModuleLevelAdmin(admin.ModelAdmin):
    fields = ('name', "module", 'is_active', 'created_by', 'deleted_at', 'deleted_by')
    list_display = ('id', 'slug', 'name', 'module', 'is_active', 'created_at', 'created_by', 'updated_at', 'deleted_at', 'deleted_by')


class FormWorkFlowAdmin(admin.ModelAdmin):
    fields = ('name', "module_level", 'category', 'is_active', 'created_by', 'deleted_at', 'deleted_by')
    list_display = ('id', 'slug', 'name', 'module_level', 'category', 'is_active', 'created_at', 'created_by', 'updated_at', 'deleted_at', 'deleted_by')


admin.site.register(ModuleLevel, ModuleLevelAdmin)
admin.site.register(FormWorkflow, FormWorkFlowAdmin)
admin.site.register(Section)
admin.site.register(SectionApprovalRole)
admin.site.register(CustomForm)
admin.site.register(CustomerFormEditorRole)
admin.site.register(CustomFormField)
admin.site.register(FormData)
admin.site.register(FieldSelectOption)

