# Create your views here.
import base64
import json
import traceback
from datetime import datetime
from nluis.pagination import StandardResultsSetLimitOffset
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from nluis_form_management.models import ModuleLevel
from libs.fxs import save_history
from nluis_authorization.api.service import createUser
from nluis_authorization.models import AppUser
from nluis_localities.models import Locality
from nluis_projects.api.serializers import ProjectListSerializer, MonitoringListSerializer
from nluis_projects.api.serializers import *
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from nluis_form_management.models import CustomForm, CustomFormField, FormData
from nluis_projects.api.utils import (
    get_user_level,
    get_user_levels,
    get_user_station_ids
)
from nluis_projects.models import *
from nluis_ccro.models import *
from nluis_setups.models import Funder, DocumentType, Designation, LocalityDocumentCounter


class ProjectTypeListView(APIView):

    def get(self, request):
        return Response({
            'results': get_user_levels(self)
        })


class ProjectTypePublicListView(APIView):

    def get(self, request):
        results = []

        for type in ProjectType.objects.filter(public_view=True, is_monitoring=False):
            results.append({
                'id': type.id,
                'name': type.name,
                'level_id': type.level_id
            })
        return Response({
            'results': results
        })


class ProjectListView(generics.ListAPIView):
    serializer_class = ProjectListSerializer
    pagination_class = StandardResultsSetLimitOffset

    def get_queryset(self):
        organization = self.request.query_params.get("organization", "")
        module_level = self.request.query_params.get("module_level", "")
        search = self.request.query_params.get("search", "")
        project_status = self.request.query_params.get("project_status", "")
        approval_status = self.request.query_params.get("approval_status", "")

        projects = Project.objects.filter(is_active=True).order_by('-id')

        if organization:
            projects = projects.filter(organization_id=organization)

        if module_level:
            projects = projects.filter(module_level__slug=module_level)

        if search:
            projects = projects.filter(name__icontains=search)

        if project_status:
            projects = projects.filter(project_status=project_status)

        if approval_status:
            projects = projects.filter(approval_status=approval_status)

        return projects


class PublishedProjectListView(generics.ListAPIView):
    serializer_class = ProjectListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        projects = Project.objects.select_related('project_type').filter(project_type__public_view=True,
                                                                         station_id__in=get_user_station_ids(
                                                                             self),
                                                                         is_monitoring=False,
                                                                         published_date__isnull=False).order_by('-id')
        if 'locality_id' in self.request.GET:
            locality_id = self.request.GET['locality_id']
            locality = Locality.objects.get(id=locality_id)
            projects = projects.prefetch_related('localites').filter(
                localites__in=locality.getChildrenIds())

        return projects


class MonitoringProjectView(generics.ListAPIView):
    serializer_class = MonitoringListSerializer

    def get_queryset(self):
        projects = Project.objects.filter(station_id__in=get_user_station_ids(self),
                                          is_monitoring=True).order_by('-created_date')
        return projects


