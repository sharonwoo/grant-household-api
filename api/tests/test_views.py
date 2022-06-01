from django.urls import reverse
from api.models import Household, FamilyMember
import base64
import pytest


def test_base64():
    given = "49276d206b696c6c696e6720796f757220627261696e206c696b65206120706f69736f6e6f7573206d757368726f6f6d"
    expected = b"SSdtIGtpbGxpbmcgeW91ciBicmFpbiBsaWtlIGEgcG9pc29ub3VzIG11c2hyb29t"
    assert base64.b64encode(bytes.fromhex(given)) == expected


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
    family_members = Household.objects.all()
    old_family_members_len = len(family_members)

    resp = client.post(
        "/api/v1/family_members/",
        {},
        content_type="application/json"
    )
    assert resp.status_code == 400

    family_members = Household.objects.all()
    assert len(family_members) == old_family_members_len
