from colorfield.fields import ColorField
from account.models import User
from django.db import models

# Create your models here.
from django.utils import timezone
from django_currentuser.db.models import CurrentUserField
from django.core.exceptions import ValidationError


# class BaseSoftDeletableModel(models.Model):
#     is_deleted = models.BooleanField(default=False)
#     deleted_at = models.DateTimeField(null=True)
#     deleted_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
#
#     class Meta:
#         abstract = True
#
#     def soft_delete(self, user_id=None):
#         self.is_deleted = True
#         self.deleted_by = user_id
#         self.deleted_at = timezone.now()
#         self.save()


# class TimestampedModel(models.Model):
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         abstract = True

class Funder(models.Model):
    class Meta:
        db_table = 'setup_funders'

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    created_by = CurrentUserField()
    updated_by = CurrentUserField(
        on_update=True, related_name='setup_funders_updated_by')

    name = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=50,
                                choices=(('government', 'Government'), ('non-government', 'Non Government')))

    def __str__(self):
        return self.name


class Designation(models.Model):
    class Meta:
        db_table = 'setup_designation'

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    created_by = CurrentUserField()
    updated_by = CurrentUserField(
        on_update=True, related_name='setup_designation_updated_by')

    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    project_type = models.ManyToManyField(
        'nluis_projects.ProjectType', blank=True)

    def __str__(self):
        return self.name


class DocumentType(models.Model):
    class Meta:
        db_table = 'setup_document_type'
        ordering = ['name']
        unique_together = ['project_type', 'code']

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    project_type = models.ForeignKey(
        'nluis_projects.ProjectType', on_delete=models.SET_NULL, null=True, blank=True)
    is_input = models.BooleanField(default=True)
    is_payable = models.BooleanField(default=False)
    acceptable_format = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name


class MapType(models.Model):
    class Meta:
        db_table = 'setup_map_type'

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    created_by = CurrentUserField()
    updated_by = CurrentUserField(
        on_update=True, related_name='setup_map_type_updated_by')

    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    level = models.ForeignKey(
        'nluis_localities.LocalityLevel', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name


class IdentityType(models.Model):
    class Meta:
        db_table = 'setup_identity_types'

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    created_by = CurrentUserField()
    updated_by = CurrentUserField(
        on_update=True, related_name='setup_identity_type_updated_by')

    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class OccupancyType(models.Model):
    class Meta:
        db_table = 'setup_occupancy_types'

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    created_by = CurrentUserField()
    updated_by = CurrentUserField(
        on_update=True, related_name='setup_occupancy_type_updated_by')

    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    swahili = models.CharField(max_length=50, blank=True, null=True)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return self.name


class PartyRole(models.Model):
    class Meta:
        db_table = 'setup_party_roles'

    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    created_by = CurrentUserField()
    updated_by = CurrentUserField(
        on_update=True, related_name='setup_party_role_updated_by')

    def __str__(self):
        return self.name


class LandUseGeometryType(models.Model):
    class Meta:
        db_table = 'setup_land_use_geometry_type'

    ch_type = (
        ('point', 'POINT'),
        ('polygon', 'POLYGON'),
        ('line', 'LINE'),
    )
    geometry_type = models.CharField(max_length=50, choices=ch_type)
    si_unit = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f'{self.geometry_type} - {self.si_unit}'


def default_style():
    return {"layers": []}  # mutable default must be a callable


class LandUse(models.Model):
    class Meta:
        db_table = 'setup_land_uses'

    code = models.CharField(max_length=50, unique=True, null=True, blank=True)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    swahili = models.CharField(max_length=50, null=True, blank=True)
    reserved = models.BooleanField(default=False)
    geometry_type = models.ForeignKey(
        'nluis_setups.LandUseGeometryType', on_delete=models.SET_NULL, blank=True, null=True
    )

    # Legacy (optional to keep while migrating)
    color = ColorField(blank=True, null=True)

    # New: inline style JSON
    style = models.JSONField(default=default_style,
                             help_text="{'layers': [...]}")

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    created_by = CurrentUserField()
    updated_by = CurrentUserField(
        on_update=True, related_name='setup_land_use_updated_by')
    order_no = models.IntegerField(default=1000)

    def clean(self):
        s = self.style
        if not isinstance(s, dict) or "layers" not in s or not isinstance(s["layers"], list):
            raise ValidationError(
                "style must be an object with a 'layers' list.")

    def __str__(self):
        return str(self.name)

    # Optional convenience
    def solid_from_color(self):
        """Return a basic style from the legacy color, useful for backfill/previews."""
        c = self.color or "#cccccc"
        return {
            "layers": [{
                "type": "polygon",
                "fill": {"type": "solid", "color": c, "opacity": 1.0},
                "stroke": {"color": "#000000", "width": 0}
            }]
        }


class LocalityDocumentCounter(models.Model):
    class Meta:
        db_table = 'setup_locality_docs_counter'
        unique_together = ['project', 'locality']

    project = models.ForeignKey(
        'nluis_projects.Project', blank=True, null=True, on_delete=models.SET_NULL)
    locality = models.ForeignKey(
        'nluis_localities.Locality', blank=True, null=True, on_delete=models.SET_NULL)
    count = models.IntegerField(default=0)
    meeting_date = models.DateField(blank=True, null=True)

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    created_by = CurrentUserField()
    updated_by = CurrentUserField(
        on_update=True, related_name='setup_counter_updated_by')


# Bill and payment setups##


class Currency(models.Model):
    class Meta:
        db_table = 'setup_currencies'
        verbose_name_plural = 'Currencies'

    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=10, blank=True, null=True)
    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    created_by = CurrentUserField()
    updated_by = CurrentUserField(
        on_update=True, related_name='setup_currency_updated_by')

    def __str__(self):
        return self.code


class ExchangeRate(models.Model):
    class Meta:
        db_table = 'setup_exchange_rates'

    amount = models.DecimalField(decimal_places=2, max_digits=16)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    created_by = CurrentUserField()
    updated_by = CurrentUserField(
        on_update=True, related_name='setup_exchange_rate_updated_by')

    def __str__(self):
        return self.currency.code

    def currency_info(self):
        return self.currency.code
