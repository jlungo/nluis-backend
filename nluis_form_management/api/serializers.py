from rest_framework import serializers
from account.models import Module, UserRole
from nluis_form_management.models import ModuleLevel, FormWorkflow, Section, CustomForm, CustomFormField, FieldSelectOption, FormData, SectionApprovalRole, CustomerFormEditorRole
from nluis_projects.models import Project
from nluis_form_management.consts import FieldType
from rest_framework.validators import UniqueTogetherValidator
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError


class ModuleLevelSerializer(serializers.ModelSerializer):
    module_slug = serializers.CharField(source="module.slug")
    module_name = serializers.CharField(source="module.name")
    class Meta:
        model = ModuleLevel
        fields = ["slug", "name", "module_slug", "module_name"]


class UpdateModuleLevelSerializer(serializers.ModelSerializer):
    module = serializers.SlugRelatedField(
        slug_field="slug", queryset=Module.objects.all()
    )

    class Meta:
        model = ModuleLevel
        fields = ["name", "module"]

    def update(self, instance, validated_data):
        name = validated_data.get("name")
        module = validated_data.get("module")
        
        update_fields = []
        if name is not None:
            instance.name = name
            update_fields.append("name")
        if module is not None:
            instance.module = module
            update_fields.append("module")
        if update_fields:
            instance.save(update_fields=update_fields)
        return instance


class CreateModuleLevelSerializer(serializers.ModelSerializer):
    module = serializers.SlugRelatedField(slug_field="slug", queryset=Module.objects.all())

    class Meta:
        model = ModuleLevel
        fields = ["name", "module"]

    
class FieldSelectOptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = FieldSelectOption
        fields = ["id", "text_label", "value", "position"]


class FormFieldSerializer(serializers.ModelSerializer):
    form_slug = serializers.CharField(source="form.slug", read_only=True)
    form_name = serializers.CharField(source="form.name", read_only=True)
    section_slug = serializers.CharField(source="form.section.slug", read_only=True)
    section_name = serializers.CharField(source="form.section.name", read_only=True)
    workflow_slug = serializers.CharField(source="form.section.form_workflow.slug", read_only=True)
    workflow_name = serializers.CharField(source="form.section.form_workflow.name", read_only=True)
    module_level_slug = serializers.CharField(source="form.section.form_workflow.module_level.slug", read_only=True)
    module_level_name = serializers.CharField(source="form.section.form_workflow.module_level.name", read_only=True)
    module_slug = serializers.CharField(source="form.section.form_workflow.module_level.module.slug", read_only=True)
    module_name = serializers.CharField(source="form.section.form_workflow.module_level.module.name", read_only=True)
    type_display = serializers.CharField(source="get_type_display", read_only=True)
    select_options = FieldSelectOptionSerializer(many=True, read_only=True)

    class Meta:
        model = CustomFormField
        fields = [
            "id",
            "label",
            "type",
            "type_display",
            "placeholder",
            "name",
            "required",
            "position",
            "is_active",
            "form_slug",
            "form_name",
            "section_slug",
            "section_name",
            "workflow_slug",
            "workflow_name",
            "module_level_slug",
            "module_level_name",
            "module_slug",
            "module_name",
            "select_options",
        ]


class CustomerFormEditorRoleSerializer(serializers.ModelSerializer):
    role_id = serializers.CharField(source="user_role.id", read_only=True)
    role_name = serializers.CharField(source="user_role.name", read_only=True)
    class Meta:
        model = CustomerFormEditorRole
        fields = ["id", "role_id", "role_name"]


