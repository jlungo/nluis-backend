from django.core.validators import RegexValidator
from django.db import models

phone_regex = RegexValidator(
    regex=r"^\+?1?\d{9,14}$",
    message="Phone number must be entered in the format: '+xxx xxx xxx xxx'. Up to 14 digits allowed.",
)


class GenderType(models.IntegerChoices):
    MALE = 1, "Male"
    FEMALE = 2, "Female"


class UserType(models.IntegerChoices):
    STAFF = 1, "Staff"
    PLANNER = 2, "Planner"
    OFFICER = 3, "Officer"
    STAKE_HOLDER = 4, "Stakeholder"
