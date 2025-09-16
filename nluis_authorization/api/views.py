from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from nluis_authorization.models import AppUser, Station
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from django.http import HttpResponse
from django.db import transaction
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from nluis_authorization.token import account_activation_token
from nluis_authorization.api.service import createUser

# Create your views here.
from rest_framework import generics
from rest_framework_simplejwt.views import TokenObtainPairView

from nluis_authorization.api.serializers import (
    MenuListSerializer,
    LoginSerializer,
    GroupListSerializer,
    UserListSerializer
)
from nluis_authorization.models import Menu


class TokenObtainPairView2(TokenObtainPairView):
    serializer_class = LoginSerializer


class MenuListView(generics.ListAPIView):
    serializer_class = MenuListSerializer
    queryset = Menu.objects.all()


class GroupListView(generics.ListAPIView):
    serializer_class = GroupListSerializer
    queryset = Group.objects.all()


class StaffUserListView(generics.ListAPIView):
    serializer_class = UserListSerializer
    queryset = User.objects.filter(is_staff=True)


# Create User View


class CreateUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        message = 'Success'
        http_status = status.HTTP_201_CREATED

        try:
            newUser = createUser(request)
            if newUser['status']:
                message = newUser['msg']
            else:
                message = newUser['msg']
                http_status = status.HTTP_400_BAD_REQUEST
        except Exception as e:
            message = str(e)
            http_status = status.HTTP_400_BAD_REQUEST

        return Response({
            'message': message,
        }, http_status)


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        return redirect('/')

    else:
        # return HttpResponse('Activation link is invalid!')
        return Response({
            'message': 'Activation link is invalid!',
        }, status.HTTP_201_CREATED)


class NormalUserListView(generics.ListAPIView):
    serializer_class = UserListSerializer
    queryset = User.objects.all()
        #filter(is_staff=False)


#changing user password

class ChangePasswordView(APIView):
    def post(self, request):
        message = ''
        try:
            user = request.user
            old_password = request.data.get('old_password')
            new_password = request.data.get('new_password')
            
            # Check if old password is correct
            if not user.check_password(old_password):
                return Response({
                    'message': 'Current password is incorrect'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Set new password
            user.set_password(new_password)
            user.save()
            
            return Response({
                'message': 'Password changed successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            message = str(e)
            traceback.print_exc()
            
        return Response({
            'message': message
        }, status=status.HTTP_400_BAD_REQUEST)