class FormSerializer(serializers.ModelSerializer):
    section_slug = serializers.CharField(source="section.slug", read_only=True)
    section_name = serializers.CharField(source="section.name", read_only=True)
    workflow_slug = serializers.CharField(source="section.form_workflow.slug", read_only=True)
    workflow_name = serializers.CharField(source="section.form_workflow.name", read_only=True)
    module_level_slug = serializers.CharField(source="section.form_workflow.module_level.slug", read_only=True)
    module_level_name = serializers.CharField(source="section.form_workflow.module_level.name", read_only=True)
    module_slug = serializers.CharField(source="section.form_workflow.module_level.module.slug", read_only=True)
    module_name = serializers.CharField(source="section.form_workflow.module_level.module.name", read_only=True)
    # fields = FormFieldSerializer(many=True, read_only=True)
    form_fields = serializers.SerializerMethodField()
    editor_roles = CustomerFormEditorRoleSerializer(many=True, read_only=True)

    # forms = serializers.SerializerMethodField()
    # approval_roles = SectionApprovalRoleSerializer(many=True, read_only=True)
    
    def get_form_fields(self, obj):
        active_fields = obj.form_fields.filter(is_active=True)
        return FormFieldSerializer(active_fields, many=True).data

    class Meta:
        model = CustomForm
        fields = [
            "slug",
            "name",
            "description",
            "is_active",
            "section_slug",
            "section_name",
            "workflow_slug",
            "workflow_name",
            "module_level_slug",
            "module_level_name",
            "module_slug",
            "module_name",
            "position",
            "form_fields",
            "editor_roles",
        ]


class SectionApprovalRoleSerializer(serializers.ModelSerializer):
    role_id = serializers.CharField(source="user_role.id", read_only=True)
    role_name = serializers.CharField(source="user_role.name", read_only=True)
    user_role = serializers.PrimaryKeyRelatedField(queryset=UserRole.objects.all(), write_only=True)

    class Meta:
        model = SectionApprovalRole
        fields = ["id", "role_id", "role_name", "user_role"]
        

class SectionSerializer(serializers.ModelSerializer):
    workflow_slug = serializers.CharField(source="form_workflow.slug", read_only=True)
    workflow_name = serializers.CharField(source="form_workflow.name", read_only=True)
    module_level_slug = serializers.CharField(source="form_workflow.module_level.slug", read_only=True)
    module_level_name = serializers.CharField(source="form_workflow.module_level.name", read_only=True)
    module_slug = serializers.CharField(source="form_workflow.module_level.module.slug", read_only=True)
    module_name = serializers.CharField(source="form_workflow.module_level.module.name", read_only=True)
    forms = serializers.SerializerMethodField()
    approval_roles = SectionApprovalRoleSerializer(many=True, read_only=True)

    def get_forms(self, obj):
        active_forms = obj.forms.filter(is_active=True)
        return FormSerializer(active_forms, many=True).data

    class Meta:
        model = Section
        fields = [
            "slug",
            "name",
            "description",
            "position",
            "is_active",
            "workflow_slug",
            "workflow_name",
            "module_level_slug",
            "module_level_name",
            "module_slug",
            "module_name",
            "forms",
            "approval_roles",
        ]


class FormWorkflowSerializer(serializers.ModelSerializer):
    module_level_slug = serializers.CharField(source="module_level.slug", read_only=True)
    module_level_name = serializers.CharField(source="module_level.name", read_only=True)
    module_slug = serializers.CharField(source="module_level.module.slug", read_only=True)
    module_name = serializers.CharField(source="module_level.module.name", read_only=True)
    # sections_count = serializers.IntegerField(source="sections.count", read_only=True)
    sections_count = serializers.SerializerMethodField()
    # sections = SectionSerializer(many=True, read_only=True)
    sections = serializers.SerializerMethodField()

    def get_sections_count(self, obj):
        return obj.sections.filter(is_active=True).count()

    def get_sections(self, obj):
        active_sections = obj.sections.filter(is_active=True)
        return SectionSerializer(active_sections, many=True).data

    class Meta:
        model = FormWorkflow
        fields = [
            "slug",
            "name",
            "category",
            "description",
            "version",
            "is_active",
            "module_level_slug",
            "module_level_name",
            "module_slug",
            "module_name",
            "sections_count",
            "sections",
        ]


class CreateFormWorkflowSerializer(serializers.ModelSerializer):
    module_level = serializers.SlugRelatedField(
        slug_field="slug", queryset=ModuleLevel.objects.all()
    )

    class Meta:
        model = FormWorkflow
        fields = ["name", "description", "version", "module_level"]


class UpdateFormWorkflowSerializer(serializers.ModelSerializer):
    module_level = serializers.SlugRelatedField(
        slug_field="slug", queryset=ModuleLevel.objects.all(), required=False
    )

    class Meta:
        model = FormWorkflow
        fields = ["name", "description", "version", "module_level", "is_active"]

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance


