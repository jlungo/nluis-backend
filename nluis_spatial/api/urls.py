from django.urls import path

from nluis_spatial.api.views import (
    LocalityGeometryView,
    ParcelGeometryView,
    ProjectGeometryView,
    ProjectLandUseView,
    PartiesListView,
    CreatePartyView,
    AllocatePartyView,
    ProjectPlotListView,
    UpdatePartyPictureView
)

urlpatterns = [
    path('locality/<int:level_id>', LocalityGeometryView.as_view()),
    path('parcel/<int:pk>', ParcelGeometryView.as_view()),
    path('project/<int:id>', ProjectGeometryView.as_view()),
    path('landuse-area', ProjectLandUseView.as_view()),

    # path('deedplan/info/<int:project_id>', DeedPlanListView.as_view()),
    # path('create/deedplan', CreateDeedPlanView.as_view()),
    # path('create/layers', CreateLayerView.as_view()),
    path('create/party', CreatePartyView.as_view()),
    path('update/party-picture', UpdatePartyPictureView.as_view()),
    path('<int:project_id>/plots/<int:parcel>/<str:status>', ProjectPlotListView.as_view()),
    path('<int:project_id>/list/parties', PartiesListView.as_view()),
    # path('<int:project_id>/list/data/<int:stage>', ListDataByStageView.as_view()),
    path('allocate', AllocatePartyView.as_view()),
    # path('<int:project_id>/list/draft', ListDraftDataView.as_view()),
    # path('generate/ccro/<int:deed_id>', GenerateCCROView.as_view()),
    # path('migrate', MigrateCCROView.as_view())

]
