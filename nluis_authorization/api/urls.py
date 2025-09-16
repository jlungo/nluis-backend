from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from nluis_authorization.api.views import (
    CreateUserView,
    activate,
    GroupListView,
    MenuListView,
    TokenObtainPairView2,
    StaffUserListView,
    NormalUserListView,
    ChangePasswordView
)

urlpatterns = [
    path('login', TokenObtainPairView2.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify', TokenVerifyView.as_view(), name='token_verify'),
    path('activate/<uidb64>/<token>',
         activate, name='activate'),
    path('menus', MenuListView.as_view()),
    path('groups', GroupListView.as_view()),
    path('user/create', CreateUserView.as_view()),
    path('users', StaffUserListView.as_view()),
    path('normal-users', NormalUserListView.as_view()),
    path('change-password', ChangePasswordView.as_view()),
]
