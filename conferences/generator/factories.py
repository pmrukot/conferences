# -*- coding: utf-8 *-*
from collections import defaultdict
from datetime import datetime, timedelta, time
import random
import hashlib

from dateutil.relativedelta import relativedelta
import factory
from factory.fuzzy import FuzzyDate, FuzzyChoice, FuzzyInteger
from faker import Factory as FakerFactory

from utils.date import daterange
from generator.models import People, Companies, Conferences, ConferenceDays, PriceLevels, Workshops, PeopleBookings, \
    PeopleBookingPayins, WorkshopPeople, CompaniesBookings, CompanyBookingPayins, CompaniesWorkshopBookings, \
    CompanyAttenders
from generator.utils.pesel import PeselGen

CONFERENCE_NAMES = ('Konferencja PyCon', 'Ekonomiczne i prawne wyzwania roku', u'Konferencja Szkoleniowa dla Doktoranów',
                    u'Nowoczesne zarządzanie przedsiębiorstwem', 'Marketing internetowy i e-biznes', 'Badania innowacje',
                    'Machine learning w praktyce', u'Data Science na przykładach',)


faker = FakerFactory.create('pl_PL')


class PeselGenerator(object):
    def __init__(self):
        self.generator = PeselGen()
        self.generated_values = set()

    def __call__(self, x):
        number = self.generator.return_pesel()
        while number in self.generated_values:
            number = self.generator.return_pesel()
        self.generated_values.add(number)
        return number


class UniqueEmailGenerator(object):
    def __init__(self):
        self.generated_emails = set()

    def __call__(self, x):
        email = ''
        is_unique = False
        while not is_unique:
            email = self.generate_value()
            is_unique = email not in self.generated_emails
        self.generated_emails.add(email)
        return email

    def generate_value(self):
        return faker.free_email()


class UniqueCompanyEmailGenerator(UniqueEmailGenerator):
    def generate_value(self):
        return faker.company_email()


def generate_booking_price(x):
    level = PriceLevels.objects.get(start_date__lte=x.created, end_date__gte=x.created,
                                    conference=x.conference_day.conference)
    if x.person.student_card_number:
        price = level.price * (1 - level.student_discount/100)
    else:
        price = level.price
    return price


def generate_company_booking_price(x):
    level = PriceLevels.objects.get(start_date__lte=x.created, end_date__gte=x.created,
                                    conference=x.conference_day.conference)
    students_price = level.price * (1 - level.student_discount/100)
    return x.students_count*students_price + x.non_students_count*level.price


class ConferenceStartDateGenerator(object):
    def __init__(self, start_date):
        self.generated_dates = defaultdict(set)
        self.start_date = start_date
        self.current_month = -1
        self.conferences_in_month = 0

    def _generate(self):
        start = self.start_date + relativedelta(months=self.current_month)
        end = start + relativedelta(months=self.current_month + 1) - relativedelta(days=3)

        date = None
        is_unique = False

        while not is_unique:
            date = FuzzyDate(datetime(start.year, start.month, 1),
                             datetime(end.year, end.month, end.day)).fuzz()
            is_unique = date not in self.generated_dates[self.current_month]

        self.generated_dates[self.current_month].update(
            i for i in daterange(date - timedelta(days=3), date + timedelta(days=3))
        )

        return date

    def __call__(self, x):
        if not self.conferences_in_month:
            self.current_month += 1
            self.conferences_in_month = random.choice(range(1, 4))
        result = self._generate()
        self.conferences_in_month -= 1
        return result


class CompanyAttendersFactory(factory.DjangoModelFactory):
    first_name = factory.LazyAttribute(lambda x: faker.first_name())
    last_name = factory.LazyAttribute(lambda x: faker.last_name())
    email = factory.LazyAttribute(UniqueEmailGenerator())
    password = factory.LazyAttribute(lambda x: hashlib.sha256(faker.text()).hexdigest())

    class Meta:
        model = CompanyAttenders


class PeopleFactory(factory.DjangoModelFactory):
    first_name = factory.LazyAttribute(lambda x: faker.first_name())
    last_name = factory.LazyAttribute(lambda x: faker.last_name())
    phone = factory.LazyAttribute(lambda x: faker.phone_number())
    email = factory.LazyAttribute(UniqueEmailGenerator())
    password = factory.LazyAttribute(lambda x: hashlib.sha256(faker.text()).hexdigest())
    pesel = factory.LazyAttribute(PeselGenerator())
    country = 'PL'
    city = u'Kraków'

    class Meta:
        model = People


class CompaniesFactory(factory.DjangoModelFactory):
    name = factory.LazyAttribute(lambda x: faker.company())
    email = factory.LazyAttribute(UniqueCompanyEmailGenerator())
    phone = factory.LazyAttribute(lambda x: faker.phone_number())
    password = factory.LazyAttribute(lambda x: hashlib.sha256(faker.text()).hexdigest())
    city = u'Kraków'
    country = 'PL'

    class Meta:
        model = Companies


