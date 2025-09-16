from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from account.models import *
from organization.models import Organization
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, RegexValidator
from account.api.utils import Util
from decouple import config


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        try:
            user_exists = User.objects.get(email=email)

            if not user_exists.is_active:
                raise AuthenticationFailed("Account disabled, contact admin")

            if user_exists.login_attempt < 4:
                user = authenticate(email=email, password=password)

                if user is None:
                    user_exists.login_attempt += 1
                    user_exists.save()
                    remaining = 5 - user_exists.login_attempt
                    message = "tries" if remaining > 1 else "try"
                    raise AuthenticationFailed(
                        f"Invalid login credentials, {remaining} {message} left"
                    )
            else:
                user_exists.is_active = False
                user_exists.save()
                raise AuthenticationFailed(
                    "Your account has been locked due to multiple failed attempts. Contact system administrator."
                )

            # Reset login attempts
            user_exists.login_attempt = 0
            user_exists.save()

            # Get token data
            data = super().validate(attrs)

            update_last_login(None, user_exists)

            user_data = get_user_data(user=user_exists)
            data.update(user_data)

            return data

        except User.DoesNotExist:
            raise AuthenticationFailed("Invalid login credentials")

def get_user_data(user):
    profile = getattr(user, "profile", None)

    return {
        "id": user.id,
        "email": user.email,
        "user_type": user.user_type,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "organization": (
            {
                "id": user.organization.id,
                "name": user.organization.name,
            }
            if user.organization
            else None
        ),
        "role": (
            {
                "id": user.role_id,
                "name": user.role.name,
            }
            if user.role
            else None
        ),
        "modules": user.user_modules,
        "phone_number": user.phone,
    }

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

class UserRegisterSerializer(serializers.ModelSerializer):

    default_error_messages = {
        "first_name": "The First Name should only contain alphanumeric characters",
        "last_name": "The Last Name should only contain alphanumeric characters",
    }

    class Meta:
        model = User
        fields = ["user_type", "email", "first_name", "last_name", "id", "gender"]

    def validate(self, attrs):
        first_name = attrs.get("first_name", "")
        last_name = attrs.get("last_name", "")

        if not first_name.isalnum():
            raise serializers.ValidationError(self.default_error_messages["first_name"])

        if not last_name.isalnum():
            raise serializers.ValidationError(self.default_error_messages["last_name"])
        return attrs

    def create(self, validated_data):
        # default_password = "nluis@25"
        # validated_data["password"] = default_password
        return User.objects.create_user(**validated_data)


class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=555)

    class Meta:
        model = User
        fields = ["token"]


class ResendVerificationSerializer(serializers.Serializer):
    user = serializers.CharField(max_length=255)

    class Meta:
        fields = ["email"]


class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    class Meta:
        fields = ["email"]


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(min_length=1, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        fields = ["password", "token", "uidb64"]

    def validate(self, attrs):
        try:
            password = attrs.get("password")
            token = attrs.get("token")
            uidb64 = attrs.get("uidb64")

            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed("The reset link is invalid", 401)

            user.set_password(password)
            user.login_attempt = 0
            user.is_active = True
            user.is_verified = True
            user.save()

            return user
        except Exception:
            raise AuthenticationFailed("The reset link is invalid", 401)


class UserSerializer(serializers.ModelSerializer):
    role_id = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    organization_name = serializers.CharField(source='organization.name', read_only=True)

    def get_role_id(self, obj):
        return obj.role.id if obj.role else None
    
    def get_role(self, obj):
        return obj.role.name if obj.role else None

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "role_id",
            "role",
            "organization",
            "organization_name",
            "user_type",
            "gender",
            "phone",
        ]


class UserUpdateSerializer(serializers.ModelSerializer):
    # Password validation setup
    password = serializers.CharField(
        write_only=True,
        required=False,
        style={"input_type": "password"},
        validators=[
            MinLengthValidator(
                limit_value=8, message="Password must be at least 8 characters long."
            ),
            RegexValidator(
                regex=r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[A-Z]).{8,}$",
                message="Password must contain at least one uppercase letter, one lowercase letter, and one number.",
            ),
        ],
    )

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "role",
            "password",
            "user_type",
        ]

    def update(self, instance, validated_data):
        # If a new password is provided, set it
        password = validated_data.pop("password", None)
        if password:
            instance.set_password(password)  # Set the new password
        return super().update(instance, validated_data)

    def validate_password(self, value):
        """Custom password validation"""
        if value:
            # Check if the password is not too common
            common_passwords = ["password", "123456", "qwerty", "letmein", "123456789"]
            if value.lower() in common_passwords:
                raise ValidationError(
                    "This password is too common, please choose a stronger one."
                )
        return value


# Custom validator for privileges
def validate_privileges(value):
    # Check if each privilege in the value list is a valid PrivilegeEnum value
    for privilege in value:
        if privilege not in PrivilegeEnum._value2member_map_:
            raise serializers.ValidationError(f"Invalid privilege: {privilege}")
    return value


class RoleSerializer(serializers.ModelSerializer):
    privileges = serializers.ListField(
        child=serializers.CharField(), validators=[validate_privileges]
    )

    class Meta:
        model = UserRole
        fields = "__all__"


class UserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGroup
        fields = "__all__"


class UserUploadFileSerializer(serializers.Serializer):
    file = serializers.FileField()


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ["slug", "name"]


class UserRoleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = ["id", "name", "code", "alias"]


class CreateUserSerializer(serializers.ModelSerializer):
    role_id = serializers.PrimaryKeyRelatedField(source="role", queryset=UserRole.objects.all(), write_only=True)
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all()
    )
    gender = serializers.ChoiceField(choices=GenderType.choices, write_only=True)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "role_id",
            "organization",
            "gender",
        ]

    def create(self, validated_data):
        validated_data.setdefault("is_active", True)
        return super().create(validated_data)
    
    def create(self, validated_data):
        
        validated_data.setdefault("is_active", True)
        user = super().create(validated_data)

        token = RefreshToken.for_user(user).access_token

        current_site = config("FRONTEND_URL")
        relative_link = "auth/verify-email/"
        absurl = f"{current_site}{relative_link}{str(token)}"

        email_body = (
            f"Hi {user.first_name},\n\n"
            f"Use the link below to verify your email:\n{absurl}"
        )
        data = {
            "email_body": email_body,
            "to_email": user.email,
            "email_subject": "Verify your email",
        }

        Util.send_email(data)

        return user

class UserSuspendSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "is_active"]
        read_only_fields = ["id"]

    def update(self, instance, validated_data):
        instance.is_active = False
        instance.save()
        return instance
