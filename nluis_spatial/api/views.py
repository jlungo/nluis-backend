import json
import traceback

from django.core.serializers import serialize
from django.db.models import Sum
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import status
from nluis_localities.models import Locality
from nluis_ccro.models import *
from nluis_projects.models import *
from nluis_spatial.models import SpatialUnit
from nluis_spatial.api.serializers import SpatialListSerializer
from nluis_setups.models import LandUse, PartyRole
from nluis_spatial.api.serializers import PartiesListSerialzers
from libs.fxs import val_none_str, str_to_list, register_parcel
from django.db import transaction


class LocalityGeometryView(APIView):
    def get(self, request, **kwargs):
        level_id = kwargs['level_id']
        geojson = serialize(
            'geojson', Locality.objects.filter(level_id=level_id))
        return Response({'geojson': geojson})


class ParcelGeometryView(APIView):

    def get(self, request, **kwargs):
        geojson = serialize('geojson', Parcel.objects.filter(id=kwargs['pk']))
        return Response(json.loads(geojson))


class ProjectGeometryView(APIView):

    def get(self, request, **kwargs):
        project_id = kwargs['id']
        geojson = serialize('geojson', Project.objects.filter(id=project_id))
        return Response({'geojson': geojson})


class ProjectLandUseView(APIView):
    permission_classes = [AllowAny]
    #permission_classes = [IsAuthenticated]
    def get(self, request, **kwargs):
        http_status = status.HTTP_200_OK
        message = 'success'
        list = []

        try:
            project_type = ProjectType.objects.get(code='VLUS')

            spacial_units = SpatialUnit.objects.values('locality__parent__name', 'locality__name',
                                                       'land_use__name').filter(
                project__project_type=project_type).annotate(sqm_area=Sum('sqm')).order_by()

            if 'locality_id' in request.GET and request.GET['locality_id'] is not None:
                _locality_id = request.GET['locality_id']
                locality = Locality.objects.get(id=_locality_id)
                spacial_units = spacial_units.filter(
                    locality__in=locality.getChildrenIds())

            if 'land_use_id' in request.GET and request.GET['land_use_id'] is not None:
                _land_use_id = request.GET['land_use_id']
                _land_use = LandUse.objects.get(id=_land_use_id)
                spacial_units = spacial_units.filter(land_use=_land_use)

            for landUse in spacial_units:
                list.append({
                    'use': landUse['land_use__name'],
                    'area': landUse['sqm_area'],
                    'village': landUse['locality__name'],
                    'district': landUse['locality__parent__name'],
                })

        except Exception as e:
            message = str(e)
            http_status = status.HTTP_400_BAD_REQUEST

        return Response({
            'message': message,
            'results': list
        }, status=http_status)


class PartiesListView(generics.ListAPIView):
    def get(self, request, **kwargs):
        results = []
        http_status = status.HTTP_200_OK
        message = ''
        project_id = kwargs['project_id']
        try:
            for party in Party.objects.all():
                try:
                    pic_id = party.id_pic.url
                except Exception as e:
                    pic_id = ''

                try:
                    picture = party.picture.url
                except Exception as e:
                    picture = ''

                plots = []
                for allocation in Allocation.objects.filter(party=party, parcel__project_id=project_id):
                    plots.append(allocation.parcel.claim_no)
                results.append({
                    'id': party.id,
                    'first_name': party.first_name.replace("--", "'"),
                    'middle_name': party.middle_name.replace("--", "'"),
                    'last_name': party.last_name.replace("--", "'"),
                    'fullname': party.first_name.replace("--", "'") + ' ' + party.middle_name.replace("--", "'") + ' '
                                + party.last_name.replace("--", "'"),
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
                    'occupation': party.occupation,
                    'plots': plots
                })
        except Exception as e:
            message = str(e)
            http_status = status.HTTP_400_BAD_REQUEST

        return Response({
            'message': message,
            'results': results
        }, status=http_status)


