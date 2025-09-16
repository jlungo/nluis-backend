from django.contrib.gis.db.models import PointField, GeometryField
from django.db import models
from libs.fxs import get_ukubwa

# Create your models here.
from django_currentuser.db.models import CurrentUserField


class SpatialUnit(models.Model):
    class Meta:
        db_table = 'spatial_unit'

    project = models.ForeignKey(
        'nluis_projects.Project', on_delete=models.CASCADE, blank=True, null=True)
    locality = models.ForeignKey(
        'nluis_localities.Locality', on_delete=models.CASCADE, blank=True, null=True)
    geometry_type = models.ForeignKey('nluis_setups.LandUseGeometryType', on_delete=models.CASCADE, blank=True,
                                      null=True)
    land_use = models.ForeignKey(
        'nluis_setups.LandUse', on_delete=models.CASCADE, blank=True, null=True)
    description = models.CharField(max_length=50, blank=True, null=True)
    sqm = models.DecimalField(max_digits=10, decimal_places=3)
    width = models.DecimalField(max_digits=10, decimal_places=3)
    length = models.DecimalField(max_digits=10, decimal_places=3)
    geom = GeometryField(blank=True, null=True)
    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    created_by = CurrentUserField()
    deleted = models.BooleanField(default=False)
    updated_by = CurrentUserField(
        on_update=True, related_name='spatial_unit_updated_by')

    # def datetime(self):
    #     return str(f'{self.created_date} {self.created_time}')[:16]

    def __str__(self):
        return self.description

    def use(self):
        return self.land_use.name


class Beacon(models.Model):
    class Meta:
        db_table = 'project_beacons'
        unique_together = ['deed_plan_info', 'name']

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    created_by = CurrentUserField()
    deleted = models.BooleanField(default=False)
    updated_by = CurrentUserField(
        on_update=True, related_name='point_spatial_updated_by')

    project = models.ForeignKey(
        'nluis_projects.Project', on_delete=models.CASCADE, blank=True, null=True)
    deed_plan_info = models.ForeignKey(
        'nluis_ccro.DeedPlan', on_delete=models.CASCADE, null=True, blank=True)
    geom = PointField(blank=True, null=True)
    srid = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=50, blank=True, null=True)

    def datetime(self):
        return str(f'{self.created_date} {self.created_time}')[:16]

    def __str__(self):
        return self.name
