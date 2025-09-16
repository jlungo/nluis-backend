from nluis_form_management.models import ModuleLevel, FormWorkflow, Section, CustomForm, CustomFormField, FieldSelectOption, FormData
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from nluis.pagination import StandardResultsSetLimitOffset
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from nluis_projects.models import LocalityProject
from django.conf import settings
from django.core.files.storage import default_storage
from django.utils.crypto import get_random_string
from rest_framework.views import APIView
from django.db.models import Q
from .serializers import *
import os

class ModuleLevelListView(generics.ListAPIView):
    serializer_class = ModuleLevelSerializer
    pagination_class = StandardResultsSetLimitOffset
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        module = self.request.query_params.get("module", "")
        keyword = self.request.query_params.get("keyword", "")

        levels = ModuleLevel.objects.filter(is_active=True)

        if module:
            levels = levels.filter(module__slug=module)

        if keyword:
            levels = levels.filter(name__icontains=keyword)

        return levels


class ModuleLevelCreateView(generics.CreateAPIView):
    serializer_class = CreateModuleLevelSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = ModuleLevel.objects.all()


class ModuleLevelSoftDeleteView(generics.DestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = ModuleLevel.objects.all()

    def get_object(self):
        slug = self.kwargs.get("slug")
        return generics.get_object_or_404(ModuleLevel, slug=slug)

    def perform_destroy(self, instance):
        if instance.is_active:
            instance.is_active = False
            instance.save(update_fields=["is_active"])

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_200_OK)


class ModuleLevelUpdateView(generics.UpdateAPIView):
    serializer_class = UpdateModuleLevelSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = ModuleLevel.objects.all()

    def get_object(self):
        slug = self.kwargs.get("slug")
        return generics.get_object_or_404(ModuleLevel, slug=slug)


class FormWorkflowListView(generics.ListAPIView):
    serializer_class = FormWorkflowSerializer
    pagination_class = StandardResultsSetLimitOffset
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        module = self.request.query_params.get("module", "")
        module_level = self.request.query_params.get("module_level", "")
        category = self.request.query_params.get("category", "")
        keyword = self.request.query_params.get("keyword", "")

        workflows = FormWorkflow.objects.filter(is_active=True)

        if module:
            workflows = workflows.filter(module_level__module__slug=module)

        if module_level:
            workflows = workflows.filter(module_level__slug=module_level)

        if category:
            workflows = workflows.filter(category=category)

        if keyword:
            workflows = workflows.filter(name__icontains=keyword)

        return workflows


class FormWorkflowCreateView(generics.CreateAPIView):
    serializer_class = CreateFormWorkflowSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = FormWorkflow.objects.all()


class FormWorkflowUpdateView(generics.UpdateAPIView):
    serializer_class = UpdateFormWorkflowSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = FormWorkflow.objects.all()

    def get_object(self):
        slug = self.kwargs.get("slug")
        return generics.get_object_or_404(FormWorkflow, slug=slug)


class FormWorkflowSoftDeleteView(generics.DestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = FormWorkflow.objects.all()

    def get_object(self):
        slug = self.kwargs.get("slug")
        return generics.get_object_or_404(FormWorkflow, slug=slug)

    def perform_destroy(self, instance):
        if instance.is_active:
            instance.is_active = False
            instance.save(update_fields=["is_active"])

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_200_OK)


class SectionListView(generics.ListAPIView):
    serializer_class = SectionSerializer
    pagination_class = StandardResultsSetLimitOffset
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        module = self.request.query_params.get("module", "")
        module_level = self.request.query_params.get("module_level", "")
        workflow = self.request.query_params.get("workflow", "")
        keyword = self.request.query_params.get("keyword", "")

        sections = Section.objects.filter(is_active=True)

        if module:
            sections = sections.filter(form_workflow__module_level__module__slug=module)

        if module_level:
            sections = sections.filter(form_workflow__module_level__slug=module_level)

        if workflow:
            sections = sections.filter(form_workflow__slug=workflow)

        if keyword:
            sections = sections.filter(name__icontains=keyword)

        return sections