class ProjectInfoView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, **kwargs):
        results = {}
        http_status = status.HTTP_200_OK
        message = ''

        project_id = kwargs['pk']
        project = Project.objects.get(id=project_id)
        
        try:
            project_id = kwargs['pk']
            project = Project.objects.get(id=project_id)
            answers = []

            localities_with_progress = []

            workflow = project.module_level.workflows.filter(is_active=True).first()

            sections = workflow.sections.filter(is_active=True).order_by('position')
            
            form_fields = CustomFormField.objects.filter(is_active=True, form__section__in=sections)

            total_fields = form_fields.count()

            for locality_project in project.localities.all():

                filled_fields = FormData.objects.filter(locality_project=locality_project, form_field__in=form_fields).distinct().count()
                
                progress = (filled_fields / total_fields * 100) if total_fields > 0 else 0

                localities_with_progress.append(
                    {
                        "id": locality_project.id,
                        "locality__id": locality_project.locality_id,
                        "locality__name": locality_project.locality.name,
                        "locality__level": locality_project.locality.level_id,
                        "approval_status": locality_project.approval_status,
                        "remarks": locality_project.remarks,
                        "progress": round(progress, 2),
                    }
                )

            results = {
                'id': project.id,
                'type': project.project_type.name if project.project_type is not None else None,
                'organization': project.organization.name if project.organization is not None else None,
                'reference_number': project.reference_number,
                'name': project.name,
                'description': project.description,
                'registration_date': project.reg_date,
                'authorization_date': project.auth_date,
                'budget': project.budget,
                'project_status': project.project_status,
                'approval_status': project.approval_status,
                'remarks': project.remarks,
                'funders': project.funders.values('id', 'name', 'category'),
                'auth_by': project.auth_by.email if project.auth_by is not None else None,
                'localities': localities_with_progress,
                'answers': answers
            }

        except Exception as e:
            message = str(e)
            print('message == ', message)
            http_status = status.HTTP_400_BAD_REQUEST
            traceback.print_exc()

        return Response({
            'message': message,
            'results': results
        }, status=http_status)


class CreateProjectView(APIView):
    @transaction.atomic
    def post(self, request):
        http_status = status.HTTP_201_CREATED
        message = ''
        ref_id = 0
        # appuser = AppUser.objects.get(user=request.user)

        try:
            organization = request.data['organization']
            reference_number = request.data.get('reference_number')
            name = request.data['name']
            description = request.data['description']
            registration_date = request.data['registration_date']
            authorization_date = request.data['authorization_date']
            currency_type = request.data.get('currency_type')
            budget = request.data.get('budget')
            module_level = request.data['module_level']
            funder_ids = request.data['funder_ids']
            locality_ids = request.data['locality_ids']
            project = request.data.get('project', None)

            if project == 'existing':
                proj_plan = Project(
                    name=name,
                    description=description,
                    project_type=ProjectType.objects.get(
                        id=request.data['project_type']),
                    # station=appuser.station,
                    budget=budget,
                    registered_as=project,
                    reg_date=registration_date,
                    auth_date=authorization_date,

                )
            elif 'project_id' in request.data:
                project_info = request.data['project_id']
                project_attached = None
                if project_info != 0:
                    project_attached = Project.objects.get(id=project_info)

                proj_plan = Project(
                    name=name,
                    description=description,
                    project_type=ProjectType.objects.get(is_monitoring=True),
                    # station=appuser.station,
                    budget=budget,
                    registered_as=project,
                    reg_date=registration_date,
                    project_info=project_attached,
                    is_monitoring=True
                )
            else:
                proj_plan = Project(
                    organization=Organization.objects.get(id=organization),
                    reference_number=reference_number,
                    name=name,
                    description=description,
                    module_level=ModuleLevel.objects.get(slug=module_level),
                    currency_type=currency_type,
                    budget=budget,
                    registered_as=project,
                    reg_date=registration_date,
                    auth_date=authorization_date,
                )
            
            proj_plan.save()

            # ref_id = proj_plan.id

            for id in locality_ids:
                locality_instance = Locality.objects.get(id=int(id))

                LocalityProject.objects.create(project=proj_plan, locality=locality_instance)

            for id in funder_ids:
                proj_plan.funders.add(Funder.objects.get(id=int(id)))

            message = 'Project Created'

        except Exception as e:
            message = str(e)
            http_status = status.HTTP_400_BAD_REQUEST

        return Response({
            'message': message,
            'ref_id': ref_id,
        }, status=http_status)


