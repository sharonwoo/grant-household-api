from django.shortcuts import render
from django.db.models import OuterRef, Subquery, DateTimeField, F, Sum


from .models import Household, FamilyMember
from .serializers import HouseholdSerializer, FamilyMemberSerializer

from datetime import date, timedelta

# rest_framework imports
from rest_framework import serializers, viewsets
from rest_framework.generics import ListAPIView


class HouseholdViewSet(viewsets.ModelViewSet):
    serializer_class = HouseholdSerializer
    queryset = Household.objects.all()


class FamilyMemberViewSet(viewsets.ModelViewSet):
    serializer_class = FamilyMemberSerializer
    queryset = FamilyMember.objects.all()