class SectionCreateView(generics.CreateAPIView):
    serializer_class = CreateSectionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Section.objects.all()


class SectionUpdateView(generics.UpdateAPIView):
    serializer_class = UpdateSectionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Section.objects.all()

    def get_object(self):
        slug = self.kwargs.get("slug")
        return generics.get_object_or_404(Section, slug=slug)


class SectionSoftDeleteView(generics.DestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Section.objects.all()

    def get_object(self):
        slug = self.kwargs.get("slug")
        return generics.get_object_or_404(Section, slug=slug)

    def perform_destroy(self, instance):
        if instance.is_active:
            instance.is_active = False
            instance.save(update_fields=["is_active"])

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_200_OK)


class FormListView(generics.ListAPIView):
    serializer_class = FormSerializer
    pagination_class = StandardResultsSetLimitOffset
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        module = self.request.query_params.get("module", "")
        module_level = self.request.query_params.get("module_level", "")
        workflow = self.request.query_params.get("workflow", "")
        section = self.request.query_params.get("section", "")
        keyword = self.request.query_params.get("keyword", "")

        forms = CustomForm.objects.filter(is_active=True)

        if module:
            forms = forms.filter(section__form_workflow__module_level__module__slug=module)

        if module_level:
            forms = forms.filter(section__form_workflow__module_level__slug=module_level)

        if workflow:
            forms = forms.filter(section__form_workflow__slug=workflow)

        if section:
            forms = forms.filter(section__slug=section)

        if keyword:
            forms = forms.filter(name__icontains=keyword)

        return forms


class FormCreateView(generics.CreateAPIView):
    serializer_class = CreateFormSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = CustomForm.objects.all()


class FormUpdateView(generics.UpdateAPIView):
    serializer_class = UpdateFormSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = CustomForm.objects.all()

    def get_object(self):
        slug = self.kwargs.get("slug")
        return generics.get_object_or_404(CustomForm, slug=slug)


class FormSoftDeleteView(generics.DestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = CustomForm.objects.all()

    def get_object(self):
        slug = self.kwargs.get("slug")
        return generics.get_object_or_404(CustomForm, slug=slug)

    def perform_destroy(self, instance):
        if instance.is_active:
            instance.is_active = False
            instance.save(update_fields=["is_active"])

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_200_OK)


class FormFieldListView(generics.ListAPIView):
    serializer_class = FormFieldSerializer
    pagination_class = StandardResultsSetLimitOffset
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        module = self.request.query_params.get("module", "")
        module_level = self.request.query_params.get("module_level", "")
        workflow = self.request.query_params.get("workflow", "")
        section = self.request.query_params.get("section", "")
        form = self.request.query_params.get("form", "")
        keyword = self.request.query_params.get("keyword", "")

        fields = CustomFormField.objects.filter(is_active=True)

        if module:
            fields = fields.filter(form__section__form_workflow__module_level__module__slug=module)

        if module_level:
            fields = fields.filter(form__section__form_workflow__module_level__slug=module_level)

        if workflow:
            fields = fields.filter(form__section__form_workflow__slug=workflow)

        if section:
            fields = fields.filter(form__section__slug=section)

        if form:
            fields = fields.filter(form__slug=form)

        if keyword:
            fields = fields.filter(label__icontains=keyword)

        return fields


class FormFieldCreateView(generics.CreateAPIView):
    serializer_class = CreateFormFieldSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = CustomFormField.objects.all()


class FormFieldUpdateView(generics.UpdateAPIView):
    serializer_class = UpdateFormFieldSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = CustomFormField.objects.all()

    def get_object(self):
        pk = self.kwargs.get("pk")
        return generics.get_object_or_404(CustomFormField, pk=pk)


class FormFieldSoftDeleteView(generics.DestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = CustomFormField.objects.all()

    def get_object(self):
        pk = self.kwargs.get("pk")
        return generics.get_object_or_404(CustomFormField, pk=pk)

    def perform_destroy(self, instance):
        if instance.is_active:
            instance.is_active = False
            instance.save(update_fields=["is_active"])

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_200_OK)


