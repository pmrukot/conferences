import random


class PeselGen:

    GENDER_MALE = 0
    GENDER_FEMALE = 1

    def __init__(self, gender=0):
        self.user_data = {}
        self.gender = gender

    """generates random dob"""
    def _randomize_data(self):
        self.user_data = {
            'dob_day': random.choice(range(1, 29)),
            'dob_month': random.choice(range(1, 12)),
            'dob_year': random.choice(range(40, 99)),
        }
        self.user_data = {key: str(value).zfill(2) for
                          (key, value) in self.user_data.iteritems()}
        self.user_data['gender_sum'] = str(self._randomize_gender_checksum()).\
            zfill(4)

    """generates random checksum that represents gender"""
    def _randomize_gender_checksum(self):
        # odd - male / even - female
        number = random.randint(100, 350)

        if number % 2 == 0 and self.gender == 0:
            number += 1
        elif number % 2 == 1 and self.gender == 1:
            number += 1

        return number

    """returns generated user data"""
    def return_pesel(self):
        self._randomize_data()
        final_pesel = self.user_data['dob_year'] + \
            self.user_data['dob_month'] + self.user_data['dob_day'] + \
            self.user_data['gender_sum']

        return self._peselize_string(final_pesel)

    """counts pesel checksum"""
    def _peselize_string(self, pesel):
        weights = (1, 3, 7, 9, 1, 3, 7, 9, 1, 3)
        sum = 0
        for key, digit in enumerate(pesel):
            sum += int(digit) * weights[key]
        mod = (10 - sum % 10) % 10

        return str(pesel) + str(mod)
