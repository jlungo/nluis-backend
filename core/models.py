from account.models import User
from django.db import models
from django_currentuser.db.models import CurrentUserField


class AuditableModel(models.Model):
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = CurrentUserField(related_name="%(class)s_created_by", null=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    deleted_by = CurrentUserField(related_name="%(class)s_deleted_by", blank=True, null=True)

    class Meta:
        abstract = True
