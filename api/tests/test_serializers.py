from api.models import Household, FamilyMember

from api.serializers import HouseholdSerializer, FamilyMemberSerializer

"""
TODO: https://stackoverflow.com/questions/71692387/trying-to-test-a-nested-serilailzer-how-to-create-required-subfactories
"""


def test_valid_household_serializer():
    valid_serializer_data = {
        "housing_type": "Landed",
    }
    serializer = HouseholdSerializer(data=valid_serializer_data)
    assert serializer.is_valid()
    assert serializer.validated_data == valid_serializer_data
    assert serializer.data == valid_serializer_data
    assert serializer.errors == {}


def test_invalid_household_serializer():
    invalid_serializer_data = {
        "housing_type": "",
    }
    serializer = HouseholdSerializer(data=invalid_serializer_data)
    assert not serializer.is_valid()
    assert serializer.validated_data == {}
    assert serializer.data == invalid_serializer_data
