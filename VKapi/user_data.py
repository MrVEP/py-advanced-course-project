import vk_api
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from credentials import group_token

vk_session = vk_api.VkApi(token=group_token)
vk = vk_session.get_api()


class VKUser:

    def __init__(self, user_id: int):
        self.id = user_id
        self.first_name = None
        self.last_name = None
        self.age = None
        self.sex = None
        self.city = None
        self.city_id = None
        self.age_range = [None, None]

    def pull_from_vk_page(self):
        response = vk.users.get(user_ids=self.id, fields='bdate,sex,city')
        user_info = response[0]
        self.first_name = user_info['first_name']
        self.last_name = user_info['last_name']
        if 'bdate' in user_info.keys() and len(user_info['bdate'].split('.')) == 3:
            self.define_age(user_info['bdate'].split('.'))
            self.age_range = [self.age, self.age]
        if 'sex' in user_info.keys():
            self.sex = user_info['sex']
        if 'city' in user_info.keys():
            self.city = user_info['city']['title']
            self.city_id = user_info['city']['id']

    def define_age(self, bdate: list):
        birthday = date(int(bdate[2]), int(bdate[1]), int(bdate[0]))
        current_date = datetime.date(datetime.today())
        age = relativedelta(current_date, birthday).years
        self.age = age
