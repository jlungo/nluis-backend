from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.http import Http404

from nluis.standard_result_pagination import StandardResultsSetPagination
from .serializer import *
from .models import *
from rest_framework.response import Response
from rest_framework.views import APIView


class OrganizationNoPaginationView(generics.ListAPIView):
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]
    queryset = Organization.objects.all()


class OrganizationView(generics.ListCreateAPIView):
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    queryset = Organization.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        valid = serializer.is_valid(raise_exception=True)
        if valid:
            status_code = status.HTTP_201_CREATED
            serializer.save()
            return Response(serializer.data, status=status_code)

# Retrieve, update or delete a Organization instance.


class OrganizationUpdateView(generics.GenericAPIView):
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Organization.objects.get(pk=pk)
        except Organization.DoesNotExist:
            raise Http404

    def put(self, request, *args, **kwargs):
        organization_key = self.get_object(
            self.kwargs.get('pk_organization', ''))
        serializer = self.serializer_class(organization_key, data=request.data)
        valid = serializer.is_valid(raise_exception=True)

        if valid:
            status_code = status.HTTP_201_CREATED
            serializer.save()
            return Response(serializer.data, status=status_code)

    def get(self, request, *args, **kwargs):
        organization = self.get_object(self.kwargs.get('pk_organization', ''))
        serializer = OrganizationSerializer(organization)
        return Response(serializer.data)

    def delete(self, request, pk_organization, format=None):
        organization = self.get_object(pk_organization)
        organization.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
# organization type


class OrganizationTypeNoPaginationView(generics.ListAPIView):
    serializer_class = OrganizationTypeSerializer
    permission_classes = [IsAuthenticated]
    queryset = OrganizationType.objects.all()


class OrganizationTypeView(generics.ListCreateAPIView):
    serializer_class = OrganizationTypeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    queryset = OrganizationType.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        valid = serializer.is_valid(raise_exception=True)
        if valid:
            status_code = status.HTTP_201_CREATED
            serializer.save()
            return Response(serializer.data, status=status_code)

# Retrieve, update or delete a OrganizationType instance.


class OrganizationTypeUpdateView(generics.GenericAPIView):
    serializer_class = OrganizationTypeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return OrganizationType.objects.get(pk=pk)
        except OrganizationType.DoesNotExist:
            raise Http404

    def put(self, request, *args, **kwargs):
        type_key = self.get_object(self.kwargs.get('pk_type', ''))
        serializer = self.serializer_class(type_key, data=request.data)
        valid = serializer.is_valid(raise_exception=True)

        if valid:
            status_code = status.HTTP_201_CREATED
            serializer.save()
            return Response(serializer.data, status=status_code)

    def get(self, request, *args, **kwargs):
        type = self.get_object(self.kwargs.get('pk_type', ''))
        serializer = OrganizationTypeSerializer(type)
        return Response(serializer.data)

    def delete(self, request, pk_type, format=None):
        type = self.get_object(pk_type)
        type.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
