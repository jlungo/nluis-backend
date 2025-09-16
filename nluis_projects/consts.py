from django.db import models


class ProjectStatus(models.IntegerChoices):
    PENDING = 1, "Pending"
    IN_PROCESS = 2, "In Process"
    COMPLETED = 3, "Completed"
    ON_HOLD = 4, "On Hold"


class ProjectApprovalStatus(models.IntegerChoices):
    WAITING_FOR_APPROVAL = 1, "Waiting for Approval"
    APPROVED = 2, "Approved"
    REJECTED = 3, "Rejected"
