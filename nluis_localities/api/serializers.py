# nluis_localities/api/serializers.py
import json
from rest_framework import serializers
from django.contrib.gis.geos import GEOSGeometry
from nluis_localities.models import Locality, LocalityLevel


class GeoJSONGeometryField(serializers.JSONField):
    """
    Accepts/returns geometry as GeoJSON.
    Incoming: dict -> GEOSGeometry (SRID=4326 if missing)
    Outgoing: GEOSGeometry -> dict (parsed GeoJSON)
    """
    default_srid = 4326

    def to_internal_value(self, data):
        if data is None:
            return None
        if isinstance(data, (str, bytes)):
            geom = GEOSGeometry(data)
        else:
            geom = GEOSGeometry(json.dumps(data))
        if geom.srid is None:
            geom.srid = self.default_srid
        elif geom.srid != self.default_srid:
            # normalize on write
            geom.transform(self.default_srid)
        return geom

    def to_representation(self, value):
        if value is None:
            return None
        if value.srid != self.default_srid:
            value = value.clone()
            value.transform(self.default_srid)
        # GEOSGeometry.geojson returns a JSON string
        return json.loads(value.geojson)


class LocalityLevelSerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(
        queryset=LocalityLevel.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = LocalityLevel
        fields = [
            "id", "name", "description", "code", "parent",
            "created_at", "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

class LocalityReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Locality
        fields = ["id", "name", "code", "level", "parent", "created_at", "updated_at"]  # no geom
        

class LocalitySerializer(serializers.ModelSerializer):
    level = serializers.PrimaryKeyRelatedField(queryset=LocalityLevel.objects.all())
    parent = serializers.PrimaryKeyRelatedField(
        queryset=Locality.objects.all(), required=False, allow_null=True
    )
    geom = GeoJSONGeometryField(required=False, allow_null=True)
    centroid = GeoJSONGeometryField(required=False, allow_null=True)

    class Meta:
        model = Locality
        fields = [
            "id", "name", "code", "level", "parent",
            "geom", "centroid",
            "created_at", "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at", "centroid"]

    def create(self, validated_data):
        # centroid is computed in model.save(); ensure SRID normalization here too
        geom = validated_data.get("geom")
        if geom and geom.srid != 4326:
            geom.transform(4326)
            validated_data["geom"] = geom
        return super().create(validated_data)

    def update(self, instance, validated_data):
        geom = validated_data.get("geom", None)
        if geom and geom.srid != 4326:
            geom.transform(4326)
            validated_data["geom"] = geom
        return super().update(instance, validated_data)



# nluis_localities/api/serializers_upload.py

class LocalityGeoJSONUploadFormSerializer(serializers.Serializer):
    """
    Multipart form:
      - level_name: e.g. "Region", "District", "Ward", "Village"
      - parent_level: optional, e.g. "Region" (when uploading Districts)
      - field_map: JSON string or object, e.g. {"name":"REG_NAME","code":"REG_CODE","parent_code":"REG_CODE"}
      - file: the .geojson (FeatureCollection) file
    """
    level_name = serializers.CharField()
    parent_level = serializers.CharField(required=False, allow_blank=True)
    field_map = serializers.JSONField()  # can accept a JSON string or object in multipart
    file = serializers.FileField()

    def validate(self, data):
        fmap = data["field_map"]
        for key in ("name", "code"):
            if key not in fmap:
                raise serializers.ValidationError(f"field_map must include '{key}'")
        return data
