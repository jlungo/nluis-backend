from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, ValidationError):
        # Keep the original field-specific error structure
        response_data = {'errors': exc.detail}
        response = Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    return response


class CustomValidationError(ValidationError):
    pass


