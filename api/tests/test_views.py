from django.urls import reverse
from api.models import Household, FamilyMember
import base64
import pytest


def test_base64():  # check if pytest is working as expected

    given = "49276d206b696c6c696e6720796f757220627261696e206c696b65206120706f69736f6e6f7573206d757368726f6f6d"
    expected = b"SSdtIGtpbGxpbmcgeW91ciBicmFpbiBsaWtlIGEgcG9pc29ub3VzIG11c2hyb29t"
    assert base64.b64encode(bytes.fromhex(given)) == expected


"""
basic tests to check if invalid objects are not accepted. 
"""


@pytest.mark.django_db
def test_add_household_invalid_json(client):
    households = Household.objects.all()
    old_household_len = len(households)

    resp = client.post(
        "/api/v1/households/",
        {},
        content_type="application/json"
    )
    assert resp.status_code == 400

    households = Household.objects.all()
    assert len(households) == old_household_len


@pytest.mark.django_db
def test_add_family_member_invalid_json(client):
    family_members = FamilyMember.objects.all()
    old_family_members_len = len(family_members)

    resp = client.post(
        "/api/v1/family_members/",
        {},
        content_type="application/json"
    )
    assert resp.status_code == 400

    family_members = FamilyMember.objects.all()
    assert len(family_members) == old_family_members_len


"""
basic model tests
"""


@pytest.mark.django_db
def test_household_model():
    household = Household(housing_type="HDB")
    household.save()
    assert household.housing_type == "HDB"
    assert household.uuid
    assert household.created_date
    assert household.updated_date
    assert household.family_members


@pytest.mark.django_db
def test_family_member_model():
    # household = Household(housing_type="HDB")
    # household.save()

    family_member = FamilyMember(household="9f5609e5-ce08-4107-9750-71a704607861",
                                 name="pytest person 1",
                                 gender="Male",
                                 marital_status="Single",
                                 spouse=None,
                                 occupation_type="Unemployed",
                                 annual_income=0,
                                 date_of_birth="1987-06-02"
                                 )
    family_member.save()

    assert family_member.uuid
    assert family_member.created_date
    assert family_member.updated_date
    assert family_member.name == "pytest person 1"