class FormDataSerializer(serializers.ModelSerializer):
    form_field_id = serializers.IntegerField(source="form_field.id", read_only=True)
    field_label = serializers.CharField(source="form_field.label", read_only=True)
    field_name = serializers.CharField(source="form_field.name", read_only=True)
    field_type = serializers.CharField(source="form_field.type", read_only=True)
    form_slug = serializers.CharField(source="form_field.form.slug", read_only=True)
    form_name = serializers.CharField(source="form_field.form.name", read_only=True)
    section_slug = serializers.CharField(source="form_field.form.section.slug", read_only=True)
    section_name = serializers.CharField(source="form_field.form.section.name", read_only=True)
    workflow_slug = serializers.CharField(source="form_field.form.section.form_workflow.slug", read_only=True)
    workflow_name = serializers.CharField(source="form_field.form.section.form_workflow.name", read_only=True)
    module_level_slug = serializers.CharField(source="form_field.form.section.form_workflow.module_level.slug", read_only=True)
    module_level_name = serializers.CharField(source="form_field.form.section.form_workflow.module_level.name", read_only=True)
    module_slug = serializers.CharField(source="form_field.form.section.form_workflow.module_level.module.slug", read_only=True)
    module_name = serializers.CharField(source="form_field.form.section.form_workflow.module_level.module.name", read_only=True)
    project_slug = serializers.CharField(source="project.slug", read_only=True)
    project_name = serializers.CharField(source="project.name", read_only=True)

    class Meta:
        model = FormData
        fields = [
            "id",
            "slug",
            "value",
            # "version",
            "is_active",
            "form_field",
            # "project", //muted by simon
            "form_field_id",
            "field_label",
            "field_name",
            "field_type",
            "form_slug",
            "form_name",
            "section_slug",
            "section_name",
            "workflow_slug",
            "workflow_name",
            "module_level_slug",
            "module_level_name",
            "module_slug",
            "module_name",
            "project_slug",
            "project_name",
        ]


class CreateFormDataSerializer(serializers.ModelSerializer):
    form_field = serializers.PrimaryKeyRelatedField(queryset=CustomFormField.objects.all())
    project = serializers.SlugRelatedField(slug_field="slug", queryset=Project.objects.all(), required=False, allow_null=True)

    class Meta:
        model = FormData
        fields = ["form_field", "project", "value"]


class UpdateFormDataSerializer(serializers.ModelSerializer):
    form_field = serializers.PrimaryKeyRelatedField(queryset=CustomFormField.objects.all(), required=False)
    project = serializers.SlugRelatedField(slug_field="slug", queryset=Project.objects.all(), required=False, allow_null=True)

    class Meta:
        model = FormData
        fields = ["form_field", "project", "value", "is_active"]

    def update(self, instance, validated_data):
        for field_name, value in validated_data.items():
            setattr(instance, field_name, value)
        instance.save()
        return instance

class CreateSectionSerializer(serializers.ModelSerializer):
    form_workflow = serializers.SlugRelatedField(
        slug_field="slug", queryset=FormWorkflow.objects.all()
    )

    class Meta:
        model = Section
        fields = ["name", "description", "position", "form_workflow"]


class UpdateSectionSerializer(serializers.ModelSerializer):
    form_workflow = serializers.SlugRelatedField(
        slug_field="slug", queryset=FormWorkflow.objects.all(), required=False
    )

    class Meta:
        model = Section
        fields = ["name", "description", "position", "form_workflow", "is_active"]

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance


