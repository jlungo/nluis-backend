from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path('identity-types', views.IdentityTypeListView.as_view()),
    path('document-types', views.DocumentTypeListView.as_view()),
    path('occupancy-types', views.OccupancyTypeListView.as_view()),
    path('party-roles', views.PartyRoleListView.as_view()),
    path('land-uses', views.LandUseListView.as_view()),
    path('funders', views.FunderListView.as_view()),
    path('funders/create', views.FunderCreateView.as_view()),
    path('currencies/', views.CurrencyListView.as_view()),
]
