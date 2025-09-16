from abc import ABC

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from nluis_authorization.models import Menu, GroupMenu, Station
from django.contrib.auth.models import Group, User
from nluis_authorization.models import AppUser
from nluis_localities.models import Locality, LocalityLevel


class LoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        list_menu = []
        groups = []
        app_user = AppUser.objects.get(user=user)
        locality = app_user.station.locality
        level = LocalityLevel.objects.get(id=locality.level.id)

        for menu_group in GroupMenu.objects.filter(group__in=user.groups.all()):
            for menu in menu_group.menu.all().order_by('order'):
                list_menu.append({
                    'name': menu.name,
                    'icon': menu.icon,
                    'screen_code': menu.screen_code,
                    'submenu': [
                        # {'name': 'sub menu name', 'screen_code': 'screen_code', 'params': 'params'}
                    ]
                })
            groups.append({
                'id': menu_group.group.id,
                'name': menu_group.group.name
            })

        token['name'] = 'user.name'
        token['menu'] = list_menu
        token['locality'] = {
            'station_name': app_user.station.name,
            'locality_name': locality.name,
            'level':  locality.level.name
        }
        token['groups'] = groups
        print(token['locality'])
        return token


class MenuListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ['id', 'name', 'icon', 'screen_code']


class StationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ['id', 'name', 'is_default']


class GroupListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']


class UserListSerializer(serializers.ModelSerializer):

    full_name = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'

    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'first_name',
                  'last_name', 'email', 'is_staff']
