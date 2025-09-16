from django.urls import path

from nluis_collect.api.views import CCRODocumentListView, CreateMobileDataView, CCRORemarkListView, \
    CCROCreateRemarkListView, CCRODownloadSHP, ConfigUserView, ListDraftDataView, CCROUploadSHP, \
    CCROChangeStageListView, QuestionnairesListView, QuestionnairesFormsListView, QuestionnairesCreateAnswerView, \
    QuestionnairesAnalyseView, QuestionnairesMonitoringListView, QuestionnairesMonitoringFormsListView, download_excel, \
    CCROUpdatePartyView, CCROGenerateDocumentView, CCROUpdatePartyPictureView, DeburgView, CreateMobileDataView2, \
    download_parcel_excel, QuestionnairesMonitoringVerificationView, QuestionnairesDownloadSHP, parcel_data, CCROVillageListView, CCROParcelCountView

urlpatterns = [
    path('mobile/user/config/<str:device_id>', ConfigUserView.as_view()),
    path('upload/mobile/data', CreateMobileDataView.as_view()),
    path('upload/mobile/data-backup', CreateMobileDataView2.as_view()),

    path('ccro/parcelcount/', CCROParcelCountView.as_view(), name='ccro_parcel_count'),

    path('list/draft/<int:project_id>/<int:locality_id>/<str:flag>', ListDraftDataView.as_view()),
    path('ccro/download/shp', CCRODownloadSHP.as_view()),
    path('ccro/download/excel', download_excel),
    path('ccro/download/excel/<str:stage>', download_parcel_excel),
    path('ccro/upload/shp', CCROUploadSHP.as_view()),
    path('ccro/create/remark', CCROCreateRemarkListView.as_view()),
    path('ccro/remarks/<int:pk>', CCRORemarkListView.as_view()),
    path('ccro/documents/<int:pk>', CCRODocumentListView.as_view()),
    path('ccro/generate-doc', CCROGenerateDocumentView.as_view()),
    path('ccro/change/stage', CCROChangeStageListView.as_view()),
    # FOR API INTEGRATION
    path('ccro/parcel-data/<str:stage>/', parcel_data),
    path('ccro/villages/', CCROVillageListView.as_view()),

    # END INTEGRATION

    path('questionnaires/list/<int:project_id>/<int:has_answers>/<str:flag>/<int:is_analysis>',
         QuestionnairesListView.as_view()),
    path('questionnaires/monitoring/list/<int:project_type_id>/<int:has_answers>/<str:flag>',
         QuestionnairesMonitoringListView.as_view()),

    path('questionnaires/<int:project_id>/<int:form_id>/forms/<int:has_answers>/<int:is_monitoring>',
         QuestionnairesFormsListView.as_view()),
    path('questionnaires/<int:project_id>/<int:form_id>/analyse', QuestionnairesAnalyseView.as_view()),
    path('questionnaires/create/answer', QuestionnairesCreateAnswerView.as_view()),

    path('questionnaires/monitoring/<int:form_id>/form/<int:has_answers>',
         QuestionnairesMonitoringFormsListView.as_view()),

    path('questionnaires/monitoring/verification/<int:project_id>/<int:form_id>',
         QuestionnairesMonitoringVerificationView.as_view()),

    # UPDATES
    path('ccro/update/party', CCROUpdatePartyView.as_view()),
    path('ccro/update/party-picture', CCROUpdatePartyPictureView.as_view()),
    path('deb/<str:what>/<str:who>/<str:file>/<int:project_id>', DeburgView.as_view()),

    path('questionnaires/download/shp', QuestionnairesDownloadSHP.as_view()),

]