class FieldSelectOptionListView(generics.ListAPIView):
    serializer_class = FieldSelectOptionSerializer
    pagination_class = StandardResultsSetLimitOffset
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        module = self.request.query_params.get("module", "")
        module_level = self.request.query_params.get("module_level", "")
        workflow = self.request.query_params.get("workflow", "")
        section = self.request.query_params.get("section", "")
        form = self.request.query_params.get("form", "")
        field_id = self.request.query_params.get("field", "")
        keyword = self.request.query_params.get("keyword", "")

        options = FieldSelectOption.objects.filter(is_active=True)

        if module:
            options = options.filter(field__form__section__form_workflow__module_level__module__slug=module)

        if module_level:
            options = options.filter(field__form__section__form_workflow__module_level__slug=module_level)

        if workflow:
            options = options.filter(field__form__section__form_workflow__slug=workflow)

        if section:
            options = options.filter(field__form__section__slug=section)

        if form:
            options = options.filter(field__form__slug=form)

        if field_id:
            options = options.filter(field_id=field_id)

        if keyword:
            options = options.filter(text_label__icontains=keyword)

        return options


class FieldSelectOptionCreateView(generics.CreateAPIView):
    serializer_class = CreateFieldSelectOptionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = FieldSelectOption.objects.all()


class FieldSelectOptionUpdateView(generics.UpdateAPIView):
    serializer_class = UpdateFieldSelectOptionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = FieldSelectOption.objects.all()

    def get_object(self):
        pk = self.kwargs.get("pk")
        return generics.get_object_or_404(FieldSelectOption, pk=pk)


class FieldSelectOptionSoftDeleteView(generics.DestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = FieldSelectOption.objects.all()

    def get_object(self):
        pk = self.kwargs.get("pk")
        return generics.get_object_or_404(FieldSelectOption, pk=pk)

    def perform_destroy(self, instance):
        if instance.is_active:
            instance.is_active = False
            instance.save(update_fields=["is_active"])

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_200_OK)


class FormDataListView(generics.ListAPIView):
    serializer_class = FormDataSerializer
    pagination_class = StandardResultsSetLimitOffset
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        module = self.request.query_params.get("module", "")
        module_level = self.request.query_params.get("module_level", "")
        workflow = self.request.query_params.get("workflow", "")
        section = self.request.query_params.get("section", "")
        form = self.request.query_params.get("form", "")
        form_field_id = self.request.query_params.get("form_field", "")
        project = self.request.query_params.get("project", "")
        keyword = self.request.query_params.get("keyword", "")

        data = FormData.objects.filter(is_active=True)

        if module:
            data = data.filter(form__section__form_workflow__module_level__module__slug=module)

        if module_level:
            data = data.filter(form__section__form_workflow__module_level__slug=module_level)

        if workflow:
            data = data.filter(form__section__form_workflow__slug=workflow)

        if section:
            data = data.filter(form__section__slug=section)

        if form:
            data = data.filter(form_field__form__slug=form)

        if form_field_id:
            data = data.filter(form_field_id=form_field_id)

        if project:
            data = data.filter(project__slug=project)

        if keyword:
            data = data.filter(value__icontains=keyword)

        return data


class FormDataCreateView(generics.CreateAPIView):
    serializer_class = CreateFormDataSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = FormData.objects.all()


class FormDataUpdateView(generics.UpdateAPIView):
    serializer_class = UpdateFormDataSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = FormData.objects.all()

    def get_object(self):
        pk = self.kwargs.get("pk")
        return generics.get_object_or_404(FormData, pk=pk)


class FormDataSoftDeleteView(generics.DestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = FormData.objects.all()

    def get_object(self):
        pk = self.kwargs.get("pk")
        return generics.get_object_or_404(FormData, pk=pk)

    def perform_destroy(self, instance):
        if instance.is_active:
            instance.is_active = False
            instance.save(update_fields=["is_active"])

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_200_OK)


class SubmissionCreateView(generics.CreateAPIView):
    serializer_class = SubmissionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = FormWorkflow.objects.all()


class SubmissionRetrieveView(generics.RetrieveAPIView):
    serializer_class = SubmissionDetailSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = FormWorkflow.objects.all()

    lookup_field = "slug"


