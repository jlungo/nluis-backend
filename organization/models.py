from django.db import models
from .consts import *
import uuid

class OrganizationType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=5000)

    class Meta:
        db_table="organization_type"
        ordering = ["-id"]


class Organization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=5000)
    short_name = models.CharField(max_length=1000)
    url = models.URLField(max_length=2000, null=True, blank=True)
    type = models.ForeignKey(OrganizationType, on_delete=models.CASCADE)
    level = models.PositiveSmallIntegerField(choices=OrganizationLevel.choices, default=OrganizationLevel.CHILD_ORGANIZATION)
    status = models.IntegerField(choices=OrganizationStatus.choices, default=OrganizationStatus.PENDING) # TODO: Limit parent to only one.
    address = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.name
