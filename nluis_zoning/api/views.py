# nluis_zoning/api/views.py
import json
from datetime import datetime
from django.core.serializers import serialize as dj_serialize
from django.utils.dateparse import parse_datetime
from django.contrib.gis.geos import Polygon
from django.db import connection
from django.db.models import Q, F
from django.contrib.gis.db.models import GeometryField
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.views import APIView
from django.db.models import Func, Value
from django.http import HttpResponse

from nluis_zoning.models import LandUsePlan, LandUseZone
from nluis_setups.models import LandUse
from .serializers import LandUsePlanSerializer, LandUseZoneSerializer


# ---------- Helpers ----------
class SimplifyPreserveTopology(Func):
    """
    Wraps PostGIS ST_SimplifyPreserveTopology(geom, tolerance)
    so it can be used in .annotate().
    """
    function = "ST_SimplifyPreserveTopology"
    output_field = GeometryField()


def apply_zone_filters(qs, request):
    """
    Filters: plan, land_use, locality, deleted (true/false),
             updated_after=ISO8601, bbox=minx,miny,maxx,maxy, status
    """
    plan = request.query_params.get("plan")
    land_use = request.query_params.get("land_use")
    locality = request.query_params.get("locality")
    status_q = request.query_params.get("status")
    deleted = request.query_params.get("deleted")
    updated_after = request.query_params.get("updated_after")
    bbox = request.query_params.get("bbox")

    if plan:
        qs = qs.filter(plan_id=plan)
    if land_use:
        qs = qs.filter(land_use_id=land_use)
    if locality:
        qs = qs.filter(locality_id=locality)
    if status_q:
        qs = qs.filter(status=status_q)

    if deleted is not None:
        val = str(deleted).lower() in ("1", "true", "yes")
        qs = qs.filter(deleted=val)

    if updated_after:
        dt = parse_datetime(
            updated_after) or datetime.fromisoformat(updated_after)
        qs = qs.filter(updated_at__gte=dt)

    if bbox:
        try:
            minx, miny, maxx, maxy = map(float, bbox.split(","))
            poly = Polygon.from_bbox((minx, miny, maxx, maxy))
            poly.srid = 4326
            qs = qs.filter(geom__intersects=poly)
        except Exception:
            pass

    return qs


# ---------- Plans ----------

class LandUsePlanListCreateView(generics.ListCreateAPIView):
    """
    GET: list plans (filter by locality, active=1 to get current)
    POST: create plan
    """
    serializer_class = LandUsePlanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = LandUsePlan.objects.all().order_by("-created_at")
        locality = self.request.query_params.get("locality")
        active = self.request.query_params.get("active")
        if locality:
            qs = qs.filter(locality_id=locality)
        if active and str(active).lower() in ("1", "true", "yes"):
            qs = qs.filter(Q(effective_to__isnull=True) | Q(
                effective_to__gt=datetime.utcnow().date()))
        return qs


class LandUsePlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LandUsePlanSerializer
    permission_classes = [IsAuthenticated]
    queryset = LandUsePlan.objects.all()


# ---------- Zones ----------

class LandUseZoneListCreateView(generics.ListCreateAPIView):
    serializer_class = LandUseZoneSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = LandUseZone.objects.select_related(
            "plan", "land_use", "locality").order_by("-updated_at")
        return apply_zone_filters(qs, self.request)


class LandUseZoneDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LandUseZoneSerializer
    permission_classes = [IsAuthenticated]
    queryset = LandUseZone.objects.all()

# ---------- Zones as GeoJSON (viewport) ----------


