from django.db import models
from django_currentuser.db.models import CurrentUserField

# Create your models here.


class Report(models.Model):
    class Meta:
        db_table = 'reports'

    name = models.CharField(max_length=200, unique=True)
    endpoint = models.CharField(
        max_length=50, blank=True, null=True, unique=True)
    filter = models.CharField(
        max_length=1000, blank=True, null=True)
    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    created_by = CurrentUserField()
    updated_by = CurrentUserField(
        on_update=True, related_name='report_updated_by')
