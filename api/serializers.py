from rest_framework import serializers
from .models import Household, FamilyMember


class FamilyMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyMember
        fields = [
            "uuid",
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
    family_members = FamilyMemberSerializer(many=True, read_only=True)

    class Meta:
        model = Household
        fields = [
            "uuid",
            "housing_type",
            "family_members",
        ]