class UpdateProjectView(APIView):

    @transaction.atomic
    def put(self, request, pk):
        http_status = status.HTTP_200_OK
        message = ''
        ref_id = pk

        try:
            proj_plan = Project.objects.get(id=pk)

            if 'name' in request.data:
                proj_plan.name = request.data['name']

            if 'description' in request.data:
                proj_plan.description = request.data['description']

            if 'registration_date' in request.data:
                proj_plan.reg_date = request.data['registration_date']

            if 'authorization_date' in request.data:
                proj_plan.auth_date = request.data['authorization_date']

            if 'budget' in request.data:
                proj_plan.budget = request.data['budget']

            if 'module_level' in request.data:
                proj_plan.module_level = ModuleLevel.objects.get(slug=request.data['module_level'])

            if 'project' in request.data:
                proj_plan.registered_as = request.data['project']

            proj_plan.save()

            if 'locality_ids' in request.data:

                proj_plan.localities.update(is_active=False)

                for id in request.data['locality_ids']:
                    locality_instance = Locality.objects.get(id=int(id))
                    locality_project, created = LocalityProject.objects.get_or_create(
                        project=proj_plan,
                        locality=locality_instance,
                        defaults={'is_active': True}
                    )
                    if not created:

                        locality_project.is_active = True
                        locality_project.save()

            if 'funder_ids' in request.data:
                proj_plan.funders.clear()
                for id in request.data['funder_ids']:
                    proj_plan.funders.add(Funder.objects.get(id=int(id)))

            message = 'Project Updated'

        except Project.DoesNotExist:
            message = 'Project not found'
            http_status = status.HTTP_404_NOT_FOUND

        except Exception as e:
            message = str(e)
            http_status = status.HTTP_400_BAD_REQUEST

        return Response({
            'message': message,
            'ref_id': ref_id,
        }, status=http_status)
    

class DeleteProjectView(APIView):

    @transaction.atomic
    def delete(self, request, pk):
        http_status = status.HTTP_200_OK
        message = ''

        try:
            proj_plan = Project.objects.get(id=pk)
            proj_plan.is_active = False
            proj_plan.save()
            message = "Project deactivated successfully"
            
        except Project.DoesNotExist:
            message = "Project not found"
            http_status = status.HTTP_404_NOT_FOUND

        except Exception as e:
            message = str(e)
            http_status = status.HTTP_400_BAD_REQUEST

        return Response({
            "message": message,
            "ref_id": pk,
        }, status=http_status)



class AproveProjectView(APIView):
    @transaction.atomic
    def post(self, request, **kwargs):
        http_status = status.HTTP_201_CREATED
        message = ''
        ref_id = 0

        try:
            project = Project.objects.get(id=kwargs['pk'])
            if project:
                project_status = ProjectStatus.objects.get(
                    code=request.data['status_code'])
                if project_status.code == 'approved':

                    # for authorized date
                    if not project.auth_date:
                        project.auth_date = datetime.now()
                    project.auth_by = request.user
                    project.status = project_status
                    project.action = project_status.code
                    project.save()

                if project_status.code == 'completed':
                    project.status = project_status
                    project.action = project_status.code
                    project.published_date = request.data['published_date']
                    project.save()
                else:
                    project.status = project_status
                    project.action = project_status.code
                    if 'remarks' in request.data:
                        project.remarks = request.data['remarks']
                    project.save()

                message = 'Succesfully'
                ref_id = project.id

                save_history(ref_id, project_status.code, project_status.code, request.data['task_id'],
                             request.data['screen_code'])
        except Exception as e:
            message = str(e)
            http_status = status.HTTP_400_BAD_REQUEST
            transaction.set_rollback(True)

        return Response({
            'message': message,
            'ref_id': ref_id
        }, status=http_status)


