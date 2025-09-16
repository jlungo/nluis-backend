from django.contrib.auth.models import Group
from account.models import User
from django.db import models

# Create your models here.
from django_currentuser.db.models import CurrentUserField


class Station(models.Model):
    class Meta:
        db_table = 'auth_stations'
        verbose_name = 'Station'
        verbose_name_plural = 'Stations'

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey(
        'nluis_authorization.Station', null=True, blank=True, on_delete=models.SET_NULL)
    locality = models.ForeignKey(
        'nluis_localities.Locality', null=True, blank=True, on_delete=models.SET_NULL)
    is_default = models.BooleanField(default=False)
    created_date = models.DateField(auto_now_add=True, blank=True, null=True)
    created_time = models.TimeField(auto_now_add=True, blank=True, null=True)
    last_update_date = models.DateField(auto_now=True)
    last_update_time = models.TimeField(auto_now=True)
    created_by = CurrentUserField()
    updated_by = CurrentUserField(
        on_update=True, related_name='stations_updated_by')

    def __str__(self):
        return self.name

    def getChildrenIds(self):
        childIds = Station.objects.raw(
            'WITH RECURSIVE children AS (SELECT auth_stations.* c FROM auth_stations WHERE id = %s UNION SELECT s.* FROM auth_stations s INNER JOIN children c ON c.id = s.parent_id) SELECT id FROM children',
            [
                self.id]
        )
        return childIds


class AppUser(models.Model):
    class Meta:
        db_table = 'auth__app_users'

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    gender = models.CharField(
        max_length=20, choices=(('M', 'Male'), ('F', 'Female')))
    middle_name = models.CharField(max_length=20)

    station = models.ForeignKey(
        Station, on_delete=models.DO_NOTHING, blank=True, null=True)

    project = models.ForeignKey(
        'nluis_projects.Project', on_delete=models.SET_NULL, null=True, blank=True)
    created_date = models.DateField(auto_now_add=True, blank=True, null=True)
    created_time = models.TimeField(auto_now_add=True, blank=True, null=True)
    last_update_date = models.DateField(auto_now=True)
    last_update_time = models.TimeField(auto_now=True)
    created_by = CurrentUserField(related_name='auth_user_created_by')
    updated_by = CurrentUserField(
        on_update=True, related_name='auth_user_updated_by')

    def __str__(self):
        return self.user.email

    def user_id(self):
        return self.user.id


class Menu(models.Model):
    class Meta:
        db_table = 'auth__menu'

    name = models.CharField(max_length=50, unique=True)
    icon = models.CharField(max_length=40)
    screen_code = models.CharField(max_length=50)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class GroupMenu(models.Model):
    class Meta:
        db_table = 'auth__menu_group'

    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    menu = models.ManyToManyField(Menu)

    def __str__(self):
        return self.group.name
