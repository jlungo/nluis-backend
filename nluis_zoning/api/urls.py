# nluis_zoning/api/urls.py
from django.urls import path
from .views import (
    LandUsePlanListCreateView, LandUsePlanDetailView,
    LandUseZoneListCreateView, LandUseZoneDetailView,
    LandUseZoneGeoJSONView, LandUseZoneBulkUploadView,
    LandUseZoneTileView,  # NEW
)

urlpatterns = [
    # Plans
    path("plans/", LandUsePlanListCreateView.as_view(), name="plan-list-create"),
    path("plans/<int:pk>/", LandUsePlanDetailView.as_view(), name="plan-detail"),

    # Zones
    path("zones/", LandUseZoneListCreateView.as_view(), name="zone-list-create"),
    path("zones/<int:pk>/", LandUseZoneDetailView.as_view(), name="zone-detail"),

    # Zones as GeoJSON (viewport)
    path("zones/geojson/", LandUseZoneGeoJSONView.as_view(), name="zone-geojson"),

    # Bulk upload FeatureCollection
    path("zones/bulk/", LandUseZoneBulkUploadView.as_view(), name="zone-bulk"),

    # NEW: Vector tiles
    path("zones/tiles/<int:z>/<int:x>/<int:y>.mvt", LandUseZoneTileView.as_view(), name="zone-tiles"),
]
