from django.db import models
from django.contrib.gis.db import models as gismodels
from django_currentuser.db.models import CurrentUserField
from django.utils import timezone
from nluis_localities.models import Locality
from nluis_setups.models import LandUse
from django.contrib.postgres.indexes import GistIndex

class LandUsePlan(models.Model):
    """A plan document for a specific admin unit (e.g., VLUP 2025 for Village A)."""
    name = models.CharField(max_length=150)
    locality = models.OneToOneField(Locality, on_delete=models.CASCADE, related_name='plans')  # plan coverage
    effective_from = models.DateField(default=timezone.now)
    effective_to = models.DateField(null=True, blank=True)  # null = still valid
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = CurrentUserField()
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = CurrentUserField(on_update=True, related_name='landuseplan_updated_by')

    class Meta:
        indexes = [
            models.Index(fields=['locality']),
            models.Index(fields=['effective_from', 'effective_to']),
        ]

    def __str__(self):
        return self.name


class LandUseZone(models.Model):
    """Polygonal zone assigned to a LandUse within a Plan."""
    STATUS_CHOICES = [
        ("Draft", "Draft"),
        ("In Review", "In Review"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    ]

    # plan = models.ForeignKey(LandUsePlan, on_delete=models.CASCADE, related_name='zones') REmove this here.
    land_use = models.ForeignKey(LandUse, on_delete=models.PROTECT)
    locality = models.ForeignKey(Locality, on_delete=models.PROTECT, related_name='zones')

    geom = gismodels.MultiPolygonField(srid=4326)
    area_sqm = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Draft")  # NEW
    source = models.CharField(max_length=200, blank=True)
    version = models.PositiveIntegerField(default=1)
    deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = CurrentUserField()
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = CurrentUserField(on_update=True, related_name='landusezone_updated_by')

    class Meta:
        indexes = [
            GistIndex(fields=['geom']),
            models.Index(fields=['land_use']),
            models.Index(fields=['locality']),
            models.Index(fields=['status']),  # NEW (for quick status filters)
        ]

    def save(self, *args, **kwargs):
        # keep your existing area computation
        if self.geom and self.geom.srid != 4326:
            self.geom.srid = 4326
        if self.geom:
            geom_metric = self.geom.transform(32737, clone=True)  # adjust per locality if needed
            self.area_sqm = round(geom_metric.area, 2)
        super().save(*args, **kwargs)