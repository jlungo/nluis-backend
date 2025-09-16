
from django.contrib.auth.models import User, Group
from nluis_authorization.models import AppUser, Station

from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from nluis_authorization.token import account_activation_token
from django.core.mail import EmailMessage
from django.db import transaction


@transaction.atomic
def createUser(request):
    station_id = None
    try:
        if validateEmail(request.data['email']):

            _user = User(
                email=request.data['email'].lower(),
                first_name=request.data['first_name'],
                last_name=request.data['last_name'],
                username=(request.data['first_name'] +
                          '.'+request.data['last_name']).lower(),
            )
            password = User.objects.make_random_password()
            print("Password : " + password)
            _user.set_password(password)
            _user.save()

            if 'station_id' in request.data:
                station_id = request.data['station_id']

            station_id = Station.objects.first().id

            app_user = AppUser(
                user=_user,
                phone=request.data['phone'],
                middle_name=request.data['middle_name'],
                station=getDefaultStation(station_id)
            )
            app_user.save()

            # to get the domain of the current site
            current_site = get_current_site(request)
            mail_subject = 'Activation link'
            message = render_to_string('verify_email.html', {
                'user': _user,
                'password': password,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(_user.pk)),
                'token': account_activation_token.make_token(_user),
            })
            to_email = _user.email
            email = EmailMessage(
                mail_subject, message, to=[
                    to_email], from_email='info@nlupc.go.tz'
            )
            email.send()

            return {"user": _user, "status": True, "msg": "Please confirm your email address to complete the registration"}
        else:
            return {"status": False, "msg": "Envalid email or username or exists"}

    except Exception as e:
        transaction.set_rollback(True)
        return {"status": False, "msg": str(e)}


# Validate email function
def validateEmail(email):
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False

# get default station


def getDefaultStation(station_id=None):

    if not station_id:
        station = Station.objects.get(is_default=True)
    else:
        station = Station.objects.get(id=station_id)
    return station