class LandUseZoneGeoJSONView(APIView):
    """
    Read-only FeatureCollection for map layers (same filters as list).
    Supports 'zoom' param to simplify geometry.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        zoom = int(request.query_params.get("zoom", 12))
        tol_by_zoom = {10: 0.0002, 12: 0.00008,
                       14: 0.00003, 16: 0.00001, 18: 0.000005}
        tol = tol_by_zoom.get(zoom, 0.00008)

        qs = apply_zone_filters(
            LandUseZone.objects.select_related("plan", "land_use", "locality"),
            request
        ).annotate(geom_out=SimplifyPreserveTopology(F("geom"), Value(tol)))

        geojson_str = dj_serialize(
            "geojson",
            qs,
            geometry_field="geom_out",
            fields=("id", "plan", "land_use", "locality",
                    "area_sqm", "version", "deleted", "status")
        )
        # Inject color from related land_use into properties after serialization (simple pass)
        data = json.loads(geojson_str)
        lu_colors = {lu.id: getattr(lu, "color", None) for lu in LandUse.objects.filter(
            id__in=list({f["properties"]["land_use"]
                        for f in data.get("features", [])})
        )}
        for f in data.get("features", []):
            f["properties"]["color"] = lu_colors.get(
                f["properties"]["land_use"])
        return Response(data)

# ---------- NEW: Vector tile endpoint (MVT) ----------


class LandUseZoneTileView(APIView):
    """
    GET /api/v1/zoning/zones/tiles/{z}/{x}/{y}.mvt?locality=<id>&plan=&land_use=&status=&deleted=0|1
    Returns Mapbox Vector Tile (layer: 'zones') with properties: id, land_use, status, color.
    """
    permission_classes = [AllowAny]  # or IsAuthenticated, your call

    def get(self, request, z: int, x: int, y: int):
        # dynamic table names
        zones_table = LandUseZone._meta.db_table
        lu_table = LandUse._meta.db_table

        # filters
        locality = request.query_params.get("locality")
        plan = request.query_params.get("plan")
        land_use = request.query_params.get("land_use")
        status_q = request.query_params.get("status")
        deleted = request.query_params.get("deleted")

        where_clauses = ["1=1"]
        params = [z, x, y]  # for ST_TileEnvelope

        if locality:
            where_clauses.append("z.locality_id = %s")
            params.append(locality)
        if plan:
            where_clauses.append("z.plan_id = %s")
            params.append(plan)
        if land_use:
            where_clauses.append("z.land_use_id = %s")
            params.append(land_use)
        if status_q:
            where_clauses.append("z.status = %s")
            params.append(status_q)
        if deleted is not None:
            val = str(deleted).lower() in ("1", "true", "yes")
            where_clauses.append("z.deleted = %s")
            params.append(val)

        where_sql = " AND ".join(where_clauses)

        # Build + run ST_AsMVT query
        sql = f"""
        WITH bounds AS (
          SELECT ST_TileEnvelope(%s, %s, %s) AS geom3857
        ),
        src AS (
          SELECT z.id, z.land_use_id, z.status, z.deleted,
                 COALESCE(lu.color, '#6b7280') AS color,
                 ST_Transform(z.geom, 3857) AS g3857
          FROM {zones_table} z
          LEFT JOIN {lu_table} lu ON lu.id = z.land_use_id
          WHERE {where_sql}
        ),
        clipped AS (
          SELECT id, land_use_id, status, deleted, color,
                 ST_AsMVTGeom(g3857, bounds.geom3857, 4096, 64, true) AS mvtgeom
          FROM src, bounds
          WHERE g3857 && bounds.geom3857
        )
        SELECT ST_AsMVT(clipped, 'zones', 4096, 'mvtgeom') FROM clipped;
        """

        with connection.cursor() as cur:
            cur.execute(sql, params)
            row = cur.fetchone()
            tile = row[0] if row and row[0] else b""

        resp = HttpResponse(tile, content_type="application/vnd.mapbox-vector-tile")
        # (optional) if you gzip tiles at the DB/proxy layer, also set:
        # resp["Content-Encoding"] = "gzip"
        resp["Cache-Control"] = "public, max-age=60"
        return resp

# ----------Zone bulk upload----------


class LandUseZoneBulkUploadView(APIView):
    """
    POST a GeoJSON FeatureCollection to create/update zones in bulk.
    Upsert by (plan, land_use, locality, version?, optional 'id').
    Body example:
    {
      "type":"FeatureCollection",
      "features":[
        {"type":"Feature","geometry":{...},"properties":{"plan":1,"land_use":3,"locality":55,"source":"QField"}}
      ]
    }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        body = request.data
        if not isinstance(body, dict) or body.get("type") != "FeatureCollection":
            return Response({"detail": "Body must be a GeoJSON FeatureCollection."},
                            status=status.HTTP_400_BAD_REQUEST)

        created, updated, errors = 0, 0, []

        for idx, feat in enumerate(body.get("features", []), start=1):
            props = feat.get("properties") or {}
            data = {
                "plan": props.get("plan"),
                "land_use": props.get("land_use"),
                "locality": props.get("locality"),
                "geom": feat.get("geometry"),
                "source": props.get("source", ""),
                "version": props.get("version", 1),
                "deleted": props.get("deleted", False),
            }

            zone_id = props.get("id") or feat.get("id")
            if zone_id:
                try:
                    instance = LandUseZone.objects.get(id=zone_id)
                    ser = LandUseZoneSerializer(
                        instance, data=data, partial=True)
                    ser.is_valid(raise_exception=True)
                    ser.save()
                    updated += 1
                    continue
                except LandUseZone.DoesNotExist:
                    # fall through to create
                    pass
                except Exception as e:
                    errors.append(
                        {"feature": idx, "id": zone_id, "error": str(e)})
                    continue

            try:
                ser = LandUseZoneSerializer(data=data)
                ser.is_valid(raise_exception=True)
                ser.save()
                created += 1
            except Exception as e:
                errors.append({"feature": idx, "error": str(e)})

        return Response({"created": created, "updated": updated, "errors": errors})