class ProjectStatsView(APIView):

    def get(self, request):
        results = {}
        funders = []
        projectsToExpire = []
        http_status = status.HTTP_200_OK
        message = ''
        try:

            if 'project_type_id' in request.GET:
                project_type_id = request.GET['project_type_id']
                project_type = ProjectType.objects.select_related(
                    'level').get(id=project_type_id)
            else:
                selected_level_id = get_user_level(self)
                project_type = ProjectType.objects.select_related(
                    'level').get(level_id=selected_level_id)

            projects = Project.objects.select_related(
                'project_type').filter(project_type_id=project_type.id)

            _projects = {
                'total': projects.count(),
                'approved': projects.filter(status__code='approved').count(),
                'rejected': projects.filter(status__code='rejected').count(),
                'submitted': projects.filter(status__code='submitted').count(),
                'registered': projects.filter(status__code='registered').count(),
                'reviewed': projects.filter(status__code='reviewed').count(),
                'returned': projects.filter(status__code='returned').count(),
                'completed': projects.filter(status__code='completed').count(),
                'ongoing': 0,
                'active': 0,
                'expiry': 0
            }

            results = {
                'projects': _projects
            }

            for funder in Funder.objects.all():
                funders.append({
                    'funder': funder.name,
                    'projects': projects.filter(funders__id=funder.id).count()
                })

            for pro in projects:

                if pro.published_date != None and pro.project_type.duration_alert != None and (
                        pro.project_type.duration - pro.age()) == pro.project_type.duration_alert:
                    projectsToExpire.append({
                        'project': pro.name,
                        'duration': pro.project_type.duration,
                        'current_duration': pro.age()
                    })

        except Exception as e:
            message = str(e)
            traceback.print_exc()
            http_status = status.HTTP_400_BAD_REQUEST

        return Response({
            'message': message,
            'results': {'stats': results, 'funders': funders, 'toExpire': projectsToExpire}
        }, status=http_status)


class TeamMemberListView(generics.ListAPIView):
    serializer_class = TeamMemberSerializer

    def get_queryset(self):
        return TeamMember.objects.filter(project_id=self.kwargs['project_id'])


class TeamMemberHistoryListView(generics.ListAPIView):
    serializer_class = TeamMemberHistorySerializer

    def get_queryset(self):
        return TeamMemberHistory.objects.filter(project_id=self.kwargs['project_id'])


class CreateTeamMemberView(APIView):
    def post(self, request):
        message = ''
        user = User()
        try:
            # member = TeamMemberSerializer(data=request.data)
            # TeamMember.objects.filter(**request.data).exists()

            try:
                user = User.objects.get(email=request.data['email'])
            except Exception as e:
                newUser = createUser(request)

                if newUser['status']:
                    user = newUser['user']
                else:

                    user = User.objects.get(username=(request.data['first_name'] +
                                                      '.' + request.data['last_name']).lower())

            project_id = request.data['project_id']

            member = TeamMember(
                project=Project.objects.get(id=project_id),
                user=user,
                locality=Locality.objects.get(id=request.data['locality_id']),
                professional=request.data['professional'],
                team_position=request.data['team_position'],
                dodoso_categories=request.data['categories']
            )

            member.save()

            # Asign group to team member user
            _user = User.objects.get(id=user.id)
            _user.groups.add(request.data['group_id'])
            _user.save()

            save_history(project_id, 'Create', f'{member.id} was created', request.data['task_id'],
                         request.data['screen_code'])

            return Response({'message': 'Created Successfully'}, status=status.HTTP_200_OK)

        except Exception as e:
            message = str(e)
            traceback.print_exc()

        return Response({
            'message': message
        }, status=status.HTTP_400_BAD_REQUEST)


