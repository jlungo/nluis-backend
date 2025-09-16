from account.api.utils import Util
from decouple import config, Config, RepositoryEnv
from nluis.standard_result_pagination import StandardResultsSetPagination
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics
import jwt
from nluis.pagination import StandardResultsSetLimitOffset
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.http import Http404, HttpResponse, HttpResponsePermanentRedirect
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializer import *
from ..models import *
from django.db import transaction
from rest_framework import viewsets
import pandas as pd
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db.models import Q


class UserListView(generics.ListAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    pagination_class = StandardResultsSetPagination
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        keyword = self.request.query_params.get("keyword", "").strip()
        organization = self.request.query_params.get("organization", "").strip()
        role = self.request.query_params.get("role", "").strip()
        is_verified = self.request.query_params.get("is_verified", "").strip()

        users = User.objects.filter(is_active=True)

        if keyword:
            users = users.filter(
                Q(first_name__icontains=keyword)
                | Q(last_name__icontains=keyword)
                | Q(email__icontains=keyword)
                | Q(phone__icontains=keyword)
            )

        if organization:
            users = users.filter(
                Q(organization__id=organization)
                | Q(organization__name__icontains=organization)
                | Q(organization__short_name__icontains=organization)
            )

        if role:
            users = users.filter(
                Q(role__id=role) | Q(role__code__iexact=role) | Q(role__name__icontains=role)
            )

        if is_verified == "1":
            users = users.filter(is_verified=True)
        
        if is_verified == "0":
            users = users.filter(is_verified=False)

        return users


class UserUpdateView(generics.GenericAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, *args, **kwargs):
        user = self.get_object(self.kwargs.get("pk_user", ""))
        serializer = UserUpdateSerializer(user)

        return Response(serializer.data)

    def delete(self, request, pk_user, format=None):
        user = self.get_object(pk_user)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, *args, **kwargs):
        user = self.get_object(self.kwargs.get("pk_user", ""))
        serializer = self.serializer_class(user, data=request.data, partial=True)
        valid = serializer.is_valid(raise_exception=True)
        if valid:
            status_code = status.HTTP_200_OK
            serializer.save()
            return Response(serializer.data, status=status_code)


class UserLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]


