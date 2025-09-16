# nluis_localities/api/urls.py
from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import LocalityLevelViewSet, LocalityViewSet, LocalityGeoJSONUploadFormView

router = DefaultRouter()
router.register(r"levels", LocalityLevelViewSet, basename="locality-level")
router.register(r"localities", LocalityViewSet, basename="locality")

urlpatterns = [
    path("upload-geojson/", LocalityGeoJSONUploadFormView.as_view(),
         name="locality-upload-geojson-form"),
]


urlpatterns += router.urls
