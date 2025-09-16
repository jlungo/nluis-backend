from django.db import models


class OrganizationLevel(models.IntegerChoices):
    PARENT_ORGANIZATION = 1, "Parent organization"
    CHILD_ORGANIZATION = 2, "Child organization"


class OrganizationStatus(models.IntegerChoices):
    PENDING = 1, "Pending"
    ACTIVE = 2, "Active"
    INACTIVE = 3, "Inactive"
