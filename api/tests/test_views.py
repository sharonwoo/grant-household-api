
from api.models import Household, FamilyMember
import pytest


def test_an_admin_view(admin_client):  # django admin test
    response = admin_client.get('/admin/')
    assert response.status_code == 200


"""
basic tests to check if invalid objects are not accepted.
"""


@pytest.mark.django_db
def test_add_household_invalid_json(admin_client):
    households = Household.objects.all()
    old_household_len = len(households)

    resp = admin_client.post(
        "/api/v1/households/",
        {},
        content_type="application/json"
    )
    assert resp.status_code == 400

    households = Household.objects.all()
    assert len(households) == old_household_len


@pytest.mark.django_db
def test_add_family_member_invalid_json(admin_client):
    family_members = FamilyMember.objects.all()
    old_family_members_len = len(family_members)

    resp = admin_client.post(
        "/api/v1/family_members/",
        {},
        content_type="application/json"
    )
    assert resp.status_code == 400

    family_members = FamilyMember.objects.all()
    assert len(family_members) == old_family_members_len


"""
grant list
    test cases:
    1. Student Encouragement Bonus: age <16, income <150,000
    2. Family Togetherness Scheme: husband & wife, age < 18
        n.b. marriages not allowed if less than 21 in our api
    3. Elder Bonus: age > 50
    4. Baby Sunshine Grant: age < 5
    5. YOLO GST Grant: income < 100,000
"""


def test_baby_sunshine_bonus(admin_client):

    rich_household = Household(housing_type="HDB")
    rich_household.save()
    poorer_household = Household(housing_type="Landed")
    poorer_household.save()
    poor_household = Household(housing_type="Landed")
    poor_household.save()

    baby_1 = admin_client.post(
        "/api/v1/family_members/",
        {'household': str(rich_household.uuid),
         'name': "Baby 1",
         'gender': "Male",
         'marital_status': "Single",
         'spouse': None,
         'occupation_type': "Unemployed",
         'annual_income': 0,
         'date_of_birth': "2022-06-02"},
        content_type="application/json"
    )
    random_2 = admin_client.post(
        "/api/v1/family_members/",
        {'household': str(poor_household.uuid),
         'name': "Random 2",
         'gender': "Male",
         'marital_status': "Single",
         'spouse': None,
         'occupation_type': "Unemployed",
         'annual_income': 0,
         'date_of_birth': "1987-06-02"},
        content_type="application/json"
    )
    resp = admin_client.get(
        "/api/v1/grants/?age_less_than=5")

    assert resp.data[0]['uuid'] == str(rich_household.uuid)


def test_elder_bonus(admin_client):

    rich_household = Household(housing_type="HDB")
    rich_household.save()
    poorer_household = Household(housing_type="Landed")
    poorer_household.save()
    poor_household = Household(housing_type="Landed")
    poor_household.save()

    old_person_1 = admin_client.post(
        "/api/v1/family_members/",
        {'household': str(rich_household.uuid),
         'name': "Old Person 1",
         'gender': "Male",
         'marital_status': "Single",
         'spouse': None,
         'occupation_type': "Unemployed",
         'annual_income': 0,
         'date_of_birth': "1922-06-02"},
        content_type="application/json"
    )
    random_2 = admin_client.post(
        "/api/v1/family_members/",
        {'household': str(poor_household.uuid),
         'name': "Random 2",
         'gender': "Male",
         'marital_status': "Single",
         'spouse': None,
         'occupation_type': "Unemployed",
         'annual_income': 0,
         'date_of_birth': "1987-06-02"},
        content_type="application/json"
    )
    resp = admin_client.get(
        "/api/v1/grants/?age_more_than=50")

    assert resp.data[0]['uuid'] == str(rich_household.uuid)


def test_yolo_gst_grant(admin_client):

    rich_household = Household(housing_type="HDB")
    rich_household.save()
    poorer_household = Household(housing_type="Landed")
    poorer_household.save()
    poor_household = Household(housing_type="Landed")
    poor_household.save()

    rich_person_1 = admin_client.post(
        "/api/v1/family_members/",
        {'household': str(rich_household.uuid),
         'name': "Old Person 1",
         'gender': "Male",
         'marital_status': "Single",
         'spouse': None,
         'occupation_type': "Unemployed",
         'annual_income': 10000000,
         'date_of_birth': "1922-06-02"},
        content_type="application/json"
    )
    poor_person_2 = admin_client.post(
        "/api/v1/family_members/",
        {'household': str(poor_household.uuid),
         'name': "Random 2",
         'gender': "Male",
         'marital_status': "Single",
         'spouse': None,
         'occupation_type': "Unemployed",
         'annual_income': 1000,
         'date_of_birth': "1922-06-02"},
        content_type="application/json"
    )
    poor_person_3 = admin_client.post(
        "/api/v1/family_members/",
        {'household': str(poorer_household.uuid),
         'name': "Random 2",
         'gender': "Male",
         'marital_status': "Single",
         'spouse': None,
         'occupation_type': "Unemployed",
         'annual_income': 10000,
         'date_of_birth': "1987-06-02"},
        content_type="application/json"
    )
    poor_person_4 = admin_client.post(
        "/api/v1/family_members/",
        {'household': str(poorer_household.uuid),
         'name': "Random 2",
         'gender': "Male",
         'marital_status': "Single",
         'spouse': None,
         'occupation_type': "Unemployed",
         'annual_income': 10000,
         'date_of_birth': "1987-06-02"},
        content_type="application/json"
    )
    resp = admin_client.get(
        "/api/v1/grants/?household_income=100000")

    assert set([resp.data[0]['uuid'], resp.data[1]['uuid']]) == set(
        [str(poorer_household.uuid), str(poor_household.uuid)])


