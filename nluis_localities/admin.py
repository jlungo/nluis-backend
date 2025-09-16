from django import forms
from django.contrib import admin

# Register your models here.
from libs.shp.ushp import read_shp
from nluis_localities.models import Locality, LocalityLevel


@admin.register(LocalityLevel)
class LocalityLevelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'parent', 'created_at', 'updated_at')
    search_fields = ('name', 'code')
    list_filter = ('parent',)
    ordering = ('id',)


admin.site.register(Locality)