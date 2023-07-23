import datetime
from random import randrange
from typing import Any, Dict, List, Optional, Tuple

import requests
import vk_api
from vk_api.longpoll import VkEventType, VkLongPoll

from database import insert_data_seen_users, insert_data_users, select
from settings import (COUNTRY_ID, ERROR_MESSAGE, GROUP_TOKEN, MAX_CITY_RESULTS,
                      MAX_PHOTOS, MAX_PHOTOS_COUNT, MAX_SEARCH_COUNT,
                      URL_USERS_GET, USER_TOKEN, VK_API_VERSION)
 
vk_token = "vk1.a.M6-dUrKpYL1cg11BOYqA-FFkgBe4c8XUC4qf34yyygfJrxapsVPHsfTwvFWZ_RIIbdDi1pLmoC1aFvbTuoIMN0M_lON-xXoLBK0OJMul8cf7ThX76q-bdEoHuHZSK5wOjX30u5hLHqxyO2kx9sTC6d9aZUSh8Y6NTsPsp5cdzY4sQAZNKAws-LIhbIJQejU9uP192w2ea2dY6OpDAKP3Ag"
 
vk = vk_api.VkApi(token=vk_token)
longpoll = VkLongPoll(vk)
 
class Vkinder:
    def __init__(self, token):
        self.vk = vk_api.VkApi(token=vk_token)
        self.vk_api = self.vk.get_api()
 
    def search_users(self, city, age, sex):
        user = self.vk_api.users.get(fields='city,age,sex')[0]
        if not user.get('city') or not user.get('age') or not user.get('sex'):
            return []
        fields = 'photo_max_orig,sex,bdate'
        if 'bdate' not in user:
            fields += ',bdate'
        users = self.vk_api.users.search(
            q='',
            city=city,
            fields=fields,
            count=1
        )
        if not users['items'] or 'age' not in users['items'][0]:
            return []
        users = self.vk_api.users.search(
            q='',
            city=city,
            fields='photo_max_orig',
            age_from=users['items'][0]['age'] - 5,
            age_to=users['items'][0]['age'] + 5,
            sex=sex,
            count=1000
        )
        response = requests.get(url, params=params).json()
        try:
            items = response['response']['items']
            for person in items:
                if not person.get('is_closed'):
                    first_name = person.get('first_name')
                    last_name = person.get('last_name')
                    vk_id = str(person.get('id'))
                    vk_link = f'vk.com/id{vk_id}'
                    insert_data_users(first_name, last_name, vk_id, vk_link)
            return 'Search completed'
        except KeyError:
            self.write_msg(user_id, ERROR_MESSAGE)
 
    def get_user_photos(self, user_id):
        photos = self.vk_api.photos.get(
            owner_id=user_id,
            album_id='profile',
            extended=1,
            count=3
        )
       repl = requests.get(url, params=params)
        photos = []
        response = repl.json()
        try:
            items = response['response']['items']
            for item in items:
                likes = item['likes'].get('count', 0)
                photo_id = item['id']
                photos.append((likes, photo_id))
            photos.sort(reverse=True)
            return photos
        except KeyError:
            self.write_msg(user_id, ERROR_MESSAGE)
 
    def get_user_info(self, user_id):
        try:
            user_info = self.vk_api.users.get(
                user_ids=user_id,
                fields='photo_max_orig,city,sex,bdate',
                count=1
            )
            user_info = user_info[0]
            return user_info
        except IndexError:
            return None
 
def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7), 'attachment': ''})
 
def handle_message(event):
    user_id = event.user_id
    message = event.text.lower()
    if message == 'поиск':
        vkinder = Vkinder(vk_token)
        user_info = vkinder.get_user_info(user['id'])
        if user_info:
           db_user_id = db.get_db_id(user_id)
        city = db.get_city(user_id)
        sex = db.get_sex(user_id)
        age_from = db.get_age_from(user_id)
        age_to = db.get_age_to(user_id)
        offset = db.get_offset(user_id)
        response = requests.get(
            'https://api.vk.com/method/users.search',
            self.get_params({'count': 1,
                             'offset': offset,
                             'city': city,
                             'country': 1,
                             'sex': sex,
                             'age_from': age_from,
                             'age_to': age_to,
                             'fields': 'is_closed',
                             'status': 6,
                             'has_photo': 1}
                            )
            )
            if users:
                for user in users:
                    photos = vkinder.get_user_photos(user['id'])
                    user_info = vkinder.get_user_info(user['id'])
                    if user_info:
                        message = f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}\n"
                        message += f"Дата рождения: {user_info.get('bdate', '')}\n"
                        message += f"Город: {user_info.get('city', {}).get('title', '')}\n"
                        for photo_link in photos:
                            message += f"Фото: [{photo_link}]({photo_link})\n"
                        message += f"Ссылка на профиль: https://vk.com/id{user['id']}"
                        write_msg(user_id, message)
                        save_search_results(create_connection(), user_id, user['id'], user_info.get('first_name', ''), user_info.get('last_name', ''), user_info.get('bdate', ''), user_info.get('city', {}).get('title', ''))
            else:
                write_msg(user_id, "По вашему запросу никого не найдено")
        else:
            write_msg(user_id, "Для использования данной команды вам необходимо заполнить свой профиль")
    else:
        write_msg(user_id, "Я вас не понимаю. Введите корректную команду")
 
def handle_error(event):
    print(event)
 
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        try:
            handle_message(event)
        except Exception as e:
            handle_error(e)
