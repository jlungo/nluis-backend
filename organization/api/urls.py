from django.urls import path
from . import views


app_name = "organization_api"


urlpatterns = [
    path("", views.OrganizationListView.as_view(), name="organization-list"),
    path("create/", views.OrganizationCreateView.as_view(), name="organization-create"),
    path("<uuid:id>/detail/", views.OrganizationDetailView.as_view(), name="organization-detail"),
    path("<uuid:id>/update/", views.OrganizationUpdateView.as_view(), name="organization-update"),
    path("<uuid:id>/delete/", views.OrganizationDeleteView.as_view(), name="organization-delete"),
    path("<uuid:id>/suspend/", views.SuspendOrganizationView.as_view(), name="suspend-organization"),
    path("<uuid:id>/activate/", views.ActivateOrganizationView.as_view(), name="organization-activate"),
    path("organization-types/", views.OrganizationTypeListView.as_view(), name="organization-type-list"),
    path("organization-types/create/", views.OrganizationTypeCreateView.as_view(), name="organization-type-create"),
    path("organization-types/<uuid:id>/", views.OrganizationTypeUpdateView.as_view(), name="organization-type-update"),
    path("organization-types/<uuid:id>/delete/", views.OrganizationTypeDeleteView.as_view(), name="organization-type-delete"),
]