class LogoutView(APIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = LogoutSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            refresh_token = serializer.validated_data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"detail": "Successfully logged out"}, status=status.HTTP_200_OK
            )

        except KeyError:
            return Response(
                {"detail": "Refresh token not provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except TokenError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response(
                {"detail": "An error occurred during logout"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# User Registration View
class UserRegistrationView(generics.GenericAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        with transaction.atomic():
            serializer = self.serializer_class(data=request.data)
            valid = serializer.is_valid(raise_exception=True)

            if valid:
                user = serializer.save()

                # Send email
                token = RefreshToken.for_user(user).access_token
                current_site = config("FRONTEND_URL")
                relative_link = "auth/verify-email/"
                absurl = current_site + relative_link + str(token)
                email_body = f"Hi {user.first_name}, Use the link below to verify your email \n{absurl}"
                data = {
                    "email_body": email_body,
                    "to_email": user.email,
                    "email_subject": "Verify your email",
                }
                Util.send_email(data)

                response = get_user_data(user)

                return Response(response, status=status.HTTP_201_CREATED)


class BulkUserUploadView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = (AllowAny,)
    serializer_class = UserUploadFileSerializer
    REQUIRED_COLUMNS = [
        "first_name",
        "last_name",
        "email",
        "gender",
        "role_code",
        "group_code",
    ]
    GENDER_MAP = {"M": GenderType.MALE, "F": GenderType.FEMALE}

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        file = serializer.validated_data["file"]
        if not file:
            return Response(
                {"error": "File is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            sheets = {}
            if file.name.endswith(".csv"):
                sheets["Sheet1"] = pd.read_csv(file)
            elif file.name.endswith(".xlsx"):
                xls = pd.read_excel(file, sheet_name=None)
                sheets = xls
            else:
                return Response(
                    {"error": "Unsupported file format. Use CSV or XLSX."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response(
                {"error": f"File read error: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        errors = []
        created = 0
        email_errors = []

        for sheet_name, df in sheets.items():
            missing_cols = [
                col for col in self.REQUIRED_COLUMNS if col not in df.columns
            ]
            if missing_cols:
                errors.append(
                    {
                        "sheet": sheet_name,
                        "row": None,
                        "error": f"Missing columns: {', '.join(missing_cols)}",
                    }
                )
                continue

            for index, row in df.iterrows():
                row_number = index + 2
                try:
                    email = str(row["email"]).strip().lower()

                    if User.objects.filter(email=email).exists():
                        raise ValidationError("User with this email already exists.")

                    gender = str(row["gender"]).strip().upper()
                    if gender not in self.GENDER_MAP:
                        raise ValidationError(
                            "Invalid gender. Use 'M' for Male or 'F' for Female."
                        )

                    role_code = str(row["role_code"]).strip()
                    if not UserRole.objects.filter(code=role_code).exists():
                        raise ValidationError(
                            f"Role with code '{role_code}' does not exist."
                        )

                    group_code = str(row["group_code"]).strip()
                    if not UserGroup.objects.filter(code=group_code).exists():
                        raise ValidationError(
                            f"Group with code '{group_code}' does not exist."
                        )

                    user = User.objects.create(
                        first_name=row["first_name"].strip(),
                        last_name=row["last_name"].strip(),
                        email=email,
                        gender=self.GENDER_MAP[gender],
                        role=UserRole.objects.get(code=role_code),
                        group=UserGroup.objects.get(code=group_code),
                    )

                    created += 1

                    # Send verification email (safely)
                    try:
                        token = RefreshToken.for_user(user).access_token
                        current_site = config("FRONTEND_URL")
                        absurl = f"{current_site}verify-email/{token}"
                        email_body = f"Hi {user.first_name},\nUse the link below to verify your email:\n{absurl}"
                        email_data = {
                            "email_body": email_body,
                            "to_email": user.email,
                            "email_subject": "Verify your email",
                        }
                        Util.send_email(email_data)
                    except Exception as e:
                        email_errors.append(
                            {
                                "email": user.email,
                                "error": f"Email send failed: {str(e)}",
                            }
                        )

                except ValidationError as ve:
                    errors.append(
                        {"sheet": sheet_name, "row": row_number, "error": str(ve)}
                    )
                except Exception as e:
                    errors.append(
                        {"sheet": sheet_name, "row": row_number, "error": str(e)}
                    )

        if errors:
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "message": f"Successfully created {created} users.",
                "email_failures": email_errors if email_errors else None,
            },
            status=status.HTTP_201_CREATED,
        )


class UserReSendAccountActivationEmailView(generics.GenericAPIView):
    serializer_class = ResendVerificationSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        user = request.data.get("user", "")
        # send email
        user = User.objects.get(id=user)
        serializer2 = UserRegisterSerializer(user)
        token = RefreshToken.for_user(user).access_token
        current_site = config("FRONTEND_URL")
        relativeLink = "verify-email/"
        absurl = current_site + relativeLink + str(token)
        email_body = (
            "Hi "
            + user.first_name
            + " Use the link below to verify your email \n"
            + absurl
        )
        data = {
            "email_body": email_body,
            "to_email": user.email,
            "email_subject": "Verify your email",
        }
        response = {
            "success": True,
            "statusCode": status.HTTP_201_CREATED,
            "message": "Email successfully resent!",
            "user": serializer.data,
        }

        Util.send_email(data)

        return Response(response, status=status.HTTP_201_CREATED)


# Email Verification  View
class VerifyEmailView(generics.GenericAPIView):
    serializer_class = EmailVerificationSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        valid = serializer.is_valid(raise_exception=True)
        if valid:
            token = serializer.data["token"]

            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")
                user = User.objects.get(id=payload["user_id"])
                if not user.is_verified or not user.is_active:
                    user.is_verified = True
                    user.is_active = True
                    user.login_attempt = 0
                    user.save()
                serializer = UserRegisterSerializer(user)
                data = {}
                data["message"] = "Successfully activated"
                data["uid64"] = urlsafe_base64_encode(smart_bytes(user.id))
                data["token"] = PasswordResetTokenGenerator().make_token(user)
                data["email"] = user.email

                return Response(data, status=status.HTTP_200_OK)
            except jwt.ExpiredSignatureError:
                return Response(
                    {"error": "Activation Expired"}, status=status.HTTP_400_BAD_REQUEST
                )
            except jwt.exceptions.DecodeError:
                return Response(
                    {"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
                )


class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        email = request.data.get("email", "")

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)

            absurl = config("FRONTEND_URL") + f"auth/reset-password/{uidb64}/{token}"
            email_body = "Hello, \n Use link below to reset your password  \n" + absurl
            data = {
                "email_body": email_body,
                "to_email": user.email,
                "email_subject": "Reset your passsword",
            }
            Util.send_email(data)
            return Response(
                {"success": "We have sent you a link to reset your password"},
                status=status.HTTP_200_OK,
            )
        else:
            raise Http404


class CustomRedirect(HttpResponsePermanentRedirect):
    pass

    # allowed_schemes = [os.environ.get('APP_SCHEME'), 'http', 'https']


class PasswordTokenCheckAPI(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    permission_classes = (AllowAny,)

    def get(self, request, uidb64, token):

        redirect_url = request.GET.get("redirect_url")

        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if PasswordResetTokenGenerator().check_token(user, token):
                return Response(
                    {
                        "success": True,
                        "message": "Credentials valid",
                        "uid64": uidb64,
                        "token": token,
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"error": "Token is not valid, please request a new one"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except DjangoUnicodeDecodeError as identifier:
            return Response(
                {"error": "Token is not valid, please request a new one"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    permission_classes = (AllowAny,)

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {"success": True, "message": "Password reset success"},
            status=status.HTTP_200_OK,
        )


class RoleViewSet(viewsets.ModelViewSet):
    queryset = UserRole.objects.all()
    serializer_class = RoleSerializer
    pagination_class = StandardResultsSetPagination


class UserGroupViewSet(viewsets.ModelViewSet):
    queryset = UserGroup.objects.all()
    serializer_class = UserGroupSerializer
    pagination_class = StandardResultsSetPagination


class UserPermissionView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, module_slug):
        user = request.user

        if not user.role:
            return Response(
                {"error": "User has no role assigned"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            module = Module.objects.get(slug=module_slug)

            role_permissions = UserRolePermission.objects.filter(
                user_role=user.role, module=module
            )

            all_permissions = []
            for role_permission in role_permissions:
                group = role_permission.group

                group_permissions = group.permissions.all()
                for permission in group_permissions:
                    all_permissions.append(
                        {
                            "id": permission.id,
                            "name": permission.name,
                            "codename": permission.codename,
                        }
                    )

            return Response(
                {
                    "module_slug": module_slug,
                    "permissions": all_permissions,
                    "permission_count": len(all_permissions),
                },
                status=status.HTTP_200_OK,
            )

        except Module.DoesNotExist:
            return Response(
                {
                    "error": f"Module with slug '{module_slug}' not found",
                    "module_slug": module_slug,
                    "permissions": [],
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": f"Error fetching permissions: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ModuleListView(generics.ListAPIView):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


class UserRoleListView(generics.ListAPIView):
    queryset = UserRole.objects.all().order_by("name")
    serializer_class = UserRoleListSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


class CreateUserView(generics.CreateAPIView):
    serializer_class = CreateUserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


class UserSuspendView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSuspendSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

