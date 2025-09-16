from django.contrib.gis.db.models import PointField, GeometryField
from django.db import models
from django.contrib.auth.models import Group
from account.models import User
from core.models import AuditableModel


# Create your models here.
from django_currentuser.db.models import CurrentUserField

from libs.fxs import get_ukubwa, get_image_url
from nluis_collect.models import FormAnswer
from nluis_localities.models import Locality
from nluis_setups.models import Funder
import dateutil
import datetime
from dateutil import relativedelta
from organization.models import Organization
from .consts import *


# class ProjectStatus(models.Model):
#     class Meta:
#         db_table = "project_project_status"
#         verbose_name_plural = "Project Status"

#     name = models.CharField(max_length=50, unique=True)
#     code = models.CharField(max_length=50, blank=True, null=True)
#     description = models.TextField()
#     created_date = models.DateField(auto_now_add=True)
#     created_time = models.TimeField(auto_now_add=True)
#     created_by = CurrentUserField()
#     updated_by = CurrentUserField(
#         on_update=True, related_name="project_status_updated_by"
#     )


class ProjectType(models.Model):
    class Meta:
        db_table = "project_project_types"

    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=50, unique=True)
    level = models.ForeignKey(
        "nluis_localities.LocalityLevel",
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
    )
    is_monitoring = models.BooleanField(default=False)
    public_view = models.BooleanField(default=False)
    duration = models.IntegerField(null=True, blank=True)
    duration_alert = models.IntegerField(null=True, blank=True)
    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    created_by = CurrentUserField()
    updated_by = CurrentUserField(
        on_update=True, related_name="project_types_updated_by"
    )

    def __str__(self):
        return self.name

    def level_info(self):
        return {"id": self.level.id, "name": self.level.name}


class Project(models.Model):
    class Meta:
        db_table = "project_projects"

    organization = models.ForeignKey(
        Organization,
        related_name="organization_projects",
        on_delete=models.CASCADE,
    )
    reference_number = models.CharField(max_length=255, blank=True, null=True)
    reg_date = models.DateField(auto_now_add=True, blank=True, null=True)
    auth_date = models.DateField(blank=True, null=True)
    published_date = models.DateField(blank=True, null=True)
    auth_by = CurrentUserField(blank=True, null=True, related_name="auth_by")

    funders = models.ManyToManyField(Funder)
    module_level = models.ForeignKey(
        "nluis_form_management.ModuleLevel",
        related_name="module_level_projects",
        on_delete=models.CASCADE,
    )
    project_type = models.ForeignKey(
        ProjectType, blank=True, null=True, on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    registered_as = models.CharField(
        max_length=100, default="existing", blank=True, null=True
    )
    currency_type = models.ForeignKey("nluis_setups.Currency", related_name="project_budget_currencies", on_delete=models.SET_NULL, blank=True, null=True)
    budget = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    project_status = models.IntegerField(
        choices=ProjectStatus.choices, default=ProjectStatus.PENDING
    )
    approval_status = models.IntegerField(
        choices=ProjectApprovalStatus.choices,
        default=ProjectApprovalStatus.WAITING_FOR_APPROVAL,
    )
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = CurrentUserField()
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = CurrentUserField(on_update=True, related_name="lus_updated_by")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def datetime(self):
        return str(f"{self.created_at}")[:16]

    def project_type_info(self):
        return {
            "id": self.project_type.id,
            "name": self.project_type.name,
            "duration": self.project_type.duration,
        }

    def total_locality(self):
        return self.localities.count()
    
    def total_funders(self):
        return self.funders.count()


    def age(self):
        now = datetime.datetime.utcnow()
        now = now.date()

        # Get the difference between the current date and auth date
        age = dateutil.relativedelta.relativedelta(now, self.published_date)
        return age.years


class LocalityProject(AuditableModel):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="localities"
    )
    locality = models.ForeignKey(Locality, on_delete=models.CASCADE)
    approval_status = models.IntegerField(
        choices=ProjectApprovalStatus.choices,
        default=ProjectApprovalStatus.WAITING_FOR_APPROVAL,
    )
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "locality_project"
        ordering = ["-id"]


class TeamMember(models.Model):
    class Meta:
        db_table = "project_team_members"
        unique_together = ["project", "user", "locality"]
        ordering = ["-id"]

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=100, blank=True, null=True)
    locality = models.ForeignKey(
        "nluis_localities.Locality", on_delete=models.SET_NULL, null=True, blank=True
    )
    team_position = models.CharField(max_length=50, null=True, blank=True)
    professional = models.CharField(max_length=100)
    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    created_by = CurrentUserField(related_name="project_team_member_created_by")
    updated_by = CurrentUserField(
        on_update=True, related_name="project_team_member_updated_by"
    )
    updated_date = models.DateField(auto_now=True)
    updated_time = models.TimeField(auto_now=True)
    status = models.CharField(max_length=10, null=True)
    dodoso_categories = models.CharField(max_length=250, null=True)

    def project_info(self):
        return {"id": self.project.id, "name": self.project.name}

    def user_info(self):
        total_data = (
            FormAnswer.objects.distinct("claim_no")
            .exclude(claim_no__contains="_")
            .filter(para_surveyor=self, project=self.project)
            .count()
        )
        return {
            "id": self.user.id,
            "username": self.user.username,
            "role_name": self.user.groups.values_list("name"),
            "fullname": f"{self.user.first_name} {self.user.last_name}",
            "project_boundary": self.locality.name if self.locality is not None else "",
            "total_data": total_data,
        }


