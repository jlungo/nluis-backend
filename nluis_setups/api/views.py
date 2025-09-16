from django.shortcuts import render

# Create your views here.
from rest_framework import generics

from nluis_setups.api.serializers import *
from nluis_setups.models import IdentityType, DocumentType, OccupancyType, PartyRole, LandUse, Funder, Currency


class IdentityTypeListView(generics.ListAPIView):
    serializer_class = IdentityTypeListSerializer
    queryset = IdentityType.objects.all()


class DocumentTypeListView(generics.ListAPIView):
    serializer_class = DocumentTypeListSerializer
    queryset = DocumentType.objects.all()


class OccupancyTypeListView(generics.ListAPIView):
    serializer_class = OccupancyTypeListSerializer
    queryset = OccupancyType.objects.all()


class PartyRoleListView(generics.ListAPIView):
    serializer_class = PartyRoleListSerializer
    queryset = PartyRole.objects.all()


class LandUseListView(generics.ListAPIView):
    serializer_class = LandUseListSerializer
    queryset = LandUse.objects.all()


class FunderListView(generics.ListAPIView):
    serializer_class = FunderListSerializer
    queryset = Funder.objects.all()


# for funders create via frontend
class FunderCreateView(generics.CreateAPIView):
    serializer_class = FunderListSerializer
    queryset = Funder.objects.all()
    
    def create(self, request, *args, **kwargs):
        name = request.data.get('name')
        if name:
            # Check if funder with same name already exists
            if Funder.objects.filter(name=name).exists():
                from rest_framework.response import Response
                from rest_framework import status
                return Response(
                    {'error': f'Funder with name "{name}" already exists.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return super().create(request, *args, **kwargs)
    

class CurrencyListView(generics.ListAPIView):
    serializer_class = CurrencySerializer
    queryset = Currency.objects.all()
