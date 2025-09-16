from rest_framework import serializers

from nluis_projects.models import (
    Project,
    ProjectType,
    TeamMember,
    Document,
    ProjectSignatory,
    Remark,
    TeamMemberHistory,
    LocalityProject,
)
from nluis_form_management.models import FormData, CustomFormField
from nluis_projects.consts import ProjectApprovalStatus


#     auth_by = CurrentUserField(blank=True, null=True, related_name="auth_by")

#     funders = models.ManyToManyField(Funder)
#     module_level = models.ForeignKey(
#         "nluis_form_management.ModuleLevel",
#         related_name="module_level_projects",
#         on_delete=models.CASCADE,
#     )
#     project_type = models.ForeignKey(
#         ProjectType, blank=True, null=True, on_delete=models.CASCADE
#     )
#     name = models.CharField(max_length=100)
#     description = models.TextField(blank=True, null=True)

#     registered_as = models.CharField(
#         max_length=100, default="existing", blank=True, null=True
#     )
#     budget = models.DecimalField(
#         max_digits=10, decimal_places=2, blank=True, null=True)

#     status = models.ForeignKey(
#         ProjectStatus, on_delete=models.DO_NOTHING, null=True, blank=True
#     )
#     remarks = models.TextField(blank=True, null=True)
#     action = models.CharField(
#         max_length=50,
#         blank=True,
#         null=True,
#         choices=(("Approved", "Approved"), ("Rejected", "Rejected")),
#     )

#     created_at = models.DateTimeField(auto_now_add=True)
#     created_by = CurrentUserField()
#     updated_at = models.DateTimeField(auto_now=True)
#     updated_by = CurrentUserField(
#         on_update=True, related_name="lus_updated_by")


class LocalityProjectSerializer(serializers.ModelSerializer):
    locality__id = serializers.IntegerField(source="locality.id")
    locality__name = serializers.CharField(source="locality.name")
    locality__level = serializers.IntegerField(source="locality.level_id")
    progress = serializers.SerializerMethodField()

    def get_progress(self, obj):
        
        workflow = obj.project.module_level.workflows.filter(is_active=True).first()

        sections = workflow.sections.filter(is_active=True).order_by('position')
        
        form_fields = CustomFormField.objects.filter(is_active=True, form__section__in=sections)

        total_fields = form_fields.count()

        filled_fields = FormData.objects.filter(locality_project=obj, form_field__in=form_fields).distinct().count()
        
        return round((filled_fields / total_fields * 100), 2) if total_fields > 0 else 0

    class Meta:
        model = LocalityProject
        fields = ["id", "locality__id", "locality__name", "locality__level", "approval_status", "remarks", "progress"]


class ProjectListSerializer(serializers.ModelSerializer):
    organization = serializers.CharField(source="organization.name")
    registration_date = serializers.CharField(source="reg_date")
    authorization_date = serializers.CharField(source="auth_date")
    localities = LocalityProjectSerializer(many=True, read_only=True)
    class Meta:
        model = Project
        fields = [
            "id",
            "organization",
            "name",
            "reference_number",
            "registration_date",
            "authorization_date",
            "budget",
            "project_status",
            "approval_status",
            "remarks",
            "created_at",
            "total_locality",
            "total_funders",
            "localities",
        ]


class MonitoringListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "reg_date",
            "auth_date",
            "remarks",
            "datetime",
            "project_type",
        ]


class ProjectTypeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectType
        fields = [
            "id",
            "name",
            "level_info",
            "public_view",
            "duration",
            "duration_alert",
        ]


class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = ["id", "user_info", "team_position", "project_info", "professional"]


class TeamMemberHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMemberHistory
        fields = ["id", "user_info", "team_position", "project_info", "professional"]


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            "id",
            "description",
            "locality_info",
            "project_info",
            "type_info",
            "file",
        ]


class SignatorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectSignatory
        fields = [
            "id",
            "first_name",
            "middle_name",
            "last_name",
            "phone",
            "fullname",
            "locality",
        ]


class RemarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Remark
        fields = ["id", "action", "description", "created_user"]


class ProjectApprovalSerializer(serializers.ModelSerializer):
    approval_status = serializers.ChoiceField(
        choices=ProjectApprovalStatus.choices,
        help_text="1 = Waiting, 2 = Approved, 3 = Rejected"
    )

    class Meta:
        model = Project
        fields = ["approval_status", "remarks"]