class AddTeamMemberView(APIView):
    def post(self, request):
        message = ''
        user = User()
        try:

            user = User.objects.get(id=request.data['user_id'])
            project_id = request.data['project_id']
            project = Project.objects.get(id=project_id)

            member = TeamMember.objects.get(user=user)

            if member:
                member_history = TeamMemberHistory(
                    project=member.project,
                    user=member.user,
                    locality=member.locality,
                    professional=member.professional,
                    team_position=member.team_position,
                    created_date=member.updated_date,
                    created_time=member.updated_time,
                    dodoso_categories=request.data['categories']

                )
                member_history.save()

            else:
                member = TeamMember(
                    user=user
                )
                member.save()

            member, created = TeamMember.objects.update_or_create(
                id=member.id,
                defaults={'user': member.user,
                          'device_id': member.device_id,
                          'project': project,
                          'professional': request.data['professional'],
                          'team_position': request.data['team_position'],
                          'locality': Locality.objects.get(id=request.data['locality_id']),
                          'para_surveyor_id': member.id,
                          'dodoso_categories': request.data['categories']

                          },
            )

            # Asign group to team member user
            _user = User.objects.get(id=user.id)
            _user.groups.add(request.data['group_id'])
            _user.save()

            save_history(project_id, 'Add', f'{member.id} was created', request.data['task_id'],
                         request.data['screen_code'])

            return Response({'message': 'Added Successfully'}, status=status.HTTP_200_OK)

        except Exception as e:
            message = str(e)
            # traceback.print_exc()

        return Response({
            'message': message
        }, status=status.HTTP_400_BAD_REQUEST)


class DocumentListView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DocumentSerializer
    queryset = Document.objects.all()




class ProjectDocumentsView(APIView):

    def get(self, request, **kwargs):

        requred_documents = []
        attached_documents = []

        task_id = kwargs['task_id']
        project_id = kwargs['project_id']
        project = Project.objects.get(id=project_id)
        project_type = project.project_type

        try:
            list_attached = Document.objects.filter(project_id=project_id, task_id=task_id,
                                                    locality_id__in=project.localites.values_list('id'))
            list_requred = DocumentType.objects.filter(
                task_id=task_id, is_input=True, project_type=project_type)

            requred_documents = []
            attached_documents = []

            for locality in project.localites.all():
                for d in list_requred:
                    if Document.objects.filter(locality=locality, document_type=d).count() < 1:
                        requred_documents.append({
                            'id': d.id,
                            'name': f'{d.name} - {locality.name}',
                            'locality': {
                                'name': locality.name,
                                'id': locality.id
                            },
                            'acceptable_format': d.acceptable_format
                        })

            for d in list_attached:
                try:
                    base_64 = str(base64.b64encode(
                        d.file.read())).replace('b\'', '')
                    base_64 = base_64.replace('\'', '')
                    path = f'data:application/pdf;base64,{base_64}'
                except Exception as e:
                    path = f'No File - {str(e)}'

                attached_documents.append({
                    'id': d.id,
                    'name': f'{d.document_type.name} - {d.locality.name}',
                    'description': d.description,
                    'path': path
                })

            http_status = status.HTTP_200_OK
            message = 'success'
        except Exception as e:
            message = str(e)
            http_status = status.HTTP_400_BAD_REQUEST
        return Response({
            'required_documents': requred_documents,
            'attached_documents': attached_documents,
            'message': message,
        }, status=http_status)


# Signatories


class CreateSignatoryView(APIView):
    @transaction.atomic
    def post(self, request):

        try:

            extra = json.loads(request.data['extra'])
            firstname = str(extra['firstname']).title()
            middlename = str(extra['middlename']).title()
            lastname = str(extra['lastname']).title()
            phone = extra['phone']

            project_id = int(extra['project_id'])
            locality_id = int(extra['locality_id'])
            designation_id = int(extra['designation_id'])

            task_id = int(extra['task_id'])
            screen_code = extra['screen_code']

            signatory = ProjectSignatory(
                project=Project.objects.get(id=project_id),
                locality=Locality.objects.get(id=locality_id),
                first_name=firstname,
                middle_name=middlename,
                last_name=lastname,
                signature=request.FILES.get('signature'),
                phone=phone,
                designation=Designation.objects.get(id=designation_id)
            )

            signatory.save()

            save_history(project_id, 'Create',
                         f'{signatory.id} was created', task_id, screen_code)
            return Response({'message': 'Created Successfully'}, status=status.HTTP_200_OK)

        except Exception as e:
            message = str(e)
            transaction.set_rollback(True)

        return Response({
            'message': message
        }, status=status.HTTP_400_BAD_REQUEST)


