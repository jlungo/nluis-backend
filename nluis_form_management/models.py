from django.db import models
from account.models import Module, UserRole
from autoslug import AutoSlugField
from core.models import AuditableModel
from nluis_projects.models import Project
from .consts import *


class ModuleLevel(AuditableModel):
    slug = AutoSlugField(populate_from="name", unique=True)
    name = models.CharField(max_length=255)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="levels")

    class Meta:
        db_table = "level"
        ordering = ["-id"]

    def __str__(self):
        return self.name


class FormWorkflow(AuditableModel):
    module_level = models.ForeignKey(
        ModuleLevel, on_delete=models.CASCADE, related_name="workflows"
    )
    slug = AutoSlugField(populate_from="name", unique=True)
    name = models.CharField(max_length=255)
    category = models.IntegerField(choices=WorkFlowCategoryType.choices)
    description = models.TextField(blank=True, null=True)
    version = models.IntegerField()

    class Meta:
        db_table = "form_workflow"
        ordering = ["-id"]

    def __str__(self):
        return self.name


class Section(AuditableModel):
    form_workflow = models.ForeignKey(
        FormWorkflow, on_delete=models.CASCADE, related_name="sections"
    )
    slug = AutoSlugField(populate_from="name", unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "section"
        ordering = ["-id"]

    def __str__(self):
        return self.name


class SectionApprovalRole(AuditableModel):
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, related_name="approval_roles"
    )
    user_role = models.ForeignKey(
        UserRole, on_delete=models.CASCADE, related_name="section_approval_roles"
    )

    class Meta:
        db_table = "section_approval_role"
        constraints = [
            models.UniqueConstraint(
                fields=["section", "user_role"],
                condition=models.Q(is_active=True),
                name="unique_section_and_user_role_when_is_active",
            )
        ]
        ordering = ["-id"]

    def __str__(self):
        return f"{self.user_role} - {self.section}"


class CustomForm(AuditableModel):
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, related_name="forms", blank=True, null=True
    )
    slug = AutoSlugField(populate_from="name", unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "form"
        ordering = ["-id"]

    def __str__(self):
        return self.name


class CustomerFormEditorRole(AuditableModel):
    customer_form = models.ForeignKey(
        CustomForm, on_delete=models.CASCADE, related_name="editor_roles"
    )
    user_role = models.ForeignKey(
        UserRole, on_delete=models.CASCADE, related_name="customer_form_editor_roles"
    )

    class Meta:
        db_table = "customer_form_editor_role"
        constraints = [
            models.UniqueConstraint(
                fields=["customer_form", "user_role"],
                condition=models.Q(is_active=True),
                name="unique_customer_form_and_user_role_when_is_active",
            )
        ]
        ordering = ["-id"]

    def __str__(self):
        return f"{self.user_role} - {self.customer_form}"


class CustomFormField(AuditableModel):
    form = models.ForeignKey(CustomForm, on_delete=models.CASCADE, related_name="form_fields")
    label = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=FieldType.choices)
    placeholder = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255)
    required = models.BooleanField(default=False)
    is_support_multiple_selection = models.BooleanField(default=False)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "form_field"
        unique_together = ("form", "name")
        ordering = ["-id"]

    def __str__(self):
        return self.label


class FieldSelectOption(AuditableModel):
    field = models.ForeignKey(
        CustomFormField,
        on_delete=models.CASCADE,
        related_name="select_options",
        limit_choices_to={"type__in": [FieldType.SELECT, FieldType.RADIO, FieldType.CHECKBOX]}
    )
    text_label = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "form_select_option"
        unique_together = ("field", "value")
        ordering = ["-id"]

    def __str__(self):
        return self.text_label


class FormData(AuditableModel):
    form_field = models.ForeignKey(
        CustomFormField,
        on_delete=models.CASCADE,
        related_name="form_data",
    )
    locality_project = models.ForeignKey(
        "nluis_projects.LocalityProject",
        on_delete=models.CASCADE,
        related_name="locality_project_form_data",
    )
    slug = AutoSlugField(populate_from="value", unique=True)
    value = models.CharField(max_length=255)
    team_member = models.JSONField(blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    
    class Meta:
        db_table = "form_data"
        ordering = ["-id"]

    def __str__(self):
        return self.value
