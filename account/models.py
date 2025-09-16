from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import Group
from account.privileges import PrivilegeEnum
from organization.models import Organization
from django.forms import ValidationError
from autoslug import AutoSlugField
from django.db.models import Q
from account.manager import *
from django.db import models
from .consts import *
import uuid


class Module(models.Model):
    slug = AutoSlugField(populate_from="name", unique=True)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = "module"
        ordering = ["-id"]

    def __str__(self):
        return self.name


class UserRole(models.Model):
    """Roles with Fixed Privileges from Enum"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, blank=True, null=True)
    alias = models.CharField(max_length=100, null=True)

    # privileges = models.JSONField(default=list)
    class Meta:
        db_table = "auth_user_role"
        ordering = ["-id"]

    def __str__(self):
        return self.name

    # def clean(self):
    #     """Validate privileges before saving"""
    #     invalid_privileges = [
    #         privilege for privilege in self.privileges if privilege not in PrivilegeEnum.values()
    #     ]

    #     if invalid_privileges:
    #         raise ValidationError(
    #             f"Invalid privileges: {', '.join(invalid_privileges)}"
    #         )

    # def save(self, *args, **kwargs):
    #     """Ensure validation is triggered before saving"""
    #     self.clean()
    #     super().save(*args, **kwargs)

    # def has_privilege(self, privilege):
    #     """Check if role has a specific privilege"""
    #     return privilege in self.privileges


class UserRolePermission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module = models.ForeignKey(
        Module, related_name="module_permissions", on_delete=models.CASCADE
    )
    user_role = models.ForeignKey(
        UserRole, related_name="role_permissions", on_delete=models.CASCADE
    )
    group = models.ForeignKey(
        Group, related_name="user_groups", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_role_permission"
        ordering = ["-id"]
        unique_together = ("module", "user_role", "group")


class UserGroup(models.Model):  # TODO: Remove
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=100, unique=True)
    alias = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "auth_user_groups"


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User Model with Role-Based Access"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_type = models.PositiveSmallIntegerField(
        choices=UserType.choices, default=UserType.STAFF
    )
    gender = models.PositiveSmallIntegerField(choices=GenderType.choices)
    email = models.EmailField(
        max_length=40, verbose_name="Email Address", unique=True, db_index=True
    )
    first_name = models.CharField(max_length=30, blank=True, verbose_name="First Name")
    last_name = models.CharField(max_length=30, blank=True, verbose_name="Last Name")
    phone = models.CharField(
        validators=[phone_regex], max_length=17, unique=True, blank=True, null=True
    )
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    organization = models.ForeignKey(
        Organization,
        related_name="user_organizations",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    role = models.ForeignKey(
        UserRole,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="user_roles",
    )
    login_attempt = models.IntegerField(default=0)
    objects = UserManager()
    REQUIRED_FIELDS = ["first_name", "last_name", "gender", "user_type"]

    USERNAME_FIELD = "email"

    def clean(self):
        super().clean()
        if self.organization and self.user_type not in [
            UserType.STAFF,
            UserType.PLANNER,
            UserType.OFFICER,
        ]:
            raise ValidationError(
                {"organization": "Organization must be of type Staff, Planner, or Officer."}
            )

    def __str__(self):
        return self.email

    def has_privilege(self, privilege):
        """Check if the user's role has a specific privilege"""
        if self.role:
            return self.role.has_privilege(privilege)
        return False

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_first_name(self):
        """
        Returns the short name for the user.
        """
        return self.first_name

    def get_role(self):
        """
        Returns the roles for the user.
        """
        if self.role:

            return {"name": self.role.name, "privileges": self.role.privileges}
        return None

    def get_group(self):
        if self.group:
            user_group = self.group
            return {
                "name": user_group.name,
                "id": user_group.id,
                "code": user_group.code,
            }
        return None

    @property
    def user_modules(self):
        role = self.role
        if role:
            user_role_permissions = role.role_permissions.order_by(
                "module_id"
            ).distinct("module_id")

            return [
                {"slug": permission.module.slug, "name": permission.module.name}
                for permission in user_role_permissions
            ]

    class Meta:
        verbose_name_plural = "Users"
        db_table = "auth_users"


class UserProfile(models.Model):
    """User Profile Model for Additional User Information"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    address = models.CharField(max_length=255, blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to="media/profile_pictures/", blank=True, null=True
    )
    date_of_birth = models.DateField(blank=True, null=True)

    class Meta:
        db_table = "auth_user_profile"

    def __str__(self):
        return f"{self.user.email} Profile"