from rest_framework import serializers
from nluis_ccro.models import *
class ParcelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parcel
        fields = ['id', 'claim_no', 'claim_date', 'vac_1', 'vac_2', 'topology', 'datetime', 'area', 'registration_no',
                  'uka_namba', 'last_remark', 'locality_info',
                  'north', 'south', 'east', 'west', 'status', 'stage', 'created_user', 'parties', 'use']