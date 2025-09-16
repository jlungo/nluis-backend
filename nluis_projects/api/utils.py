
from nluis_authorization.models import Station, AppUser
from nluis_localities.models import Locality, LocalityLevel
from nluis_projects.models import (
    ProjectType
)


def get_user_levels(self):
    results = []
    app_user = AppUser.objects.get(user=self.request.user)
    station = Station.objects.get(id=app_user.station_id)
    locality = Locality.objects.get(id=station.locality.id)
    locality_level = LocalityLevel.objects.get(id=locality.level.id)
    childs = locality_level.getChildrenIds()
    project_types = ProjectType.objects.filter(
        level_id__in=childs, is_monitoring=False)
    for type in project_types:
        results.append({
            'id': type.id,
            'name': type.name,
            'level_id': type.level_id
        })

    return results


def get_user_level_ids(self):
    app_user = AppUser.objects.get(user=self.request.user)
    station = Station.objects.get(id=app_user.station_id)
    locality = Locality.objects.get(id=station.locality.id)
    locality_level = LocalityLevel.objects.get(id=locality.level.id)
    childs = locality_level.getChildrenIds()

    return childs


def get_user_level(self):
    app_user = AppUser.objects.get(user=self.request.user)
    station = Station.objects.get(id=app_user.station_id)
    locality = Locality.objects.get(id=station.locality.id)
    locality_level = LocalityLevel.objects.get(id=locality.level.id)

    return locality_level.id


def get_user_station_ids(self):

    try:
        app_user = AppUser.objects.get(user=self.request.user)
        station = Station.objects.get(id=app_user.station_id)
        childs = station.getChildrenIds()

        return childs
    except:
        return []
