from django.urls import path

from nluis_projects.api.views import *

urlpatterns = [
    path('', ProjectListView.as_view()),
    path('published', PublishedProjectListView.as_view()),
    path('monitoring', MonitoringProjectView.as_view()),
    path('create/', CreateProjectView.as_view()),
    path('<int:pk>/', ProjectInfoView.as_view()),
    path('<int:pk>/update/', UpdateProjectView.as_view()),
    path('<int:pk>/delete/', DeleteProjectView.as_view()),
    path('approve/<int:pk>', AproveProjectView.as_view()),
    path('project-types', ProjectTypeListView.as_view()),
    path('public/project-types', ProjectTypePublicListView.as_view()),
    path('stats', ProjectStatsView.as_view()),
    path('team-members/<int:project_id>', TeamMemberListView.as_view()),
    path('team-members-history/<int:project_id>',
         TeamMemberHistoryListView.as_view()),
    path('team-members/create', CreateTeamMemberView.as_view()),
    path('team-members/add', AddTeamMemberView.as_view()),
    path('documents/<int:pk>', DocumentListView.as_view()),
    path('document-list/<int:project_id>/<int:task_id>',
         ProjectDocumentsView.as_view()),
    path('signatories/create', CreateSignatoryView.as_view()),
    path('signatories/<int:project_id>', SignatoryListView.as_view()),
    path('localities/<int:project_id>', LocalitiesListView.as_view()),
    path('project-status', ProjectStatusListView.as_view()),
    path('list/<int:project_type_id>/<int:status_id>/<str:desc>',
         ProjectSearchListView.as_view()),
  path("projects/<int:pk>/approval/", ProjectApprovalView.as_view(), name="project-approval"),
  path(
        "locality-projects/approval-update/",
        LocalityProjectApprovalUpdateView.as_view(),
        name="locality-project-approval-update",
    ),
]
