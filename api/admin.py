from django.contrib import admin
from .models import Household, FamilyMember

"""
Create records from 127.0.0.1:8000/admin with superuser for testing of spouse CRUD
"""
admin.site.register(Household)
admin.site.register(FamilyMember)