class SubmissionByModuleLevelDetailView(generics.RetrieveAPIView):
    serializer_class = SubmissionDetailSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        module_level_slug = self.kwargs.get("module_level")
        category = self.request.query_params.get("category", "")

        return (
            FormWorkflow.objects
            .filter(Q(module_level__slug=module_level_slug) | Q(category=category))
            .order_by("-created_at", "-version")
            .first()
        )


class FormDataCreateView(generics.CreateAPIView):
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = FormDataCreateSerializer

    def post(self, request, *args, **kwargs):
        data = request.data

        saved_data = []

        for key, values in data.lists():
            
            if key.startswith("data-"):
                form_field_id = key.split("-")[1]
                value = values[0]
                locality_project_id = data.get(form_field_id)

                try:
                    form_field = CustomFormField.objects.get(id=int(form_field_id))
                except (CustomFormField.DoesNotExist, ValueError):
                    raise ValidationError(
                        {"form_field": f"Form field with id {form_field_id} does not exist."}
                    )
                
                try:
                    locality_project = LocalityProject.objects.get(id=int(locality_project_id))
                except (LocalityProject.DoesNotExist, ValueError):
                    raise ValidationError(
                        {"locality_project": f"Locality project with id {locality_project_id} does not exist."}
                    )

                parsed_value = FormParse.parse(form_field.type, value, request.FILES)

                form_data = FormData.objects.create(
                    form_field=form_field,
                    locality_project=locality_project,
                    value=str(parsed_value)
                )

                saved_data.append(form_data)

        serializer = self.get_serializer(saved_data, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class FormParse:
    @staticmethod
    def parse(field_type, value, files=None):
        if field_type == "file":

            if hasattr(value, "read"):
                filename = FormParse._save_file(value)
                return default_storage.url(filename)

            if files and isinstance(value, str) and value in files:
                file_obj = files[value]
                filename = FormParse._save_file(file_obj)
                return default_storage.url(filename)

            return None

        if field_type in ["number", "decimal"]:
            try:
                return str(float(value))
            except (ValueError, TypeError):
                return None

        if field_type == "checkbox":
            if isinstance(value, list):
                return ",".join(map(str, value))
            return str(value)

        return str(value)

    @staticmethod
    def _save_file(file_obj):
        """Save uploaded file to MEDIA_ROOT/form_uploads/ and return filename."""
        
        ext = os.path.splitext(file_obj.name)[1]
        filename = f"form_uploads/{get_random_string(12)}{ext}"
        
        saved_path = default_storage.save(filename, file_obj)
        return saved_path



class FormDataListView(generics.ListAPIView):
    serializer_class = ListFormDataSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        workflow_slug = self.request.query_params.get("workflow_slug", "")
        locality_project_id = self.request.query_params.get("locality_project_id", "")

        form_data = FormData.objects.filter(is_active=True)

        if workflow_slug:
            form_data = form_data.filter(form_field__form__section__form_workflow__slug=workflow_slug)

        if locality_project_id:
            form_data = form_data.filter(locality_project=locality_project_id)

        return form_data
    

class FormDataApprovalView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        is_approved_raw = request.data.get("is_approved")
        form_data_ids = request.data.get("form_data_ids", [])

        if is_approved_raw not in ["0", "1", 0, 1, True, False]:
            return Response(
                {"detail": "Invalid 'is_approved'. Must be '1' or '0'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        is_approved = str(is_approved_raw) == "1"

        if not isinstance(form_data_ids, list):
            return Response(
                {"detail": "Invalid 'form_data_ids'. Must be a list of IDs."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        updated_count = FormData.objects.filter(id__in=form_data_ids).update(
            is_approved=is_approved
        )

        return Response(
            {
                "message": f"{updated_count} form data record(s) updated successfully.",
                "is_approved": is_approved,
                "updated_ids": form_data_ids,
            },
            status=status.HTTP_200_OK,
        )


class SubmissionUpdateView(generics.UpdateAPIView):
    serializer_class = FormWorkflowUpdateSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = FormWorkflow.objects.all()
    lookup_field = 'slug'
