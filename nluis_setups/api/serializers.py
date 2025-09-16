from rest_framework import serializers

from nluis_setups.models import (
    IdentityType,
    DocumentType,
    OccupancyType,
    LandUse,
    PartyRole,
    Funder,
    Designation,
    Currency,
)


class IdentityTypeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = IdentityType
        fields = ['id', 'name', 'description']


class DocumentTypeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = ['id', 'name', 'code', 'is_input', 'acceptable_format']


class OccupancyTypeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = OccupancyType
        fields = ['id', 'name', 'description']


class PartyRoleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartyRole
        fields = ['id', 'name', 'description']


class LandUseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = LandUse
        fields = ['id', 'name', 'description', 'color', "style"]


class FunderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Funder
        fields = ['id', 'name', 'category']


class DesignationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = ['id', 'name', 'description']


class CurrencySerializer(serializers.ModelSerializer):

    class Meta:
        model = Currency
        fields = ["id", "name", "code"]