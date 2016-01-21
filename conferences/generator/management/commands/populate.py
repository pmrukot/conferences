from datetime import timedelta
import random
from django.core.management.base import BaseCommand
from django.db.models import Min, Max
from generator.factories import PeopleFactory, CompaniesFactory, ConferencesFactory, PeopleBookingsFactory, \
    CompaniesBookingsFactory, CompanyAttendersFactory
from generator.models import People, Conferences, Companies, CompaniesBookings, CompanyAttenders, CompanyBookingLists, \
    CompaniesWorkshopBookings, WorkshopsCompanyAttenders, Workshops


class Command(BaseCommand):
    def _generate_conferences_participants(self, conferences):
        for conference in conferences:
            people = People.objects.exclude(peoplebookings__conference_day__conference=conference)
            days = conference.conferencedays_set.all()
            days_count = len(days)
            days_limits = {day.pk: random.choice(range(day.participants_limit/3, day.participants_limit/2)) for day in days}
            days_participants = {day.pk: day.peoplebookings_set.count() for day in days}
            publish_date = conference.pricelevels_set.all().aggregate(Min('start_date')).get('start_date__min')
            publish_date_diff = (conference.start_date - publish_date).days

            for person in people:
                sample_days = random.sample(days, random.choice(range(1, days_count+1)))
                for day in sample_days:
                    if days_participants[day.pk] >= days_limits[day.pk]:
                        continue

                    PeopleBookingsFactory(
                        person=person,
                        conference_day=day,
                        created=publish_date + timedelta(days=random.choice(range(publish_date_diff-7)))
                    )
                    days_participants[day.pk] += 1

            companies = Companies.objects.exclude(companiesbookings__conference_day__conference=conference)
            for company in companies:
                try:
                    sample_days = random.sample(days, random.choice(range(1, days_count+1)))
                    for day in sample_days:
                        try:
                            CompaniesBookingsFactory(
                                company=company,
                                conference_day=day,
                                created=publish_date + timedelta(days=random.choice(range(publish_date_diff-7)))
                            )
                        except Exception as e:
                            print 'CompaniesBookingFactory failed'
                except IndexError as e:
                    raise e

        for conference in conferences:
            companies = Companies.objects.filter(companiesbookings__conference_day__conference=conference)
            for company in companies:
                members_count = company.companiesbookings_set.filter(conference_day__conference=conference).\
                    aggregate(Max('non_students_count'), Max('students_count'))
                students_count, non_students_count = members_count['students_count__max'], members_count['non_students_count__max']

                for _ in range(students_count):
                    CompanyAttendersFactory(
                        company=company,
                        student_card_number=''.join(random.choice('123456789') for _ in range(6))
                    )

                for _ in range(non_students_count):
                    CompanyAttendersFactory(
                        company=company
                    )

    def _generate_companies_bookings_lists(self):
        bookings = CompaniesBookings.objects.all()
        for booking in bookings:
            non_student_queryset = CompanyAttenders.objects.filter(company=booking.company, student_card_number__isnull=True)
            student_queryset = CompanyAttenders.objects.filter(company=booking.company, student_card_number__isnull=False)

            non_student_people = random.sample(non_student_queryset, booking.non_students_count)
            students = random.sample(student_queryset, booking.students_count)

            for student in students:
                CompanyBookingLists.objects.create(
                    attender=student,
                    booking=booking
                )

            for person in non_student_people:
                CompanyBookingLists.objects.create(
                    attender=person,
                    booking=booking
                )

    def _generate_workshop_company_attenders(self):
        companies = Companies.objects.all()
        for company in companies:
            workshops = Workshops.objects.filter(companiesworkshopbookings__booking__company=company)
            attenders_queryset = CompanyAttenders.objects.filter(company=company)
            for workshop in workshops:
                workshop_bookings = workshop.companiesworkshopbookings_set.filter(booking__company=company)
                attenders = random.sample(attenders_queryset, len(workshop_bookings))

                for booking, attender in zip(workshop_bookings, attenders):
                    WorkshopsCompanyAttenders.objects.create(
                        workshop_booking=booking,
                        workshop=workshop,
                        attender=attender
                    )


    def handle(self, *args, **options):
        conferences = ConferencesFactory.create_batch(72)
        people = PeopleFactory.create_batch(1540)
        companies = CompaniesFactory.create_batch(60)

        self._generate_conferences_participants(conferences)
        self._generate_companies_bookings_lists()
        self._generate_workshop_company_attenders()

