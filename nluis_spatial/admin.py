from django.contrib import admin

# Register your models here.
from nluis_spatial.models import SpatialUnit


@admin.register(SpatialUnit)
class SpatialUnitAdmin(admin.ModelAdmin):
    list_display = ['id', 'description', 'sqm', 'width', 'length', 'land_use', 'locality']
    list_filter = ['geometry_type', 'land_use']
