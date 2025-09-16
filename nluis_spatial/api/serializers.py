from rest_framework import serializers
from nluis_ccro.models import Party

from nluis_spatial.models import (
    SpatialUnit
)


class SpatialListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpatialUnit
        fields = ['id', 'area', 'use']


class PartiesListSerialzers(serializers.ModelSerializer):
    class Meta:
        model = Party
        fields = ['id', 'first_name', 'middle_name', 'last_name', 'role', 'phone', 'picture']