class CreatePartyView(APIView):
    def post(self, request):
        status = 0
        message = ''
        try:
            extra = json.loads(request.data['extra'])
            firstname = val_none_str(extra['first_name'])
            middlename = val_none_str(extra['middle_name'])
            lastname = val_none_str(extra['last_name'])
            gender = val_none_str(extra['gender'])

            dob = val_none_str(extra['dob'])
            makazi = val_none_str(extra['makazi'])
            try:
                idType = val_none_str(extra['idType'])
            except Exception as e:
                idType = None
            try:
                idNo = val_none_str(extra['idNo'])
            except Exception as e:
                idNo = None

            role = val_none_str(extra['role'])
            acquire = val_none_str(extra['acquire'])
            marital = val_none_str(extra['marital'])
            phone = val_none_str(extra['phone'])
            try:
                email = val_none_str(extra['email'])
            except Exception as e:
                email = None
            try:
                address = val_none_str(extra['address'])
            except Exception as e:
                address = None

            try:
                occupation = val_none_str(extra['occupation'])
            except Exception as e:
                occupation = None

            try:
                disability = val_none_str(extra['disability'])
            except Exception as e:
                disability = None

            party = Party(
                first_name=firstname,
                middle_name=middlename,
                last_name=lastname,
                gender=gender,
                phone=phone,
                email=email,
                address=address,
                occupation=occupation,
                dob=dob,
                citizen=makazi,
                id_type=idType,
                id_no=idNo,
                role=PartyRole.objects.first() if role == 'Owner' else PartyRole.objects.last(),
                acquire=acquire,
                marital=marital,
                disability=disability
            )
            party.save()

            print(party)
        except Exception as e:
            print(e)
            traceback.print_exc()
            message = str(e)

        return Response({
            'status': status,
            'message': message
        })


class AllocatePartyView(APIView):

    # @transaction.atomic
    def post(self, request):
        status = 0
        message = ''
        try:
            print(request.data)
            for p in str_to_list(request.data['parties']):
                party = Party.objects.get(id=p)
                for d in str_to_list(request.data['deedplan']):
                    parcel = Parcel.objects.get(id=d)
                    allocate = Allocation(
                        party=party,
                        parcel=parcel
                    )
                    parcel.status = 'occupied'
                    parcel.save(update_fields=['status'])
                    allocate.save()

                    parcel = register_parcel(parcel)
                    if parcel.uka_namba is None:
                        transaction.set_rollback(True)
                        message = 'Bad Locality Setup Information'
                        remark = Remark(action='approved', description=message)
                        remark.save()
                        return Response({
                            'message': message,
                        }, status=http_status)

                    parcel.save()

                    from libs.docs.ccro import generate_ccro
                    from libs.docs.trans_sheet import generate_transaction

                    generate_transaction.delay(parcel.id)
                    # generate_adjudication.delay(parcel.id)
                    generate_ccro.delay(parcel.id)

                    save_history(parcel.project_id, 'Registration', f'{parcel.id} was registered', 17,
                                 'ccro_registered_data')
        except Exception as e:
            message = str(e)
            print(e)
        return Response({
            'status': status,
            'message': message
        })


class ProjectPlotListView(APIView):
    def get(self, request, **kwargs):
        results = []
        project = Project.objects.get(id=kwargs['project_id'])

        parcelId = kwargs['parcel']
        status = kwargs['status']

        if parcelId > 0:
            qs = Parcel.objects.filter(project=project, id=deedplanId)
        else:
            qs = Parcel.objects.filter(project=project)

        if status == 'vacant':
            qs = qs.exclude(id__in=Allocation.objects.values_list('parcel__id'))
        else:
            qs = qs.filter(status=status)

        for d in qs:
            d.status = status
            d.save(update_fields=['status'])
            results.append({
                'id': d.id,
                'claim_no': d.claim_no,
                'status': d.status,
                'use': d.use(),
                'parties': d.status if d.status == 'vacant' else d.parties(),
                'occupancy': d.status if d.status == 'vacant' else d.occupancy(),
                'area': d.area()

            })

        return Response({
            'results': results
        })


class UpdatePartyPictureView(APIView):
    def post(self, request):
        status = 0
        message = ''
        try:
            extra = json.loads(request.data['extra'])
            party_id = val_none_str(extra['party_id'])

            party = Party.objects.get(id=party_id)
            party.picture = request.data['picture']
            party.save()

            print(party)
        except Exception as e:
            print(e)
            traceback.print_exc()
            message = str(e)

        return Response({
            'status': status,
            'message': message
        })
