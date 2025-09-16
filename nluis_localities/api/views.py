# nluis_localities/api/views.py
import json
from typing import Optional
from django.core.serializers import serialize as dj_serialize
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.utils.text import slugify
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon, Polygon
from nluis_localities.models import Locality, LocalityLevel
from .serializers import *
from .filters import apply_locality_filters
from nluis_localities.models import *
from rest_framework.generics import GenericAPIView
from django.db import transaction
from rest_framework.parsers import MultiPartParser, FormParser


class LocalityLevelViewSet(viewsets.ModelViewSet):
    """
    CRUD for locality levels (Region/District/Ward/Village).
    """
    queryset = LocalityLevel.objects.all().order_by("name")
    serializer_class = LocalityLevelSerializer
    permission_classes = [IsAuthenticated]  # adjust if public read required

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def public(self, request, *args, **kwargs):
        """
        Optional: public read endpoint (read-only).
        """
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class LocalityViewSet(viewsets.ModelViewSet):
    queryset = Locality.objects.all().order_by("name")
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        # Hide geom on GET list/retrieve; include geom on create/update/partial_update
        if self.action in ("list", "retrieve"):
            return LocalityReadSerializer
        return LocalitySerializer

    def get_queryset(self):
        qs = super().get_queryset().select_related("level", "parent")
        qs = apply_locality_filters(qs, self.request)

        # For list/retrieve, avoid fetching the heavy geometry column
        if getattr(self, "action", None) in ("list", "retrieve"):
            qs = qs.defer("geom")
        return qs

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def geojson(self, request, *args, **kwargs):
        # Fetch WITH geometry regardless of defers above
        qs = apply_locality_filters(Locality.objects.select_related("level", "parent"), request)

        geojson_str = dj_serialize(
            "geojson",
            qs,
            geometry_field="geom",
            fields=("id", "name", "code", "level", "parent"),
        )
        return Response(json.loads(geojson_str))

    @action(detail=True, methods=["get"], permission_classes=[AllowAny])
    def boundary(self, request, pk=None):
        qs = Locality.objects.filter(pk=pk)
        geojson_str = dj_serialize(
            "geojson",
            qs,
            geometry_field="geom",
            fields=("id", "name", "code", "level", "parent"),
        )
        return Response(json.loads(geojson_str))



def _ensure_multipolygon4326(geom: GEOSGeometry) -> MultiPolygon:
    if geom.srid is None:
        geom.srid = 4326
    if geom.srid != 4326:
        geom.transform(4326)
    if geom.geom_type == "Polygon":
        return MultiPolygon(geom, srid=4326)
    if geom.geom_type == "MultiPolygon":
        return geom
    # GeometryCollection → take polygons only
    if geom.geom_type == "GeometryCollection":
        polys = [g for g in geom if g.geom_type == "Polygon"]
        if polys:
            return MultiPolygon(polys, srid=4326)
    raise ValueError(f"Unsupported geometry type: {geom.geom_type}")


def _get_or_create_level(level_name: str) -> LocalityLevel:
    obj, _ = LocalityLevel.objects.get_or_create(
        name=level_name, defaults={"code": level_name[:10]})
    return obj


def _lookup_parent(parent_code: Optional[str], parent_level_name: Optional[str]) -> Optional[Locality]:
    if not parent_code or not parent_level_name:
        return None
    try:
        parent_level = LocalityLevel.objects.get(name=parent_level_name)
        return Locality.objects.get(level=parent_level, code=parent_code)
    except (LocalityLevel.DoesNotExist, Locality.DoesNotExist):
        return None


class LocalityGeoJSONUploadFormView(GenericAPIView):
    """
    POST multipart/form-data:
      - level_name: Region|District|Ward|Village
      - parent_level: optional (e.g., Region when uploading Districts)
      - field_map: JSON, e.g. {"name":"REG_NAME","code":"REG_CODE","parent_code":"REG_CODE"}
      - file: .geojson FeatureCollection
    """
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = LocalityGeoJSONUploadFormSerializer  # ✅ correct name

    def post(self, request):
        # ✅ lets DRF render form fields in browsable API
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)

        level_name = ser.validated_data["level_name"]
        parent_level_name = ser.validated_data.get("parent_level") or None
        fmap = ser.validated_data["field_map"]

        # read file
        try:
            raw = request.FILES["file"].read().decode("utf-8")
            fc = json.loads(raw)
        except Exception as e:
            return Response({"detail": f"Invalid GeoJSON file: {e}"}, status=status.HTTP_400_BAD_REQUEST)

        if fc.get("type") != "FeatureCollection" or "features" not in fc:
            return Response({"detail": "File must be a GeoJSON FeatureCollection."}, status=400)

        name_key = fmap["name"]
        code_key = fmap["code"]
        parent_code_key = fmap.get("parent_code")

        level = _get_or_create_level(level_name)
        created, updated, errors = 0, 0, []

        with transaction.atomic():
            for i, feat in enumerate(fc["features"], start=1):
                try:
                    props = feat.get("properties") or {}
                    geom_json = feat.get("geometry")
                    if not geom_json:
                        raise ValueError("Missing geometry")

                    geom = GEOSGeometry(json.dumps(geom_json))
                    mp = _ensure_multipolygon4326(geom)

                    name_val = str(props.get(name_key, "")).strip()
                    code_val = str(props.get(code_key, "")).strip()
                    if not name_val or not code_val:
                        raise ValueError(
                            f"Missing '{name_key}' or '{code_key}' in properties")

                    parent_obj = None
                    if parent_code_key and parent_level_name:
                        pcode = str(props.get(parent_code_key, "")).strip()
                        parent_obj = _lookup_parent(pcode, parent_level_name)

                    obj, is_created = Locality.objects.get_or_create(
                        level=level, code=code_val,
                        defaults={"name": name_val,
                                  "parent": parent_obj, "geom": mp}
                    )
                    if is_created:
                        if hasattr(obj, "centroid") and obj.geom:
                            obj.centroid = obj.geom.centroid
                        if hasattr(obj, "extra"):
                            obj.extra = props
                        obj.save()
                        created += 1
                    else:
                        obj.name = name_val or obj.name
                        if parent_obj:
                            obj.parent = parent_obj
                        obj.geom = mp
                        if hasattr(obj, "extra"):
                            obj.extra = props
                        if hasattr(obj, "centroid") and obj.geom:
                            obj.centroid = obj.geom.centroid
                        obj.save()
                        updated += 1
                except Exception as e:
                    errors.append({"feature_index": i, "error": str(e)})

        return Response({"created": created, "updated": updated, "errors": errors}, status=200)