class CreateFormSerializer(serializers.ModelSerializer):
    section = serializers.SlugRelatedField(
        slug_field="slug", queryset=Section.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = CustomForm
        fields = ["name", "description", "section"]


class UpdateFormSerializer(serializers.ModelSerializer):
    section = serializers.SlugRelatedField(
        slug_field="slug", queryset=Section.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = CustomForm
        fields = ["name", "description", "section", "is_active"]

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance


# class FormFieldSerializer(serializers.ModelSerializer):
#     form_slug = serializers.CharField(source="form.slug", read_only=True)
#     form_name = serializers.CharField(source="form.name", read_only=True)
#     section_slug = serializers.CharField(source="form.section.slug", read_only=True)
#     section_name = serializers.CharField(source="form.section.name", read_only=True)
#     workflow_slug = serializers.CharField(source="form.section.form_workflow.slug", read_only=True)
#     workflow_name = serializers.CharField(source="form.section.form_workflow.name", read_only=True)
#     module_level_slug = serializers.CharField(source="form.section.form_workflow.module_level.slug", read_only=True)
#     module_level_name = serializers.CharField(source="form.section.form_workflow.module_level.name", read_only=True)
#     module_slug = serializers.CharField(source="form.section.form_workflow.module_level.module.slug", read_only=True)
#     module_name = serializers.CharField(source="form.section.form_workflow.module_level.module.name", read_only=True)
#     type_display = serializers.CharField(source="get_type_display", read_only=True)

#     class Meta:
#         model = CustomFormField
#         fields = [
#             "id",
#             "label",
#             "type",
#             "type_display",
#             "placeholder",
#             "name",
#             "required",
#             "position",
#             "is_active",
#             "form_slug",
#             "form_name",
#             "section_slug",
#             "section_name",
#             "workflow_slug",
#             "workflow_name",
#             "module_level_slug",
#             "module_level_name",
#             "module_slug",
#             "module_name",
#         ]


class CreateFormFieldSerializer(serializers.ModelSerializer):
    form = serializers.SlugRelatedField(
        slug_field="slug", queryset=CustomForm.objects.all()
    )
    type = serializers.ChoiceField(choices=FieldType.choices)

    class Meta:
        model = CustomFormField
        fields = [
            "form",
            "label",
            "type",
            "placeholder",
            "name",
            "required",
            "position",
        ]
        validators = [
            UniqueTogetherValidator(
                queryset=CustomFormField.objects.all(), fields=["form", "name"]
            )
        ]


class UpdateFormFieldSerializer(serializers.ModelSerializer):
    form = serializers.SlugRelatedField(
        slug_field="slug", queryset=CustomForm.objects.all(), required=False
    )
    type = serializers.ChoiceField(choices=FieldType.choices, required=False)

    class Meta:
        model = CustomFormField
        fields = [
            "form",
            "label",
            "type",
            "placeholder",
            "name",
            "required",
            "position",
            "is_active",
        ]

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance


class FieldSelectOptionSerializer(serializers.ModelSerializer):
    field_id = serializers.IntegerField(source="field.id", read_only=True)
    form_slug = serializers.CharField(source="field.form.slug", read_only=True)
    form_name = serializers.CharField(source="field.form.name", read_only=True)
    section_slug = serializers.CharField(source="field.form.section.slug", read_only=True)
    section_name = serializers.CharField(source="field.form.section.name", read_only=True)
    workflow_slug = serializers.CharField(source="field.form.section.form_workflow.slug", read_only=True)
    workflow_name = serializers.CharField(source="field.form.section.form_workflow.name", read_only=True)
    module_level_slug = serializers.CharField(source="field.form.section.form_workflow.module_level.slug", read_only=True)
    module_level_name = serializers.CharField(source="field.form.section.form_workflow.module_level.name", read_only=True)
    module_slug = serializers.CharField(source="field.form.section.form_workflow.module_level.module.slug", read_only=True)
    module_name = serializers.CharField(source="field.form.section.form_workflow.module_level.module.name", read_only=True)

    class Meta:
        model = FieldSelectOption
        fields = [
            "id",
            "text_label",
            "value",
            "is_active",
            "field_id",
            "form_slug",
            "form_name",
            "section_slug",
            "section_name",
            "workflow_slug",
            "workflow_name",
            "module_level_slug",
            "module_level_name",
            "module_slug",
            "module_name",
        ]


class CreateFieldSelectOptionSerializer(serializers.ModelSerializer):
    field = serializers.PrimaryKeyRelatedField(queryset=CustomFormField.objects.all())

    class Meta:
        model = FieldSelectOption
        fields = ["field", "text_label", "value"]
        validators = [
            UniqueTogetherValidator(
                queryset=FieldSelectOption.objects.all(), fields=["field", "value"]
            )
        ]


class UpdateFieldSelectOptionSerializer(serializers.ModelSerializer):
    field = serializers.PrimaryKeyRelatedField(queryset=CustomFormField.objects.all(), required=False)

    class Meta:
        model = FieldSelectOption
        fields = ["field", "text_label", "value", "is_active"]

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance


class FieldSelectOptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = FieldSelectOption
        fields = ["text_label", "value", "position"]

class FieldInputSerializer(serializers.ModelSerializer):

    select_options = FieldSelectOptionSerializer(many=True)
    id = serializers.IntegerField(required=False)
    is_active = serializers.CharField(required=False)

    class Meta:
        model = CustomFormField
        fields = ["id", "label", "type", "placeholder", "name", "required", "position", "select_options", "is_active"]


class CustomerFormEditorRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerFormEditorRole
        fields = ["user_role"]


class FormInputSerializer(serializers.ModelSerializer):
    # name = serializers.CharField()
    # description = serializers.CharField(allow_null=True, required=False, allow_blank=True)
    form_fields = FieldInputSerializer(many=True)
    editor_roles = CustomerFormEditorRoleSerializer(many=True)
    slug = serializers.CharField(required=False)
    is_active = serializers.CharField(required=False)

    class Meta:
        model = CustomForm
        fields = [
            "slug",
            "name",
            "description",
            "position",
            "editor_roles",
            "form_fields",
            "is_active",
        ]


class SectionInputSerializer(serializers.ModelSerializer):
    forms = FormInputSerializer(many=True)
    approval_roles = SectionApprovalRoleSerializer(many=True)
    slug = serializers.CharField(required=False)
    is_active = serializers.CharField(required=False)

    class Meta:
        model = Section
        fields = [
            "slug",
            "is_active",
            "name",
            "description",
            "position",
            "approval_roles",
            "forms",
        ]


class SubmissionSerializer(serializers.ModelSerializer):
    module_level = serializers.SlugRelatedField(
        slug_field="slug", queryset=ModuleLevel.objects.all()
    )
    sections = SectionInputSerializer(many=True)
    slug = serializers.CharField(read_only=True)

    class Meta:
        model = FormWorkflow
        fields = [
            "slug",
            "name",
            "category",
            "description",
            "module_level",
            "version",
            "sections",
        ]

    def _map_field_type(self, type_value: str):
        if type_value is None:
            return None
        try:
            return int(type_value)
        except (TypeError, ValueError):
            pass
        # Accept enum names like "TEXT", "NUMBER" etc.
        upper_name = str(type_value).strip().upper()
        if upper_name in FieldType.__members__:
            return FieldType[upper_name].value
        # Accept human labels like "Text"
        label_map = {label.upper(): value for value, label in FieldType.choices}
        if upper_name in label_map:
            return label_map[upper_name]
        raise serializers.ValidationError({"type": f"Invalid field type '{type_value}'"})
    

    @transaction.atomic
    def create(self, validated_data):
        sections_data = validated_data.pop("sections", [])
        workflow: FormWorkflow = FormWorkflow.objects.create(**validated_data)
        self._create_sections(workflow, sections_data)
        return workflow

    def _create_sections(self, workflow, sections_data):

        for section_data in sections_data:
            forms_data = section_data.pop("forms", [])
            approval_roles = section_data.pop("approval_roles", [])

            section = Section.objects.create(
                form_workflow=workflow,
                is_active=True,
                **section_data,
            )

            # Save approval roles
            section_roles_to_create = []
            for user_role_data in approval_roles:
                user_role = user_role_data.pop("user_role")
                
                section_roles_to_create.append(
                    SectionApprovalRole(section=section, user_role=user_role, is_active=True)
                )

            if section_roles_to_create:
                SectionApprovalRole.objects.bulk_create(section_roles_to_create)

            # Forms
            for form_data in forms_data:
                fields_data = form_data.pop("form_fields", [])
                editor_roles = form_data.pop("editor_roles", [])

                form = CustomForm.objects.create(
                    section=section,
                    is_active=True,
                    **form_data,
                )

                # Save editor roles
                editor_roles_to_create = []
                for user_role_data in editor_roles:
                    user_role = user_role_data.pop("user_role")

                    editor_roles_to_create.append(
                        CustomerFormEditorRole(
                            customer_form=form, user_role=user_role, is_active=True
                        )
                    )

                if editor_roles_to_create:
                    CustomerFormEditorRole.objects.bulk_create(editor_roles_to_create)

                # Fields
                for field_data in fields_data:
                    select_options = field_data.pop("select_options", [])
                    mapped_type = self._map_field_type(field_data.get("type"))

                    field = CustomFormField.objects.create(
                        form=form,
                        label=field_data.get("label"),
                        type=mapped_type,
                        placeholder=field_data.get("placeholder"),
                        name=field_data.get("name"),
                        required=field_data.get("required", False),
                        position=field_data.get("position"),
                        is_active=True,
                    )

                    options_to_create = [
                        FieldSelectOption(
                            field=field,
                            text_label=opt["text_label"],
                            value=opt["value"],
                            position=opt.get("position"),
                            is_active=True,
                        )
                        for opt in select_options
                    ]
                    if options_to_create:
                        FieldSelectOption.objects.bulk_create(options_to_create)


class FieldOutputSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()

    class Meta:
        model = CustomFormField
        fields = [
            "label",
            "type",
            "placeholder",
            "name",
            "required",
            "position",
        ]

    def get_type(self, obj: CustomFormField):
        raw_value = obj.type
        try:
            # If stored as int or numeric string
            numeric = int(raw_value)
            for member in FieldType:
                if member.value == numeric:
                    return member.name.lower()
        except (TypeError, ValueError):
            # If stored as string label or name
            if isinstance(raw_value, str):
                return raw_value.strip().lower()
        return str(raw_value).lower() if raw_value is not None else None


class FormOutputSerializer(serializers.ModelSerializer):
    fields = FieldOutputSerializer(many=True, source="fields")

    class Meta:
        model = CustomForm
        fields = [
            "name",
            "description",
            "fields",
        ]


class SectionOutputSerializer(serializers.ModelSerializer):
    forms = FormOutputSerializer(many=True, source="forms")

    class Meta:
        model = Section
        fields = [
            "name",
            "description",
            "position",
            "forms",
        ]



# class FormSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Form
#         fields = ["id", "slug", "name", "description"]


# class SectionSerializer(serializers.ModelSerializer):
#     forms = FormSerializer(many=True, read_only=True)

#     class Meta:
#         model = Section
#         fields = ["id", "slug", "name", "description", "position", "forms"]


class SubmissionDetailSerializer(serializers.ModelSerializer):
    module_level = serializers.SlugRelatedField(slug_field="slug", read_only=True)
    module_level_name = serializers.CharField(source="module_level.name", read_only=True)
    module_slug = serializers.CharField(source="module_level.module.slug", read_only=True)
    module_name = serializers.CharField(source="module_level.module.name", read_only=True)
    # sections = SectionSerializer(many=True, read_only=True)
    sections = serializers.SerializerMethodField()

    def get_sections(self, obj):
        active_sections = obj.sections.filter(is_active=True)
        return SectionSerializer(active_sections, many=True).data

    class Meta:
        model = FormWorkflow
        fields = [
            "slug",
            "name",
            "category",
            "description",
            "module_level",
            "module_level_name",
            "module_slug",
            "module_name",
            "version",
            "sections",
        ]

 
class FormDataCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormData
        fields = ['form_field', 'locality_project', 'value']


class ListFormDataSerializer(serializers.ModelSerializer):
    field_id = serializers.IntegerField(source="form_field.id")
    form_slug = serializers.CharField(source="form_field.form.slug")
    type = serializers.CharField(source="form_field.type")

    class Meta:
        model = FormData
        fields = [
            "slug",
            "field_id",
            "form_slug",
            "value",
            "type",
            "is_approved",
        ]


class FormWorkflowUpdateSerializer(serializers.ModelSerializer):
    module_level = serializers.SlugRelatedField(
        slug_field="slug", queryset=ModuleLevel.objects.all()
    )
    sections = SectionInputSerializer(many=True)
    slug = serializers.CharField(read_only=True)

    class Meta:
        model = FormWorkflow
        fields = [
            "slug",
            "name",
            "category",
            "description",
            "module_level",
            "version",
            "sections",
        ]

    def _map_field_type(self, type_value: str):
        if type_value is None:
            return None
        try:
            return int(type_value)
        except (TypeError, ValueError):
            pass
        upper_name = str(type_value).strip().upper()
        if upper_name in FieldType.__members__:
            return FieldType[upper_name].value
        label_map = {label.upper(): value for value, label in FieldType.choices}
        if upper_name in label_map:
            return label_map[upper_name]
        raise ValidationError({"type": f"Invalid field type '{type_value}'"})

    @transaction.atomic
    def update(self, instance, validated_data):
        sections_data = validated_data.pop("sections", [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        self._update_sections(instance, sections_data)
        return instance

    def _update_sections(self, workflow, sections_data):
        for section_data in sections_data:
            slug = section_data.get("slug")
            is_active = section_data.get("is_active")
            forms_data = section_data.pop("forms", [])
            approval_roles_data = section_data.pop("approval_roles", [])

            # Update or create section
            if slug:
                section = Section.objects.filter(form_workflow=workflow, slug=slug).first()
                if section:

                    if is_active == "0":
                        section.is_active = False
                    else:
                        for attr, value in section_data.items():
                            setattr(section, attr, value)
                        
                    section.save()
                else:
                    section = Section.objects.create(form_workflow=workflow, **section_data)
            else:
                section = Section.objects.create(form_workflow=workflow, **section_data)

            # Update approval roles
            if approval_roles_data:
                SectionApprovalRole.objects.filter(section=section).delete()
                SectionApprovalRole.objects.bulk_create([
                    SectionApprovalRole(section=section, user_role=role["user_role"], is_active=True)
                    for role in approval_roles_data
                ])

            # Update forms
            for form_data in forms_data:
                slug = form_data.get("slug")
                fields_data = form_data.pop("form_fields", [])
                editor_roles_data = form_data.pop("editor_roles", [])

                raw_is_active = form_data.pop("is_active", "1")
                is_active = str(raw_is_active) in ["1", "true", "True"]

                if slug:
                    form = CustomForm.objects.filter(section=section, slug=slug).first()
                    if form:
                        for attr, value in form_data.items():
                            setattr(form, attr, value)
                        form.is_active = is_active
                        form.save()
                    else:
                        form = CustomForm.objects.create(section=section, **form_data)
                else:
                    form = CustomForm.objects.create(section=section, **form_data)

                # Update editor roles
                if editor_roles_data:
                    CustomerFormEditorRole.objects.filter(customer_form=form).delete()
                    CustomerFormEditorRole.objects.bulk_create([
                        CustomerFormEditorRole(customer_form=form, user_role=role["user_role"], is_active=True)
                        for role in editor_roles_data
                    ])

                # Update fields
                for field_data in fields_data:

                    field_id = field_data.get("id")
                    is_active = field_data.get("is_active")
                    select_options_data = field_data.pop("select_options", [])
                    mapped_type = self._map_field_type(field_data.pop("type", None))
                    
                    raw_is_active = field_data.pop("is_active", "1")
                    is_active = str(raw_is_active) in ["1", "true", "True"]

                    if field_id:
                        field = CustomFormField.objects.filter(id=field_id, form=form).first()
                        if field:
                            for attr in ["label", "placeholder", "name", "required", "position"]:
                                if attr in field_data:
                                    setattr(field, attr, field_data[attr])
                            field.type = mapped_type
                            field.is_active = is_active
                            field.save()
                        else:
                            field = CustomFormField.objects.create(
                                form=form,
                                type=mapped_type,
                                is_active=True,
                                **field_data
                            )
                    else:
                        field = CustomFormField.objects.create(
                            form=form,
                            type=mapped_type,
                            is_active=True,
                            **field_data
                        )

                    # Update select options
                    if select_options_data:
                        FieldSelectOption.objects.filter(field=field).delete()
                        FieldSelectOption.objects.bulk_create([
                            FieldSelectOption(
                                field=field,
                                text_label=opt["text_label"],
                                value=opt["value"],
                                position=opt.get("position"),
                                is_active=True
                            )
                            for opt in select_options_data
                        ])
