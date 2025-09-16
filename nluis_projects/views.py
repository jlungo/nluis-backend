# Create your views here.
import base64
import json
import traceback
from datetime import datetime

from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from libs.fxs import save_history
from libs.shp.ushp import verify_plot, read_shp
from nluis_authorization.api.service import createUser
from nluis_authorization.models import AppUser
from nluis_collect.models import FormAnswer
from nluis_localities.models import Locality
from nluis_projects.api.serializers import ProjectListSerializer, MonitoringListSerializer
from nluis_projects.api.serializers import (
    TeamMemberSerializer,
    DocumentSerializer,
    ParcelSerializer
)
from nluis_projects.api.utils import (
    get_user_level,
    get_user_level_ids,
    get_user_levels,
    get_user_station_ids
)
from nluis_projects.models import (
    Project,
    ProjectType,
    ProjectStatus,
    ProjectHistory,
    Task,
    TeamMember,
    Document,
    ProjectSignatory,
    Parcel, Party, Allocation, ProjectLayer, GroupTask
)
from nluis_setups.models import Funder, DocumentType, Designation, LocalityDocumentCounter, MapType, LandUse, \
    OccupancyType
from nluis_spatial.models import Beacon


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

    def get_queryset(self):
        projects = Project.objects.filter(station_id__in=get_user_station_ids(self),
                                          is_monitoring=False).order_by('-id')
        if 'locality_id' in self.request.GET:
            locality_id = self.request.GET['locality_id']
            locality = Locality.objects.get(id=locality_id)
            projects = projects.prefetch_related('localites').filter(
                localites__in=locality.getChildrenIds())

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
        try:
            project_id = kwargs['pk']
            project = Project.objects.get(id=project_id)
            answers = []

            results = {
                'type': project.project_type.name,
                'name': project.name,
                'description': project.description,
                'funders': project.funders.values('id', 'name', 'category'),
                'budget': project.budget,
                'reg_date': project.reg_date,
                'auth_date': project.auth_date,
                'auth_by': project.auth_by.username if project.auth_by is not None else '',
                'action': project.action,
                'status': project.status.name if project.status is not None else '',
                'remarks': project.remarks,
                'localities': project.localites.all().values('id', 'name'),
                'answers': answers
            }

        except Exception as e:
            message = str(e)
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
        appuser = AppUser.objects.get(user=request.user)

        try:
            locality_ids = request.data['locality_ids']
            funder_ids = request.data['funder_ids']
            name = request.data['name']
            description = request.data['description']
            budget = request.data['budget']
            project = request.data['project']
            reg_date = request.data['reg_date']

            if project == 'existing':
                proj_plan = Project(
                    name=name,
                    description=description,
                    project_type=ProjectType.objects.get(
                        id=request.data['project_type']),
                    station=appuser.station,
                    budget=budget,
                    registered_as=project,
                    reg_date=reg_date,

                )
            elif 'project_id' in request.data:
                project_info = request.data['project_id']
                proj_plan = Project(
                    name=name,
                    description=description,
                    project_type=ProjectType.objects.get(is_monitoring=True),
                    station=appuser.station,
                    budget=budget,
                    registered_as=project,
                    reg_date=reg_date,
                    project_info=Project.objects.get(id=project_info),
                    is_monitoring=True
                )
            else:
                proj_plan = Project(
                    name=name,
                    description=description,
                    project_type=ProjectType.objects.get(
                        id=request.data['project_type']),
                    station=appuser.station,
                    budget=budget,
                    registered_as=project,
                    reg_date=reg_date,
                )

            proj_plan.status = ProjectStatus.objects.get(
                code__iexact='registered')
            proj_plan.save()

            ref_id = proj_plan.id

            for id in locality_ids:
                proj_plan.localites.add(Locality.objects.get(id=id))

            for id in funder_ids:
                proj_plan.funders.add(Funder.objects.get(id=id))

            task = Task.objects.filter(
                project_type=proj_plan.project_type).order_by('order_number').first()
            screen = task.screen.all().order_by('order_number').first()

            save_history(proj_plan.id, 'Create',
                         f'{proj_plan.id} was created', task.id, screen.code)
            message = 'Project Created'

        except Exception as e:
            message = str(e)
            http_status = status.HTTP_400_BAD_REQUEST
            transaction.set_rollback(True)

        return Response({
            'message': message,
            'ref_id': ref_id
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
                team_position=request.data['team_position']
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

            member = TeamMember(
                project=Project.objects.get(id=project_id),
                user=user,
                locality=Locality.objects.get(id=request.data['locality_id']),
                professional=request.data['professional'],
                team_position=request.data['team_position']
            )

            member.save()

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


class CreateDocumentView(APIView):
    @transaction.atomic
    def post(self, request):
        try:
            task_id = request.data['task_id']
            document_type_id = request.data['document_type_id']
            project = Project.objects.get(id=request.data['project_id'])
            locality = Locality.objects.get(id=request.data['locality_id'])
            document_type = DocumentType.objects.get(id=document_type_id)
            description = request.data['description']

            document = Document(
                project=project,
                locality=locality,
                document_type=document_type,
                description=description,
                file=request.data['file'],
                task=Task.objects.get(id=task_id)
            )
            document.save()

            data_type = str(document.document_type.acceptable_format).lower()

            print(document_type.code)

            if data_type == '.shp':
                for c in read_shp(document.file.path):

                    if document_type.code == 'deed_plan':
                        use = LandUse.objects.get(code=c.get('LUS'))
                        parcel = Parcel(claim_no=str(c.get('PLOTNUMBER')).split('.0')[0], project=project,
                                        locality=locality, geom=c.geom.geojson, hamlet_id=int(
                                            c.get('HAMLET')),
                                        occupancy_type=OccupancyType.objects.first(),
                                        current_use=use, proposed_use=use)
                        parcel.save()
                    if document_type.code == 'beacons':
                        beacon = Beacon(project=project,
                                        geom=c.geom.geojson, name=c.get('BC1'))
                        beacon.save()

                    if document_type.code == 'luse' or document_type.code == 'vboundary' or \
                            document_type.code == 'hboundary':
                        layer = ProjectLayer(
                            locality=locality,
                            project=project,
                            map_type=MapType.objects.get(
                                description=document_type.code),
                            label=locality.name,
                            description=description,
                            geom=c.geom.geojson,
                            srid=4326
                        )
                        layer.save()

                # print(verify_plot(document.file.path, document.id))

            save_history(request.data['project_id'], 'Create', f'{document.id} was created', task_id,
                         request.data['screen_code'])
            return Response({'message': 'Created Successfully'}, status=status.HTTP_200_OK)

        except Exception as e:
            traceback.print_exc()
            message = str(e)
            transaction.set_rollback(True)

        return Response({
            'message': message
        }, status=status.HTTP_400_BAD_REQUEST)


class ProjectTaskMenuView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, **kwargs):
        http_status = status.HTTP_200_OK
        message = ''
        results = []

        project_type_id = kwargs['project_type_id']
        project_id = kwargs['project_id']
        user = request.user

        try:
            for task_group in GroupTask.objects.filter(group__in=user.groups.all()):
                for t in task_group.task.all().filter(
                    project_type__id__in=[project_type_id]
                ).order_by('order_number'):
                    screens = []
                    for s in t.screen.all().order_by('order_number'):
                        task_status = ProjectHistory.objects.filter(project_id=project_id, task=t,
                                                                    screen_code=s.code).count() > 0
                        screens.append({
                            'name': s.name,
                            'code': s.code,
                            'status': task_status
                        })
                    results.append({
                        'id': t.id,
                        'name': t.name,
                        'screens': screens
                    })

        except Exception as e:
            message = str(e)
            http_status = status.HTTP_400_BAD_REQUEST
        return Response({
            # 'results': '',
            'message': 'message'
        }, status=http_status)


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
                base_64 = str(base64.b64encode(
                    d.file.read())).replace('b\'', '')
                base_64 = base_64.replace('\'', '')

                attached_documents.append({
                    'id': d.id,
                    'name': f'{d.document_type.name} - {d.locality.name}',
                    'description': d.description,
                    'path': f'data:application/pdf;base64,{base_64}'
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


class ParcelListView(generics.ListAPIView):
    serializer_class = ParcelSerializer

    def get_queryset(self):
        return Parcel.objects.filter(
            stage=self.kwargs['stage'],
            project_id=self.kwargs['project_id'])


class ParcelPartiesInfoView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, **kwargs):
        results = []
        http_status = status.HTTP_200_OK
        message = ''
        try:
            parcel = Parcel.objects.get(id=kwargs['pk'])
            for a in Allocation.objects.filter(parcel=parcel):
                party = a.party
                try:
                    pic_id = party.id_pic.url
                except Exception as e:
                    pic_id = ''

                try:
                    picture = party.picture.url
                except Exception as e:
                    picture = ''
                results.append({
                    'id': party.id,
                    'first_name': party.first_name.replace("--", "'"),
                    'middle_name': party.middle_name.replace("--", "'"),
                    'last_name': party.last_name.replace("--", "'"),
                    'gender': party.gender,
                    'dob': party.dob,
                    'picture': picture,
                    'citizenship_status': party.citizen,
                    'id_type': party.id_type,
                    'id_no': party.id_no,
                    'id_picture': pic_id,
                    'role_name': party.role.name if party.role is not None else '',
                    'acquire': party.acquire,
                    'marital_status': party.marital,
                    'disability': party.disability,
                    'phone': party.phone,
                    'email': party.email,
                    'address': party.address,
                    'occupation': party.occupation
                })
        except Exception as e:
            message = str(e)
            http_status = status.HTTP_400_BAD_REQUEST

        return Response({
            'message': message,
            'results': results
        }, status=http_status)


class ParcelInfoView(APIView):
    def get(self, request, **kwargs):
        results = {}
        http_status = status.HTTP_200_OK
        message = ''
        try:
            # parcel = Parcel.objects.select_related(
            #     'occupancy_type', 'deed_plan').get(id=kwargs['pk'])
            parcel = Parcel.objects.get(id=kwargs['pk'])
            results = {
                'claim_no': parcel.claim_no,
                'claim_date': parcel.claim_date,
                # 'deed_plan': {'name': parcel.deed_plan.name, 'srid': parcel.deed_plan.srid,
                #               'description': parcel.deed_plan.description} if parcel.deed_plan is not None else {},
                'use': parcel.use(),
                'vac_1': parcel.vac_1,
                'vac_2': parcel.vac_2,
                'topology': parcel.topology,
                'north': parcel.north,
                'south': parcel.south,
                'east': parcel.east,
                'west': parcel.west,
                'status': parcel.status,
                'stage': parcel.stage,
                'uka_namba': parcel.uka_namba,
                'registration_no': parcel.registration_no,
                'locality': parcel.locality.name,
                'hamlet': parcel.hamlet.name,
                'occupancy_type': parcel.occupancy()
            }

        except Exception as e:
            message = str(e)
            http_status = status.HTTP_400_BAD_REQUEST

        return Response({
            'message': message,
            'results': results
        }, status=http_status)