class CompaniesBookingsFactory(factory.DjangoModelFactory):
    total = factory.LazyAttribute(generate_company_booking_price)
    students_count = FuzzyInteger(1, 5)
    non_students_count = FuzzyInteger(4, 10)
    is_canceled = False

    class Meta:
        model = CompaniesBookings

    @factory.post_generation
    def payments(self, create, extracted, **kwargs):
        if not create:
            return

        if self.is_canceled:
            return

        count = random.choice((1, 2, 4))
        for x in range(count):
            CompanyBookingPayins.objects.create(
                booking=self,
                amount=self.total / count,
                datetime=self.created + timedelta(days=x+random.choice((0, 1)))
            )

    @factory.post_generation
    def workshop_bookings(self, create, extracted, **kwargs):
        if not create:
            pass

        workshops = self.conference_day.workshops_set.all()
        workshops = random.sample(workshops, random.choice(range(len(workshops))))
        for workshop in workshops:
            try:
                CompaniesWorkshopBookings.objects.create(
                    booking=self,
                    workshop=workshop,
                    created=self.created,
                    attenders_count=random.choice(range(1, self.students_count + self.non_students_count))
                )
            except Exception as e:
                print 'CompaniesWorkshopBookings error!'


class PeopleBookingsFactory(factory.DjangoModelFactory):
    price = factory.LazyAttribute(generate_booking_price)
    due_date = factory.LazyAttribute(lambda x: x.created + timedelta(days=7))
    is_canceled = False

    class Meta:
        model = PeopleBookings

    @factory.post_generation
    def payments(self, create, extracted, **kwargs):
        if not create:
            return

        if self.is_canceled:
            return

        count = random.choice((1, 2, 4))
        for x in range(count):
            PeopleBookingPayins.objects.create(
                booking=self,
                amount=self.price / count,
                datetime=self.created + timedelta(days=x+random.choice((0, 1)))
            )

    @factory.post_generation
    def workshop_bookings(self, create, extracted, **kwargs):
        if not create:
            return

        workshops = self.conference_day.workshops_set.all()
        workshops = random.sample(workshops, random.choice(range(1, len(workshops)+1)))
        for workshop in workshops:
            try:
                WorkshopPeople.objects.create(
                    person=self.person,
                    booking=self,
                    workshop=workshop
                )
            except Exception as e:
                print 'PeopleWorkshops error!'


class WorkshopsFactory(factory.DjangoModelFactory):
    participants_limit = factory.LazyAttribute(lambda x: random.choice(range(15, 51, 5) + [None]))
    price = FuzzyInteger(0, 60, step=5)

    class Meta:
        model = Workshops


class ConferenceDaysFactory(factory.DjangoModelFactory):
    is_canceled = False

    class Meta:
        model = ConferenceDays

    @factory.post_generation
    def workshops(self, create, extracted, **kwargs):
        if not create:
            return

        count = random.choice((3, 4, 5))
        for _ in range(count):
            start = datetime(100, 1, 1, hour=random.choice(range(7, 19)))
            WorkshopsFactory.create(
                conference_day=self,
                start=start.time(),
                end=(start + timedelta(hours=random.choice((2, 3)))).time(),
            )


class ConferencesFactory(factory.DjangoModelFactory):
    name = factory.LazyAttributeSequence(lambda x, n: '{name} #{n}'.format(name=random.choice(CONFERENCE_NAMES).encode('utf-8'), n=n))
    start_date = factory.LazyAttribute(ConferenceStartDateGenerator(datetime(2009, 10, 1)))
    end_date = factory.LazyAttribute(lambda x: x.start_date + timedelta(days=random.choice((0, 1, 2))))

    class Meta:
        model = Conferences

    @factory.post_generation
    def days(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        participants_limit = random.choice(range(180, 221, 10))

        for date in daterange(self.start_date, self.end_date):
            ConferenceDaysFactory.create(
                day=date,
                participants_limit=participants_limit,
                conference=self,
            )

    @factory.post_generation
    def prices(self, create, extracted, **kwargs):
        if not create:
            return

        start_date = self.start_date - relativedelta(weeks=random.choice(range(8, 21, 4)))
        price = random.choice(range(50, 151, 10))
        step = random.choice(range(5, 36, 5))
        student_discount = random.choice(range(5, 31, 5))

        while start_date != self.start_date:
            end_date = start_date + relativedelta(weeks=1)
            PriceLevels.objects.create(
                conference=self,
                start_date=start_date,
                end_date=end_date-relativedelta(days=1),
                price=price,
                student_discount=student_discount
            )
            price += step
            start_date = end_date