class SignatoryListView(APIView):

    def get(self, request, **kwargs):
        results = []
        required_signatories = []
        attached_signatories = []

        project = Project.objects.get(id=kwargs['project_id'])
        qs = ProjectSignatory.objects.filter(project=project)

        for s in qs:
            results.append({
                'id': s.id,
                'fullname': s.fullname(),
                'designation': s.designation.name if s.designation is not None else '',
                'locality': s.locality.name if s.locality is not None else ''
            })

        for l in project.localites.all():
            for d in qs.filter(locality=l):
                attached_signatories.append({
                    'id': d.id,
                    'design': d.designation.name,
                    'locality': l.name
                })
            for desg in Designation.objects.filter(project_type=project.project_type):
                if qs.filter(locality_id=l.id, designation=desg).count() < 1:
                    required_signatories.append({
                        'designation': {
                            'id': desg.id,
                            'name': desg.name
                        },
                        'locality': {
                            'id': l.id,
                            'name': l.name
                        }
                    })

        return Response({
            'results': results,
            'required_signatories': required_signatories,
            'attached_signatories': attached_signatories
        })


class LocalitiesListView(APIView):
    def get(self, request, **kwargs):
        project = Project.objects.get(id=kwargs['project_id'])
        required = []
        attached = []
        localities = []

        district_info = None
        for d in project.localites.all():
            if district_info is None:
                try:
                    district = d.parent.parent
                    try:
                        count = LocalityDocumentCounter.objects.get(
                            project=project, locality=district).count
                    except Exception as e:
                        count = 0

                    try:
                        meeting_date = LocalityDocumentCounter.objects.get(locality=district,
                                                                           project=project).meeting_date
                    except Exception as e:
                        meeting_date = None
                    district_info = {
                        'id': district.id,
                        'name': district.name,
                        'registration_code': district.registration_code,
                        'address': district.address,
                        'count': count,
                        'meeting_date': meeting_date,
                        'child': []
                    }
                except Exception as e:
                    district_info = {
                        'id': 0,
                        'name': 'No Parent District',
                        'registration_code': None,
                        'address': str(e),
                        'count': 0,
                        'child': []
                    }

            for c in Locality.objects.filter(parent=d):
                if c.registration_code is None:
                    required.append({
                        'id': c.id,
                        'name': f'{c.name} - {c.level.name}'
                    })

                else:
                    attached.append({
                        'id': c.id,
                        'name': f'{c.name} - {c.level.name}'
                    })

            if d.registration_code is None or d.address is None:
                required.append({
                    'id': d.id,
                    'name': f'{d.name} - {d.level.name}'
                })
                if district_info['registration_code'] is None:
                    required.append(district_info)
            else:
                attached.append({
                    'id': d.id,
                    'name': f'{d.name} - {d.level.name}'
                })

            localities.append(district_info)

            childs = []
            for c in Locality.objects.filter(parent=d):
                try:
                    count = LocalityDocumentCounter.objects.get(
                        project=project, locality=c).count
                except Exception as e:
                    count = 0

                childs.append({
                    'id': c.id,
                    'name': c.name,
                    'registration_code': c.registration_code,
                    'count': count
                })

            try:
                count = LocalityDocumentCounter.objects.get(
                    project=project, locality=d).count
            except Exception as e:
                count = 0

            try:
                meeting_date = LocalityDocumentCounter.objects.get(locality=d,
                                                                   project=project).meeting_date
            except Exception as e:
                meeting_date = None

            localities.append({
                'id': d.id,
                'name': d.name,
                'registration_code': d.registration_code,
                'count': count,
                'address': d.address,
                'child': childs,
                'meeting_date': meeting_date
            })

        return Response({
            'required_localities': required,
            'attached_localities': attached,
            'localites': localities
        })




