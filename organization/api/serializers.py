from rest_framework import serializers
from organization.models import Organization, OrganizationType


class OrganizationSerializer(serializers.ModelSerializer):
    type_name = serializers.CharField(source="type.name", read_only=True)
    class Meta:
        model = Organization
        fields = [
            "id",
            "name",
            "short_name",
            "url",
            "type_name",
            "type",
            "status",
            "level",
            "address",
        ]
        read_only_fields = ["id"]


class OrganizationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationType
        fields = [
            "id",
            "name",
        ]
        read_only_fields = ["id"]

