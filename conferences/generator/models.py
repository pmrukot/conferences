# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desidered behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class Companies(models.Model):
    name = models.CharField(max_length=255)
    nip = models.CharField(db_column='NIP', unique=True, max_length=9, blank=True, null=True)  # Field name made lowercase.
    city = models.CharField(max_length=120)
    phone = models.CharField(max_length=14)
    country = models.CharField(max_length=2)
    email = models.CharField(unique=True, max_length=255)
    password = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'companies'


class CompaniesBookings(models.Model):
    company = models.ForeignKey(Companies, models.DO_NOTHING)
    conference_day = models.ForeignKey('ConferenceDays', models.DO_NOTHING)
    students_count = models.IntegerField()
    non_students_count = models.IntegerField()
    created = models.DateTimeField(blank=True, null=True)
    modified = models.DateTimeField(blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=0)
    is_canceled = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'companies_bookings'


class CompaniesWorkshopBookings(models.Model):
    booking = models.ForeignKey(CompaniesBookings, models.DO_NOTHING)
    workshop = models.ForeignKey('Workshops', models.DO_NOTHING)
    attenders_count = models.IntegerField()
    created = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'companies_workshop_bookings'
        unique_together = (('booking', 'workshop'),)


class CompanyAttenders(models.Model):
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    company = models.ForeignKey(Companies, models.DO_NOTHING, blank=True, null=True)
    email = models.CharField(unique=True, max_length=255)
    password = models.CharField(max_length=255)
    student_card_number = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'company_attenders'


class CompanyBookingLists(models.Model):
    attender = models.ForeignKey(CompanyAttenders, models.DO_NOTHING)
    booking = models.ForeignKey(CompaniesBookings, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'company_booking_lists'


class CompanyBookingPayins(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=0)
    datetime = models.DateTimeField()
    booking = models.ForeignKey(CompaniesBookings, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'company_booking_payins'


class ConferenceDays(models.Model):
    conference = models.ForeignKey('Conferences', models.DO_NOTHING)
    day = models.DateField()
    participants_limit = models.IntegerField(blank=True, null=True)
    is_canceled = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'conference_days'


class Conferences(models.Model):
    name = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'conferences'


class People(models.Model):
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    pesel = models.CharField(db_column='PESEL', unique=True, max_length=11, blank=True, null=True)  # Field name made lowercase.
    city = models.CharField(max_length=120)
    country = models.CharField(max_length=2)
    email = models.CharField(unique=True, max_length=255)
    password = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    student_card_number = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'people'


class PeopleBookingPayins(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=0)
    datetime = models.DateTimeField()
    booking = models.ForeignKey('PeopleBookings', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'people_booking_payins'


class PeopleBookings(models.Model):
    person = models.ForeignKey(People, models.DO_NOTHING)
    conference_day = models.ForeignKey(ConferenceDays, models.DO_NOTHING)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    is_canceled = models.BooleanField()
    due_date = models.DateTimeField()
    created = models.DateTimeField(blank=True, null=True)
    modified = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'people_bookings'


class PriceLevels(models.Model):
    price = models.DecimalField(max_digits=10, decimal_places=0)
    start_date = models.DateField()
    end_date = models.DateField()
    conference = models.ForeignKey(Conferences, models.DO_NOTHING)
    student_discount = models.DecimalField(max_digits=10, decimal_places=0)

    class Meta:
        managed = False
        db_table = 'price_levels'


class WorkshopPeople(models.Model):
    person = models.ForeignKey(People, models.DO_NOTHING)
    workshop = models.ForeignKey('Workshops', models.DO_NOTHING)
    booking = models.ForeignKey(PeopleBookings, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'workshop_people'


class Workshops(models.Model):
    conference_day = models.ForeignKey(ConferenceDays, models.DO_NOTHING)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    participants_limit = models.IntegerField(blank=True, null=True)
    start = models.TimeField()
    end = models.TimeField()

    class Meta:
        managed = False
        db_table = 'workshops'


class WorkshopsCompanyAttenders(models.Model):
    workshop = models.ForeignKey(Workshops, models.DO_NOTHING)
    attender = models.ForeignKey(CompanyAttenders, models.DO_NOTHING)
    workshop_booking = models.ForeignKey(CompaniesWorkshopBookings, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'workshops_company_attenders'
