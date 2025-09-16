from django.contrib import admin

# Register your models here.
from import_export import resources
from import_export.admin import ExportActionModelAdmin, ImportMixin

from django import forms
from nluis_setups.models import (
    Designation,
    Funder,
    LandUseGeometryType,
    LocalityDocumentCounter,
    IdentityType,
    DocumentType,
    OccupancyType,
    PartyRole,
    LandUse,
    Currency,
    ExchangeRate,
    MapType
)


@admin.register(Funder)
class FunderAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


@admin.register(IdentityType)
class IdentityTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'code',
                    'acceptable_format', 'project_type']
    list_filter = ['project_type']


@admin.register(OccupancyType)
class OccupancyTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description', 'quantity']


@admin.register(PartyRole)
class PartyRoleAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description']


@admin.register(LandUseGeometryType)
class LandUserGeometryAdmin(admin.ModelAdmin):
    list_display = ['id', 'geometry_type', 'si_unit']


class LandUseForm(forms.ModelForm):
    class Meta:
        model = LandUse
        fields = "__all__"
        widgets = {
            "style": forms.Textarea(attrs={"rows": 14, "cols": 100}),
        }

@admin.register(LandUse)
class LandUseAdmin(admin.ModelAdmin):
    form = LandUseForm
    list_display = ["name", "geometry_type", "reserved"]
    search_fields = ["name", "code"]
    # autocomplete_fields = ["geometry_type"]

    # Prefill a sensible style when creating a new record
    def get_changeform_initial_data(self, request):
        # a simple solid preset—users can edit it
        return {
            "style": {
                "layers": [{
                    "type": "polygon",
                    "fill": {"type": "solid", "color": "#00D668", "opacity": 1.0},
                    "stroke": {"color": "#1B5E20", "width": 1}
                }]
            }
        }


@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description']
    list_filter = ['name']
    filter_horizontal = ['project_type']


@admin.register(LocalityDocumentCounter)
class LocalityDocumentCounterAdmin(admin.ModelAdmin):
    list_display = ['id', 'project', 'locality']


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'code']


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ['id', 'currency', 'amount', 'is_active']


@admin.register(MapType)
class MapTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description', 'level']
