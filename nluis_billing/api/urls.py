from django.urls import path

from nluis_billing.api.views import (
    FeeListView, CreateBillView
)

urlpatterns = [
    path('fees', FeeListView.as_view()),
    path('create', CreateBillView.as_view()),
]
