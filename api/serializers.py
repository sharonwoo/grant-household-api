from rest_framework import serializers
from .models import Household, FamilyMember


class FamilyMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyMember
        fields = [
            "id",
            "household",
            "name",
            "gender",
            "marital_status",
            "spouse",
            "occupation_type",
            "annual_income",
            "date_of_birth",
        ]


class HouseholdSerializer(serializers.ModelSerializer):
    familymembers = FamilyMemberSerializer(many=True, read_only=True)

    class Meta:
        model = Household
        fields = [
            "id",
            "housing_type",
            "familymembers",
        ]
