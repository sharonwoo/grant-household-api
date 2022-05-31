from django.shortcuts import render
from django.db.models import F, Sum, Prefetch


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


class GrantList(ListAPIView):
    serializer_class = HouseholdSerializer
    """
    test cases:
    1. Student Encouragement Bonus: age <16, income <150,000
    2. Family Togetherness Scheme: husband & wife, age < 18
        Q: if wife or husband < 18?
    3. Elder Bonus: age > 50
    4. Baby Sunshine Grant: age < 5
    5. YOLO GST Grant: income < 100,000

    Last updated: Family Togetherness Scheme
    """

    def get_queryset(self):
        household_income = self.request.query_params.get(
            "household_income", None)
        age_less_than = self.request.query_params.get("age_less_than", None)
        age_more_than = self.request.query_params.get("age_more_than", None)
        married = self.request.query_params.get("married", None)

        """
        Set if/else to use age_range to simplify permutation
        Note if this is None for both, age range filter will pass all values in database
        """
        if age_less_than:
            age_less_than = int(age_less_than)
        else:
            age_less_than = 200
        if age_more_than:
            age_more_than = int(age_more_than)
        else:
            age_more_than = 0

        if household_income:
            get_household_ids = (
                Household.objects.all()
                .annotate(house_income=Sum("familymember__annual_income"))
                .filter(house_income__lte=household_income)
            )

            household_ids = list(
                set(get_household_ids.values_list("pk", flat=True)))

            if married is None:
                """YOLO GST GRANT: return all household members (aged 0-200)
                Student Encouragement Bonus: return only students < 16
                other permutations not given in cases
                """
                family_member_filter = FamilyMember.objects.annotate(
                    age=(date.today() - F("date_of_birth"))
                ).filter(
                    age__range=[
                        timedelta(365.25 * age_more_than),
                        timedelta(365.25 * age_less_than),
                    ]
                )
                result = Household.objects.filter(
                    id__in=household_ids
                ).prefetch_related(
                    Prefetch("familymember", queryset=family_member_filter)
                )

            else:
                """Family Togetherness Scheme,
                other permutations not given in cases
                """
                family_member_filter = (
                    FamilyMember.objects.all()
                    .annotate(age=(date.today() - F("date_of_birth")))
                    .filter(
                        Q(
                            age__range=[
                                timedelta(365.25 * age_more_than),
                                timedelta(365.25 * age_less_than),
                            ]
                        )
                        | Q(household=F("spouse__household"))
                    )
                )
                result = Household.objects.filter(
                    id__in=household_ids
                ).prefetch_related(
                    Prefetch("familymember", queryset=family_member_filter)
                )

            return result.distinct()

        else:
            if married is None:
                """Baby Sunshine Grant"""
                family_member_filter = FamilyMember.objects.annotate(
                    age=(date.today() - F("date_of_birth"))
                ).filter(
                    age__range=[
                        timedelta(365.25 * age_more_than),
                        timedelta(365.25 * age_less_than),
                    ]
                )
                result = Household.objects.filter(
                    id__in=household_ids
                ).prefetch_related(
                    Prefetch("familymember", queryset=family_member_filter)
                )

            else:
                """Not in given grants"""
                family_member_filter = (
                    FamilyMember.objects.all()
                    .annotate(age=(date.today() - F("date_of_birth")))
                    .filter(
                        Q(
                            age__range=[
                                timedelta(365 * age_more_than),
                                timedelta(365 * age_less_than),
                            ]
                        )
                        | Q(household=F("spouse__household"))
                    )
                )
                result = Household.objects.prefetch_related(
                    Prefetch("familymember", queryset=family_member_filter)
                )

            return result.distinct()
