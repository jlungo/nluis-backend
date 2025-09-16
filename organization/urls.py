from django.urls import path
from .views import *

urlpatterns = [

    # Urls
    path('', OrganizationView.as_view(), name='organization'),
    path('nopagination/', OrganizationNoPaginationView.as_view(),
         name='organization-no-pagination'),
    path('type/', OrganizationTypeView.as_view(), name='organization-type'),
    path('type/nopagination/', OrganizationTypeNoPaginationView.as_view(),
         name='organization-type-no-pagination'),
    path('type/<str:pk_type>/',
         OrganizationTypeUpdateView.as_view(), name='organization-type-update'),
    path('<str:pk_organization>/', OrganizationUpdateView.as_view(),
         name='organization-update'),
]
