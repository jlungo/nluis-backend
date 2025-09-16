# nluis_zoning/api/serializers.py
import json
from rest_framework import serializers
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon, Polygon
from nluis_zoning.models import LandUsePlan, LandUseZone
from nluis_localities.models import Locality
from nluis_setups.models import LandUse


class GeoJSONGeometryField(serializers.JSONField):
    default_srid = 4326

    def to_internal_value(self, data):
        if data is None:
            return None

        # Parse GeoJSON into GEOSGeometry
        if isinstance(data, (str, bytes)):
            geom = GEOSGeometry(data)
        else:
            geom = GEOSGeometry(json.dumps(data))

        # Normalize SRID
        if geom.srid is None:
            geom.srid = self.default_srid
        elif geom.srid != self.default_srid:
            geom.transform(self.default_srid)

        # Accept Polygon or MultiPolygon; coerce Polygon -> MultiPolygon
        if geom.geom_type == "Polygon":
            geom = MultiPolygon(geom)
        elif geom.geom_type != "MultiPolygon":
            raise serializers.ValidationError("Only Polygon or MultiPolygon geometries are supported.")

        return geom

    def to_representation(self, value):
        if value is None:
            return None
        # Always emit as MultiPolygon (or unwrap to Polygon if you prefer)
        if value.srid != self.default_srid:
            value = value.clone()
            value.transform(self.default_srid)
        return json.loads(value.geojson)

class LandUsePlanSerializer(serializers.ModelSerializer):
    locality = serializers.PrimaryKeyRelatedField(queryset=Locality.objects.all())

    class Meta:
        model = LandUsePlan
        fields = [
            "id", "name", "locality", "effective_from", "effective_to",
            "description", "created_at", "created_by",
        ]
        read_only_fields = ["created_at", "created_by"]


# nluis_zoning/api/serializers.py
class LandUseZoneSerializer(serializers.ModelSerializer):
    land_use = serializers.PrimaryKeyRelatedField(queryset=LandUse.objects.all())
    locality = serializers.PrimaryKeyRelatedField(queryset=Locality.objects.all())
    geom = GeoJSONGeometryField()

    color = serializers.SerializerMethodField(read_only=True)  # legacy convenience
    style = serializers.SerializerMethodField(read_only=True)  # <-- NEW

    def get_color(self, obj):
        try:
            return getattr(obj.land_use, "color", None)
        except Exception:
            return None

    def get_style(self, obj):
        try:
            # return the JSON dict stored on LandUse.style
            return getattr(obj.land_use, "style", None)
        except Exception:
            return None

    class Meta:
        model = LandUseZone
        fields = [
            "id", "land_use", "locality",
            "geom", "area_sqm",
            "status", "color", "style",    # <-- include style here
            "source", "version", "deleted",
            "created_at", "created_by", "updated_at", "updated_by",
        ]
        read_only_fields = ["area_sqm", "created_at", "created_by", "updated_at", "updated_by", "color", "style"]