class ProjectHistory(models.Model):
    class Meta:
        db_table = "project_project_history"
        verbose_name_plural = "Project History"

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    screen_code = models.CharField(max_length=50, blank=True, null=True)
    action = models.CharField(max_length=50)
    remarks = models.TextField(blank=True, null=True)

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    created_by = CurrentUserField()
    updated_by = CurrentUserField(on_update=True, related_name="history_updated_by")


class ProjectSignatory(models.Model):
    class Meta:
        db_table = "project_project_signatory"
        unique_together = ["project", "locality", "designation"]
        verbose_name_plural = "Project Signatories"

    project = models.ForeignKey(
        Project, on_delete=models.DO_NOTHING, blank=True, null=True
    )
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    designation = models.ForeignKey(
        "nluis_setups.Designation", on_delete=models.DO_NOTHING, null=True, blank=True
    )
    signature = models.ImageField(upload_to="signatories")
    phone = models.CharField(max_length=20, blank=True, null=True)
    locality = models.ForeignKey(
        "nluis_localities.Locality", on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return self.fullname()

    def fullname(self):
        return f"{self.first_name} {self.middle_name} {self.last_name}".title()

    # def info(self):
    #     return {
    #         'layer': ''
    #     }


class Document(models.Model):
    class Meta:
        db_table = "project_documents"

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    locality = models.ForeignKey(
        "nluis_localities.Locality", on_delete=models.CASCADE, blank=True, null=True
    )
    document_type = models.ForeignKey(
        "nluis_setups.DocumentType", on_delete=models.CASCADE
    )
    description = models.TextField(max_length=50)
    file = models.FileField(upload_to="documents", blank=True, null=True)
    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    created_by = CurrentUserField()
    updated_by = CurrentUserField(
        on_update=True, related_name="project_documents_updated_by"
    )

    def __str__(self):
        return self.document_type.name

    def datetime(self):
        return str(f"{self.created_date} {self.created_time}")[:16]

    def project_info(self):
        return {"id": self.project.id, "name": self.project.name}

    def locality_info(self):
        return {"id": self.locality.id, "name": self.locality.name}

    def type_info(self):
        return {"id": self.document_type.id, "name": self.document_type.name}

    @property
    def file_url(self):
        if self.file and hasattr(self.file, "url"):
            return self.file.url
        else:
            return ""


class MultiMedia(models.Model):
    class Meta:
        db_table = "project_multimedia"

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    locality = models.ForeignKey(
        "nluis_localities.Locality", on_delete=models.CASCADE, blank=True, null=True
    )
    description = models.TextField(max_length=50)
    path = models.ImageField(upload_to="multimedia", blank=True, null=True)

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    created_by = CurrentUserField()
    updated_by = CurrentUserField(
        on_update=True, related_name="project_multimedia_updated_by"
    )


class Remark(models.Model):
    class Meta:
        db_table = "project_remark"

    action = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)

    created_by = CurrentUserField()
    deleted = models.BooleanField(default=False)
    updated_by = CurrentUserField(on_update=True, related_name="remark_updated_by")

    def __str__(self):
        return self.description

    def datetime(self):
        return str(f"{self.created_date} {self.created_time}")[:16]

    def created_user(self):
        print(self.created_by)
        return self.created_by.username if self.created_by is not None else ""


class TeamMemberHistory(models.Model):
    class Meta:
        db_table = "project_team_members_history"
        ordering = ["-id"]

    project = models.ForeignKey(Project, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    device_id = models.CharField(max_length=100, blank=True, null=True)
    locality = models.ForeignKey(
        "nluis_localities.Locality", on_delete=models.DO_NOTHING, null=True, blank=True
    )
    team_position = models.CharField(max_length=50, null=True, blank=True)
    professional = models.CharField(max_length=100)
    created_date = models.DateField()
    created_time = models.TimeField()
    change_date = models.DateField(auto_now_add=True)
    change_time = models.TimeField(auto_now_add=True)
    para_surveyor_id = models.IntegerField(null=True, default="0")
    dodoso_categories = models.CharField(max_length=250, null=True)

    def project_info(self):
        return {"id": self.project.id, "name": self.project.name}

    def user_info(self):
        total_data = (
            FormAnswer.objects.distinct("claim_no")
            .exclude(claim_no__contains="_")
            .filter(para_surveyor_id=self.para_surveyor_id, project=self.project)
            .count()
        )
        return {
            "id": self.user.id,
            "username": self.user.username,
            "role_name": self.user.groups.values_list("name"),
            "fullname": f"{self.user.first_name} {self.user.last_name}",
            "project_boundary": self.locality.name if self.locality is not None else "",
            "total_data": total_data,
        }


class Chapter(models.Model):
    class Meta:
        db_table = "project_chapters"

    name = models.CharField(null=False, max_length=100)
    project_type = models.ForeignKey(ProjectType, on_delete=models.DO_NOTHING)

    def __str__(self):
        return str(f"{self.id} - {self.name} - {self.project_type.name}")

    def project_type_name(self):
        return self.project_type.name