def test_student_encouragement_bonus_grant(admin_client):

    rich_household = Household(housing_type="HDB")
    rich_household.save()
    poorer_household = Household(housing_type="Landed")
    poorer_household.save()
    poor_household = Household(housing_type="Landed")
    poor_household.save()

    rich_person_1 = admin_client.post(
        "/api/v1/family_members/",
        {'household': str(rich_household.uuid),
         'name': "Old Person 1",
         'gender': "Male",
         'marital_status': "Single",
         'spouse': None,
         'occupation_type': "Unemployed",
         'annual_income': 10000000,
         'date_of_birth': "1922-06-02"},
        content_type="application/json"
    )
    poor_student = admin_client.post(
        "/api/v1/family_members/",
        {'household': str(poor_household.uuid),
         'name': "Random 2",
         'gender': "Male",
         'marital_status': "Single",
         'spouse': None,
         'occupation_type': "Student",
         'annual_income': 1000,
         'date_of_birth': "2010-06-02"},
        content_type="application/json"
    )
    poor_parent = admin_client.post(
        "/api/v1/family_members/",
        {'household': str(poor_household.uuid),
         'name': "Random 3",
         'gender': "Male",
         'marital_status': "Single",
         'spouse': None,
         'occupation_type': "Employed",
         'annual_income': 25000,
         'date_of_birth': "1986-06-02"},
        content_type="application/json"
    )
    poor_person_3 = admin_client.post(
        "/api/v1/family_members/",
        {'household': str(poorer_household.uuid),
         'name': "Random 2",
         'gender': "Male",
         'marital_status': "Single",
         'spouse': None,
         'occupation_type': "Unemployed",
         'annual_income': 10000,
         'date_of_birth': "1987-06-02"},
        content_type="application/json"
    )
    resp = admin_client.get(
        "/api/v1/grants/?household_income=100000&age_less_than=16")

    assert len(resp.data) == 1
    assert resp.data[0]['uuid'] == str(poor_household.uuid)
    assert len(resp.data[0]['family_members']) == 1
    assert resp.data[0]['family_members'][0]['uuid'] == poor_student.data['uuid']


def test_student_encouragement_bonus_grant(admin_client):

    rich_household = Household(housing_type="HDB")
    rich_household.save()
    poorer_household = Household(housing_type="Landed")
    poorer_household.save()
    poor_household = Household(housing_type="Landed")
    poor_household.save()

    male_married = FamilyMember(household=rich_household,
                                name="marriage 1",
                                gender="Male",
                                marital_status="Single",
                                spouse=None,
                                occupation_type="Unemployed",
                                annual_income=1000000,
                                date_of_birth="1987-06-02"
                                )
    male_married.save()

    female_married = FamilyMember(household=rich_household,
                                  name="marriage 2",
                                  gender="Female",
                                  marital_status="Single",
                                  spouse=male_married,
                                  occupation_type="Employed",
                                  annual_income=1000000,
                                  date_of_birth="1987-06-02"
                                  )
    female_married.save()

    baby = FamilyMember(household=rich_household,
                        name="baby 1",
                        gender="Female",
                        marital_status="Single",
                        spouse=None,
                        occupation_type="Unemployed",
                        annual_income=0,
                        date_of_birth="2021-06-02"
                        )
    baby.save()

    male_married_2 = FamilyMember(household=poor_household,
                                  name="marriage 1",
                                  gender="Male",
                                  marital_status="Single",
                                  spouse=None,
                                  occupation_type="Unemployed",
                                  annual_income=0,
                                  date_of_birth="1987-06-02"
                                  )
    male_married_2.save()

    female_married_2 = FamilyMember(household=poor_household,
                                    name="marriage 2",
                                    gender="Female",
                                    marital_status="Single",
                                    spouse=male_married_2,
                                    occupation_type="Unemployed",
                                    annual_income=0,
                                    date_of_birth="1987-06-02"
                                    )
    female_married_2.save()

    resp = admin_client.get(
        "/api/v1/grants/?married=1&age_less_than=5")

    assert len(resp.data) == 1
    assert resp.data[0]['uuid'] == str(rich_household.uuid)
    assert len(resp.data[0]['family_members']) == 3
