from django.urls import path

from nluis_reports.api.views import (
    ReportListView,
    LandUsesAreaView,
    FunderView,
    SpecialPartiesView,generate_excel,
    LandUseGenerateDocView,
    DownloadDocView

)

urlpatterns = [
    path('list', ReportListView.as_view()),
    path('land-uses-area', LandUsesAreaView.as_view()),
    path('funders', FunderView.as_view()),
    path('special-parties/<int:village_id>', SpecialPartiesView.as_view()),
    path('docs', LandUseGenerateDocView.as_view()),
    path('docs-download', DownloadDocView.as_view()),
    path('generate_excel/<int:project_id>/<str:village_name>', generate_excel, name='generate_excel'),
]
