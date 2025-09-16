from django.urls import path, include
from account.api.views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.routers import DefaultRouter  # Import the router

# Create a router and register your viewset
router = DefaultRouter()
# router.register(r'roles', RoleViewSet, basename='role')  # Register RoleViewSet
router.register(r'groups', UserGroupViewSet, basename='groups')  # Register RoleViewSet

urlpatterns = [
    # Token
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # other auth
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/create/', CreateUserView.as_view(), name='user-create'),
    path('users/<str:pk_user>/', UserUpdateView.as_view(), name='user-update'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('bulk-user-upload/', BulkUserUploadView.as_view(), name='bulk-user-upload'),
    path('email-verify/', VerifyEmailView.as_view(), name='email-verify'),
    path('resend-account-verify-email/',
            UserReSendAccountActivationEmailView.as_view(), name='email-verify'),
    path('request-password-reset-email/', RequestPasswordResetEmail.as_view(),
            name="request-password-reset-email"),
    path('password-reset/<uidb64>/<token>/',
            PasswordTokenCheckAPI.as_view(), name='password-reset-confirm'),
    path('password-reset-complete', SetNewPasswordAPIView.as_view(),
            name='password-reset-complete'),
    path('permissions/<slug:module_slug>/', UserPermissionView.as_view(), name='user-permissions'),
    path('modules/', ModuleListView.as_view(), name='module-list'),
    path('roles/', UserRoleListView.as_view(), name='user-role-list'),
    path('suspend/<uuid:id>/', UserSuspendView.as_view(), name='user-suspend'),
    path('', include(router.urls)),
]
