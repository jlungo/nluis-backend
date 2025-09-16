# nluis_localities/api/filters.py
from django.db.models import Q

def apply_locality_filters(qs, request):
    """
    Supported query params:
      - name (icontains)
      - code (exact or icontains via code__icontains)
      - level (id)
      - parent (id)
      - bbox=minx,miny,maxx,maxy  (4326)
      - updated_after=ISO-8601 date (YYYY-MM-DD)
    """
    name = request.query_params.get("name")
    code = request.query_params.get("code")
    level = request.query_params.get("level")
    root = request.query_params.get("root")
    parent = request.query_params.get("parent")
    updated_after = request.query_params.get("updated_after")
    bbox = request.query_params.get("bbox")

    if name:
        qs = qs.filter(name__icontains=name)

    if code:
        # allow partial code search
        qs = qs.filter(code__icontains=code)

    if level:
        qs = qs.filter(level_id=level)

    if parent:
        qs = qs.filter(parent_id=parent)

    if root and root == "true":
        qs = qs.filter(parent__isnull=True)

    if updated_after:
        qs = qs.filter(updated_at__date__gte=updated_after)

    if bbox:
        try:
            minx, miny, maxx, maxy = map(float, bbox.split(","))
            from django.contrib.gis.geos import Polygon
            poly = Polygon.from_bbox((minx, miny, maxx, maxy))
            poly.srid = 4326
            qs = qs.filter(geom__intersects=poly)
        except Exception:
            pass

    return qs