class ProjectStatusListView(APIView):

    def get(self, request):
        results = []
        project_status = ProjectStatus.objects.all()
        for status in project_status:
            results.append({
                'id': status.id,
                'name': status.name
            })
        return Response({
            'results': results
        })


class ProjectSearchListView(generics.ListAPIView):
    serializer_class = ProjectListSerializer

    def get_queryset(self):
        project_type_id = self.kwargs['project_type_id']
        status_id = self.kwargs['status_id']
        project_name = self.kwargs['desc']
        if project_type_id > 0:
            if status_id > 0:
                if project_name is not None and project_name != 'undefined':
                    projects = Project.objects.filter(station_id__in=get_user_station_ids(self),
                                                      is_monitoring=False, project_type_id=project_type_id,
                                                      status_id=status_id, name__icontains=project_name)\
                        .order_by('-id')
                else:
                    projects = Project.objects.filter(station_id__in=get_user_station_ids(self),
                                                      is_monitoring=False, project_type_id=project_type_id,
                                                      status_id=status_id) \
                        .order_by('-id')
            else:
                if project_name is not None and project_name != 'undefined':
                    projects = Project.objects.filter(station_id__in=get_user_station_ids(self),
                                                      is_monitoring=False, project_type_id=project_type_id,
                                                      name__icontains=project_name)\
                        .order_by('-id')
                else:
                    projects = Project.objects.filter(station_id__in=get_user_station_ids(self),
                                                      is_monitoring=False, project_type_id=project_type_id) \
                        .order_by('-id')
        else:
            if status_id > 0:
                if project_name is not None and project_name != 'undefined':
                    projects = Project.objects.filter(station_id__in=get_user_station_ids(self),
                                                      is_monitoring=False,
                                                      status_id=status_id, name__icontains=project_name)\
                        .order_by('-id')
                else:
                    projects = Project.objects.filter(station_id__in=get_user_station_ids(self),
                                                      is_monitoring=False, status_id=status_id) \
                        .order_by('-id')
            else:
                if project_name is not None and project_name != 'undefined':
                    projects = Project.objects.filter(station_id__in=get_user_station_ids(self),
                                                      is_monitoring=False,
                                                      name__icontains=project_name)\
                        .order_by('-id')
                else:
                    projects = Project.objects.filter(station_id__in=get_user_station_ids(self),
                                                      is_monitoring=False) \
                        .order_by('-id')
        if 'locality_id' in self.request.GET:
            locality_id = self.request.GET['locality_id']
            locality = Locality.objects.get(id=locality_id)
            projects = projects.prefetch_related('localites').filter(
                localites__in=locality.getChildrenIds())

        return projects


class ProjectApprovalView(generics.UpdateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectApprovalSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"

    def update(self, request, *args, **kwargs):
        """
        Approve or reject a project.

        **Payload Example:**
        {
          "approval_status": 2   # 2 = Approved, 3 = Rejected
        }
        """
        return super().update(request, *args, **kwargs)
    

class LocalityProjectApprovalUpdateView(APIView):
    def post(self, request):
        results = []

        for item in request.data:
            locality_id = item.get("locality_id")
            approval_status = item.get("approval_status")
            remarks = item.get("remarks", "")

            if not locality_id or approval_status not in [choice[0] for choice in ProjectApprovalStatus.choices]:
                results.append({"id": locality_id, "status": "invalid data"})
                continue

            try:
                lp = LocalityProject.objects.get(id=locality_id)
                lp.approval_status = approval_status
                lp.remarks = remarks
                lp.save(update_fields=["approval_status", "remarks", "updated_at"])
                results.append({"id": locality_id, "status": "updated"})
            except LocalityProject.DoesNotExist:
                results.append({"id": locality_id, "status": "not found"})

        return Response({"results": results}, status=status.HTTP_200_OK)
