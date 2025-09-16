"""nluis URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.documentation import include_docs_urls
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from nluis import settings
from nluis_authorization.views import test_logic

api_documentation_urlpatterns = [
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/v1/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/v1/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('account.api.urls')),
    path('api/v1/projects/', include('nluis_projects.api.urls')),
    path('api/v1/setup/', include('nluis_setups.api.urls')),
    path('api/v1/localities/', include('nluis_localities.api.urls')),
    path('api/v1/collect/', include('nluis_collect.api.urls')),
    path('api/v1/spatial/', include('nluis_spatial.api.urls')),
    path('api/v1/reports/', include('nluis_reports.api.urls')),
    path('api/v1/billing/', include('nluis_billing.api.urls')),
    path('api/v1/form-management/', include('nluis_form_management.api.urls')),
    path('api/v1/organization/', include('organization.api.urls')),
    path('api/v1/zoning/', include('nluis_zoning.api.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_URL)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += api_documentation_urlpatterns

admin.sites.AdminSite.site_header = 'National Land Use Information System'
admin.sites.AdminSite.site_title = 'NLUIS'
admin.sites.AdminSite.index_title = 'Admin'
