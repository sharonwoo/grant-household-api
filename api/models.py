from django.db import models
from django.core.validators import MaxValueValidator
from django.db.models.functions import Now
from rest_framework.exceptions import ValidationError


from datetime import date, timedelta
import uuid


class Household(models.Model):

    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)

    class HousingType(models.TextChoices):
        condo = "Condominium", "Condominium"
        hdb = "HDB", "HDB"
        landed = "Landed", "Landed"

    housing_type = models.CharField(
        max_length=11, choices=HousingType.choices)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            "Household UUID: %s, Housing Type: %s" % (
                str(self.uuid), self.get_housing_type_display())
        )


class FamilyMember(models.Model):

    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)

    household = models.ForeignKey(
        Household, on_delete=models.CASCADE, related_name="family_members")

    name = models.CharField(max_length=100)

    class Gender(models.TextChoices):
        male = "Male", "Male"
        female = "Female", "Female"

    gender = models.CharField(
        max_length=6, choices=Gender.choices)  # default=Gender.female)

    class MaritalStatus(models.TextChoices):
        married = "Married", "Married"
        single = "Single", "Single"

    marital_status = models.CharField(
        max_length=7, choices=MaritalStatus.choices)

    spouse = models.OneToOneField(
        "self", blank=True, null=True, on_delete=models.CASCADE)

    class OccupationType(models.TextChoices):
        unemployed = "Unemployed", "Unemployed"
        student = "Student", "Student"
        employed = "Employed", "Employed"

    occupation_type = models.CharField(
        max_length=10, choices=OccupationType.choices)

    """
    Annual income assumptions:
        - Cannot be less than 0: follows that household income lower bound is 0
    """
    annual_income = models.PositiveIntegerField()

    date_of_birth = models.DateField(
        validators=[MaxValueValidator(limit_value=date.today)]
    )

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    """
    Spouse and marital status assumptions:
        - If FamilyMember has spouse, marital_status must be "Married"
        - Spouses can live separately in different households
        - If FamilyMember's spouse is deleted (maybe they died?), marital_status should revert to "Single"
        - Only a pair of husband and wife can be Married. All else will result in a validation error if a relationship is attempted
        - Spouses can only get married if age >= 21
    """

    def clean(self, *args, **kwargs):
        if self.spouse:
            if self.gender != self.spouse.gender \
                    and self.date_of_birth <= (date.today() - timedelta(365.25 * 21)) \
                    and self.spouse.date_of_birth <= (date.today() - timedelta(365.25 * 21)):
                pass
            else:
                raise ValidationError(
                    ({"Invalid data": 'Marriage is not legal: only heterosexual unions for those above 21'}))
    """
    One to one relationships symmetrical with modified .save()
        - hack IN THE DOCS due to issue as old as time: https://code.djangoproject.com/ticket/7689
        - follows https://stackoverflow.com/questions/50355697/i-have-a-onetoone-relationship-between-two-objects-of-the-same-class-in-a-django
    """

    def save(self, *args, **kwargs):
        self.full_clean()  # calls clean
        if self.spouse:
            # allow the marriage if heterosexual and above 21
            if self.gender != self.spouse.gender \
                    and self.date_of_birth <= (date.today() - timedelta(365.25 * 21)) \
                    and self.spouse.date_of_birth <= (date.today() - timedelta(365.25 * 21)):
                self.spouse.spouse = self
                self.marital_status = "Married"
                self.spouse.marital_status = "Married"
                super(FamilyMember, self.spouse).save()
                super(FamilyMember, self).save()
            else:
                self.spouse = None
                self.marital_status = "Single"
                super(FamilyMember, self).save()
        # no spouse, so make marital status single
        else:
            self.marital_status = "Single"
            super(FamilyMember, self).save()

    def __str__(self):
        return "Name: %s, UUID: %s, Household: %s" % (self.name, str(self.uuid), str(self.household.uuid))

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(date_of_birth__lte=Now()),
                name='date_of_birth_cannot_be_future_dated'
            ),
        ]
