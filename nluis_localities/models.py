from django.contrib.gis.db import models as gismodels
from django.db import models

# Create your models here.
from django_currentuser.db.models import CurrentUserField


class LocalityLevel(models.Model):
    class Meta:
        db_table = 'setup_locality_levels'
        ordering = ['-id']

    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    code = models.CharField(max_length=10, blank=True, null=True)
    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL, related_name='child_levels')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = CurrentUserField()
    updated_by = CurrentUserField(
        on_update=True, related_name='setup_locality_levels_updated_by')

    def __str__(self):
        return self.name



class Locality(models.Model):
    class Meta:
        db_table = 'locality_localities'
        verbose_name_plural = 'Localities'
        unique_together = ['name', 'level', 'parent']

    name = models.CharField(max_length=50)
    parent = models.ForeignKey(
        'self', on_delete=models.PROTECT, blank=True, null=True)
    level = models.ForeignKey(
        LocalityLevel, on_delete=models.PROTECT, blank=False, null=False)
    geom = gismodels.MultiPolygonField(srid=4326, null=True, blank=True)  
    code = models.CharField(max_length=50, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    centroid = gismodels.PointField(srid=4326, null=True, blank=True) 
    updated_at = models.DateTimeField(auto_now=True)
    created_by = CurrentUserField()
    updated_by = CurrentUserField(
        on_update=True, related_name='locality_localities_updated_by')

    def __str__(self):
        return f'{self.name} - {self.level}'

    # keep centroid in sync on save (if geom provided)
    def save(self, *args, **kwargs):
        if self.geom and self.geom.srid != 4326:
            self.geom.srid = 4326  # normalize
        if self.geom:
            # compute centroid for quick labeling
            self.centroid = self.geom.centroid
            self.centroid.srid = 4326
        super().save(*args, **kwargs)
