import requests
import json
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.db import transaction
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings


from nluis_authorization.models import AppUser
from nluis_billing.api.serializers import (
    FeeListSerializer,
)
from nluis_projects.models import (
    ProjectType, Project
)
from nluis_billing.models import (
    Fee, Bill, BillItem
)
from nluis_setups.models import (
    ExchangeRate
)

from nluis_billing.api.xmlparser import billxml
from nluis_billing.api.ssl import ssl_sign, ssl_verity


def request_control_number(bill):

    # get xml content
    content = billxml(bill)
    # sign content
    signature = ssl_sign(
        content, settings.GEPG_PRIVATE_KEY_FILE, settings.GEPG_PRIVATE_KEY_PASS)
    # Combine signature and content signed
    payload = f'''<Gepg>{content} <gepgSignature>{signature}</gepgSignature></Gepg>'''

    # Gepg Headers definition ;
    header = [
        'Content-Type: application/xml',
        'Gepg-Com: default.sp.in',
        'Gepg-Code:'+settings.SP_CODE,
        f'Content-Length:{len(payload)}'
    ]

    url = settings.ENGINE_SERVER_IP+'/api/bill/sigqrequest'
    print(payload)
    response = requests.request("POST", url, headers=header, data=payload)

    return response


class FeeListView(generics.ListAPIView):
    serializer_class = FeeListSerializer

    def get_queryset(self):
        fees = ''

        try:
            Id = self.request.GET['project_type_id']
            _project_type = ProjectType.objects.get(id=Id)

            fees = Fee.objects.filter(
                project_type=_project_type)

        except Exception as e:
            message = str(e)

        return fees


class CreateBillView(APIView):

    def post(self, request):
        http_status = status.HTTP_201_CREATED
        message = ''
        appuser = AppUser.objects.get(user=request.user)
        exchange_rate = ExchangeRate.objects.get(is_active=True)
        _issued_date = timezone.now()
        _expiry_date = (timezone.now() + timedelta(14))
        items = request.data['items']

        try:

            holder = appuser.user.first_name+' '+appuser.user.last_name
            phone = appuser.phone
            with transaction.atomic():
                billObj = Bill(
                    holder_name=holder,
                    holder_phone=phone,
                    issued_date=_issued_date,
                    expiry_date=_expiry_date,
                    exchange_rate_id=exchange_rate.id,
                    currency=exchange_rate.currency
                )
                billObj.save()

                for item in items:
                    fee_id = item['fee_id']
                    project_id = item['project_id']
                    fee = Fee.objects.get(id=fee_id)
                    project = Project.objects.get(id=project_id)
                    qnt = 1
                    total_amount = qnt*fee.price

                    billItem = BillItem(
                        bill_id=billObj.id,
                        fee_id=fee.id,
                        project=project,
                        quantity=qnt,
                        unit_price=fee.price,
                        amount=total_amount
                    )

                    billItem.save()

            # request control number
            request_control_number(bill=billObj)

        except Exception as e:
            message = str(e)
            http_status = status.HTTP_400_BAD_REQUEST

        return Response({
            'message': message,
        }, status=http_status)
