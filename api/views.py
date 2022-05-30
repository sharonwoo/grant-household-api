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

    """
    Modified destroy method so DELETE does not take out both paired spouses. 
    """

    def destroy(self, request, *args, **kwargs):
        familymember = self.get_object()
        spouse = familymember.spouse
        if spouse is not None:
            spouse.spouse = None
            spouse.marital_status = "Single"
            spouse.save()
        familymember.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


"""
TODO - GrantList API - aliases to "api/v1/grants/"
Use ListViewAPI
Need timedelta and date for date queries
Need F, Sum for date and household income queries 
Develop and testing queries in Django shell 
"""
